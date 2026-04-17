"""
База данных для игрового бота
"""
import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import config
import json

class Database:
    def __init__(self, db_path: str = config.DATABASE_URL):
        self.db_path = db_path
        self.lock = asyncio.Lock()
    
    async def init(self):
        """Инициализация таблиц базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance INTEGER DEFAULT ?,
                    total_games INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_loss INTEGER DEFAULT 0,
                    total_wagered INTEGER DEFAULT 0,
                    total_won INTEGER DEFAULT 0,
                    total_lost INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_daily TEXT,
                    referrer_id INTEGER,
                    is_banned INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    FOREIGN KEY (referrer_id) REFERENCES users(user_id)
                )
            """, (config.START_BALANCE,))
            
            # Транзакции
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    amount INTEGER,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # История игр
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_type TEXT,
                    bet INTEGER,
                    result INTEGER,
                    profit INTEGER,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Инвентарь
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_type TEXT,
                    item_id TEXT,
                    quantity INTEGER DEFAULT 1,
                    acquired_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Настройки
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Достижения
            await db.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement_id TEXT,
                    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await db.commit()
    
    # === ПОЛЬЗОВАТЕЛИ ===
    
    async def create_user(self, user_id: int, username: str, first_name: str, 
                         referrer_id: Optional[int] = None) -> bool:
        """Создание нового пользователя"""
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Проверяем существование
                cursor = await db.execute(
                    "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    return False
                
                await db.execute("""
                    INSERT INTO users (user_id, username, first_name, referrer_id)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, referrer_id))
                
                # Бонус рефереру
                if referrer_id:
                    await db.execute("""
                        UPDATE users SET balance = balance + ? WHERE user_id = ?
                    """, (config.REFERRAL_BONUS, referrer_id))
                    await self.log_transaction(referrer_id, "referral", config.REFERRAL_BONUS,
                                              f"Бонус за приглашение {user_id}")
                
                await db.commit()
                return True
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение данных пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_balance(self, user_id: int, amount: int, operation: str = "add"):
        """Обновление баланса"""
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                if operation == "add":
                    await db.execute(
                        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                        (amount, user_id)
                    )
                elif operation == "sub":
                    await db.execute(
                        "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                        (amount, user_id)
                    )
                await db.commit()
    
    async def get_balance(self, user_id: int) -> int:
        """Получение баланса"""
        user = await self.get_user(user_id)
        return user['balance'] if user else 0
    
    async def update_user_stats(self, user_id: int, won: bool, amount: int):
        """Обновление статистики пользователя"""
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users SET 
                        total_games = total_games + 1,
                        total_wins = total_wins + ?,
                        total_loss = total_loss + ?,
                        total_wagered = total_wagered + ?,
                        total_won = total_won + ?,
                        total_lost = total_lost + ?
                    WHERE user_id = ?
                """, (
                    1 if won else 0,
                    0 if won else 1,
                    abs(amount),
                    amount if won else 0,
                    abs(amount) if not won else 0,
                    user_id
                ))
                
                # Обновление опыта
                await db.execute("""
                    UPDATE users SET 
                        exp = exp + ?,
                        level = CASE 
                            WHEN exp + ? >= level * 100 THEN level + 1 
                            ELSE level 
                        END
                    WHERE user_id = ?
                """, (10, 10, user_id))
                
                await db.commit()
    
    # === ТРАНЗАКЦИИ ===
    
    async def log_transaction(self, user_id: int, tx_type: str, amount: int, description: str):
        """Логирование транзакции"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, tx_type, amount, description))
            await db.commit()
    
    async def get_transactions(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Получение истории транзакций"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM transactions WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # === ИГРЫ ===
    
    async def log_game(self, user_id: int, game_type: str, bet: int, 
                       result: int, profit: int, details: str = ""):
        """Логирование игры"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO game_history (user_id, game_type, bet, result, profit, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, game_type, bet, result, profit, details))
            await db.commit()
    
    async def get_game_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Получение истории игр"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM game_history WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_top_players(self, limit: int = 10) -> List[Dict]:
        """Получение топ игроков"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT user_id, username, first_name, balance, total_wins, total_games
                FROM users WHERE is_banned = 0
                ORDER BY balance DESC LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # === ЕЖЕДНЕВНЫЙ БОНУС ===
    
    async def claim_daily_bonus(self, user_id: int) -> bool:
        """Получение ежедневного бонуса"""
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT last_daily FROM users WHERE user_id = ?", (user_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return False
                
                last_claim = row['last_daily']
                now = datetime.now()
                
                if last_claim:
                    last_claim_time = datetime.fromisoformat(last_claim)
                    if (now - last_claim_time).total_seconds() < config.DAILY_BONUS_COOLDOWN:
                        return False
                
                await db.execute("""
                    UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?
                """, (config.DAILY_BONUS, now.isoformat(), user_id))
                await db.commit()
                return True
    
    # === ИНВЕНТАРЬ ===
    
    async def add_item(self, user_id: int, item_type: str, item_id: str, quantity: int = 1):
        """Добавление предмета в инвентарь"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, quantity FROM inventory 
                WHERE user_id = ? AND item_type = ? AND item_id = ?
            """, (user_id, item_type, item_id))
            row = await cursor.fetchone()
            
            if row:
                await db.execute("""
                    UPDATE inventory SET quantity = quantity + ? WHERE id = ?
                """, (quantity, row[0]))
            else:
                await db.execute("""
                    INSERT INTO inventory (user_id, item_type, item_id, quantity)
                    VALUES (?, ?, ?, ?)
                """, (user_id, item_type, item_id, quantity))
            
            await db.commit()
    
    async def get_inventory(self, user_id: int) -> List[Dict]:
        """Получение инвентаря"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM inventory WHERE user_id = ? ORDER BY acquired_at DESC
            """, (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # === ДОСТИЖЕНИЯ ===
    
    async def unlock_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Разблокировка достижения"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id FROM achievements WHERE user_id = ? AND achievement_id = ?
            """, (user_id, achievement_id))
            if await cursor.fetchone():
                return False
            
            await db.execute("""
                INSERT INTO achievements (user_id, achievement_id) VALUES (?, ?)
            """, (user_id, achievement_id))
            await db.commit()
            return True
    
    # === БАН ===
    
    async def ban_user(self, user_id: int, banned: bool = True):
        """Бан/разбан пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_banned = ? WHERE user_id = ?",
                (1 if banned else 0, user_id)
            )
            await db.commit()
    
    async def is_banned(self, user_id: int) -> bool:
        """Проверка бана"""
        user = await self.get_user(user_id)
        return user['is_banned'] == 1 if user else False


# Глобальный экземпляр
db = Database()
