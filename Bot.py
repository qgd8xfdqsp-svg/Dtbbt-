import logging
import sqlite3
import asyncio
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = "8795895107:AAF1gHb_Qe6ampB-UF9iEpBZKhU6TGi8PRY"
ADMIN_ID = 7678755832
WEB_APP_URL = "https://ваш_логин.github.io/playerok-market/"

# Класс для работы с базой данных
class Database:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Таблица пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      last_name TEXT,
                      balance INTEGER DEFAULT 1000,
                      rating REAL DEFAULT 5.0,
                      deals_count INTEGER DEFAULT 0,
                      joined_date TEXT,
                      last_active TEXT,
                      is_banned INTEGER DEFAULT 0,
                      is_admin INTEGER DEFAULT 0)''')
        
        # Таблица сделок
        c.execute('''CREATE TABLE IF NOT EXISTS deals
                     (deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      deal_type TEXT,
                      item_name TEXT,
                      item_category TEXT,
                      quantity INTEGER,
                      price_per_item INTEGER,
                      total_price INTEGER,
                      status TEXT DEFAULT 'active',
                      created_date TEXT,
                      completed_date TEXT,
                      buyer_id INTEGER,
                      seller_id INTEGER,
                      deal_hash TEXT UNIQUE,
                      FOREIGN KEY (user_id) REFERENCES users (user_id))''')
        
        # Таблица инвентаря
        c.execute('''CREATE TABLE IF NOT EXISTS inventory
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      item_name TEXT,
                      item_category TEXT,
                      quantity INTEGER,
                      purchase_price INTEGER,
                      selling_price INTEGER,
                      added_date TEXT,
                      is_selling INTEGER DEFAULT 0,
                      FOREIGN KEY (user_id) REFERENCES users (user_id))''')
        
        # Таблица транзакций
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      amount INTEGER,
                      transaction_type TEXT,
                      description TEXT,
                      created_date TEXT,
                      deal_id INTEGER,
                      FOREIGN KEY (user_id) REFERENCES users (user_id))''')
        
        # Таблица категорий товаров
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      category_name TEXT UNIQUE,
                      category_icon TEXT,
                      is_active INTEGER DEFAULT 1)''')
        
        # Таблица отзывов
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
                     (review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      from_user_id INTEGER,
                      to_user_id INTEGER,
                      deal_id INTEGER,
                      rating INTEGER,
                      comment TEXT,
                      created_date TEXT,
                      FOREIGN KEY (from_user_id) REFERENCES users (user_id),
                      FOREIGN KEY (to_user_id) REFERENCES users (user_id))''')
        
        conn.commit()
        
        # Добавляем категории если их нет
        categories = [
            ('Игры', '🎮'),
            ('Подписки', '📺'),
            ('Софт', '💻'),
            ('Донат', '💎'),
            ('Аккаунты', '👤'),
            ('Другое', '📦')
        ]
        
        for cat_name, cat_icon in categories:
            c.execute("INSERT OR IGNORE INTO categories (category_name, category_icon) VALUES (?, ?)",
                     (cat_name, cat_icon))
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name, last_name=None):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT OR IGNORE INTO users 
                     (user_id, username, first_name, last_name, joined_date, last_active) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, username, first_name, last_name, now, now))
        
        # Если пользователь админ
        if user_id == ADMIN_ID:
            c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    
    def update_last_active(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        conn.close()
    
    def get_balance(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def update_balance(self, user_id, amount, description=""):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        c.execute('''INSERT INTO transactions (user_id, amount, transaction_type, description, created_date)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, amount, 'credit' if amount > 0 else 'debit', 
                   description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    
    def add_deal(self, user_id, deal_type, item_name, category, quantity, price_per_item):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = quantity * price_per_item
        deal_hash = f"{user_id}_{now}_{item_name}".replace(" ", "_")
        
        c.execute('''INSERT INTO deals 
                     (user_id, deal_type, item_name, item_category, quantity, 
                      price_per_item, total_price, created_date, deal_hash)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, deal_type, item_name, category, quantity, 
                   price_per_item, total_price, now, deal_hash))
        
        deal_id = c.lastrowid
        
        c.execute("UPDATE users SET deals_count = deals_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return deal_id
    
    def get_user_deals(self, user_id, limit=10):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT * FROM deals 
                     WHERE user_id = ? OR buyer_id = ? OR seller_id = ?
                     ORDER BY created_date DESC LIMIT ?''',
                  (user_id, user_id, user_id, limit))
        deals = c.fetchall()
        conn.close()
        return deals
    
    def get_active_deals(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT * FROM deals 
                     WHERE (user_id = ? OR buyer_id = ? OR seller_id = ?) 
                     AND status = 'active'
                     ORDER BY created_date DESC''',
                  (user_id, user_id, user_id))
        deals = c.fetchall()
        conn.close()
        return deals
    
    def complete_deal(self, deal_id):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''UPDATE deals SET status = 'completed', completed_date = ? 
                     WHERE deal_id = ?''', (now, deal_id))
        conn.commit()
        conn.close()
    
    def cancel_deal(self, deal_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE deals SET status = 'cancelled' WHERE deal_id = ?", (deal_id,))
        conn.commit()
        conn.close()
    
    def add_to_inventory(self, user_id, item_name, category, quantity, purchase_price, selling_price):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Проверяем есть ли уже такой предмет
        c.execute('''SELECT id, quantity FROM inventory 
                     WHERE user_id = ? AND item_name = ? AND is_selling = 0''',
                  (user_id, item_name))
        existing = c.fetchone()
        
        if existing:
            # Обновляем количество
            c.execute('''UPDATE inventory SET quantity = quantity + ? 
                         WHERE id = ?''', (quantity, existing[0]))
        else:
            # Добавляем новый
            c.execute('''INSERT INTO inventory 
                         (user_id, item_name, item_category, quantity, 
                          purchase_price, selling_price, added_date)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, item_name, category, quantity, 
                       purchase_price, selling_price, now))
        
        conn.commit()
        conn.close()
    
    def get_inventory(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT * FROM inventory 
                     WHERE user_id = ? AND quantity > 0
                     ORDER BY added_date DESC''', (user_id,))
        inventory = c.fetchall()
        conn.close()
        return inventory
    
    def remove_from_inventory(self, inventory_id, quantity):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory WHERE id = ?", (inventory_id,))
        current = c.fetchone()
        
        if current and current[0] >= quantity:
            if current[0] == quantity:
                c.execute("DELETE FROM inventory WHERE id = ?", (inventory_id,))
            else:
                c.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?",
                         (quantity, inventory_id))
            conn.commit()
            success = True
        else:
            success = False
        
        conn.close()
        return success
    
    def get_categories(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE is_active = 1")
        categories = c.fetchall()
        conn.close()
        return categories
    
    def add_review(self, from_user_id, to_user_id, deal_id, rating, comment):
        conn = self.get_connection()
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO reviews 
                     (from_user_id, to_user_id, deal_id, rating, comment, created_date)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (from_user_id, to_user_id, deal_id, rating, comment, now))
        
        # Обновляем рейтинг пользователя
        c.execute('''UPDATE users SET rating = (
                     SELECT AVG(rating) FROM reviews WHERE to_user_id = ?
                     ) WHERE user_id = ?''', (to_user_id, to_user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_rating(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT AVG(rating) FROM reviews WHERE to_user_id = ?", (user_id,))
        rating = c.fetchone()[0]
        conn.close()
        return rating if rating else 5.0
    
    def get_user_stats(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Количество сделок
        c.execute("SELECT COUNT(*) FROM deals WHERE user_id = ?", (user_id,))
        total_deals = c.fetchone()[0]
        
        # Активные сделки
        c.execute("SELECT COUNT(*) FROM deals WHERE user_id = ? AND status = 'active'", (user_id,))
        active_deals = c.fetchone()[0]
        
        # Завершенные сделки
        c.execute("SELECT COUNT(*) FROM deals WHERE user_id = ? AND status = 'completed'", (user_id,))
        completed_deals = c.fetchone()[0]
        
        # Сумма всех сделок
        c.execute("SELECT SUM(total_price) FROM deals WHERE user_id = ?", (user_id,))
        total_volume = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_deals': total_deals,
            'active_deals': active_deals,
            'completed_deals': completed_deals,
            'total_volume': total_volume
        }
    
    def get_all_users(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, username, first_name, balance, deals_count, joined_date FROM users")
        users = c.fetchall()
        conn.close()
        return users
    
    def get_all_deals(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM deals ORDER BY created_date DESC")
        deals = c.fetchall()
        conn.close()
        return deals
    
    def ban_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def unban_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def is_banned(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] == 1 if result else False
    
    def is_admin(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] == 1 if result else (user_id == ADMIN_ID)

# Инициализация базы данных
db = Database()

# Класс для работы с WebApp данными
class WebAppHandler:
    @staticmethod
    async def process_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = update.effective_message.web_app_data
        if not data:
            return
        
        try:
            webapp_data = json.loads(data.data)
            user_id = update.effective_user.id
            
            logger.info(f"WebApp data from user {user_id}: {webapp_data}")
            
            # Проверяем не забанен ли пользователь
            if db.is_banned(user_id):
                await update.effective_message.reply_text("❌ Вы заблокированы в боте")
                return
            
            action = webapp_data.get('action')
            
            if action == 'purchase':
                await WebAppHandler.handle_purchase(update, context, webapp_data, user_id)
            elif action == 'sell_deal':
                await WebAppHandler.handle_sell_deal(update, context, webapp_data, user_id)
            elif action == 'buy_deal':
                await WebAppHandler.handle_buy_deal(update, context, webapp_data, user_id)
            elif action == 'create_deal':
                await WebAppHandler.handle_create_deal(update, context, webapp_data, user_id)
            elif action == 'get_balance':
                await WebAppHandler.handle_get_balance(update, context, user_id)
            elif action == 'get_inventory':
                await WebAppHandler.handle_get_inventory(update, context, user_id)
            elif action == 'get_deals':
                await WebAppHandler.handle_get_deals(update, context, user_id)
            else:
                await update.effective_message.reply_text("❌ Неизвестное действие")
            
        except json.JSONDecodeError:
            await update.effective_message.reply_text("❌ Ошибка обработки данных")
    
    @staticmethod
    async def handle_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, user_id: int):
        item = data.get('item', 'Неизвестно')
        price = data.get('price', 0)
        
        balance = db.get_balance(user_id)
        
        if balance >= price:
            db.update_balance(user_id, -price, f"Покупка: {item}")
            db.add_deal(user_id, 'buy', item, 'games', 1, price)
            
            await update.effective_message.reply_text(
                f"✅ Покупка совершена!\n"
                f"Товар: {item}\n"
                f"Цена: {price} ₽\n"
                f"Остаток: {balance - price} ₽"
            )
            
            # Уведомление админу
            if db.is_admin(ADMIN_ID):
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"🛒 Покупка\n"
                         f"Пользователь: {user_id}\n"
                         f"Товар: {item}\n"
                         f"Цена: {price} ₽"
                )
        else:
            await update.effective_message.reply_text(
                f"❌ Недостаточно средств\n"
                f"Баланс: {balance} ₽\n"
                f"Нужно: {price} ₽"
            )
    
    @staticmethod
    async def handle_sell_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, user_id: int):
        item = data.get('item', 'Неизвестно')
        quantity = data.get('quantity', 1)
        price = data.get('price', 0)
        total_price = data.get('totalPrice', price * quantity)
        
        deal_id = db.add_deal(user_id, 'sell', item, 'games', quantity, price)
        
        await update.effective_message.reply_text(
            f"✅ Сделка на продажу создана!\n"
            f"ID: #{deal_id}\n"
            f"Товар: {item}\n"
            f"Количество: {quantity}\n"
            f"Цена: {price} ₽/шт\n"
            f"Всего: {total_price} ₽"
        )
    
    @staticmethod
    async def handle_buy_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, user_id: int):
        item = data.get('item', 'Неизвестно')
        amount = data.get('amount', 0)
        
        balance = db.get_balance(user_id)
        
        if balance >= amount:
            db.update_balance(user_id, -amount, f"Покупка по сделке: {item}")
            deal_id = db.add_deal(user_id, 'buy', item, 'games', 1, amount)
            
            await update.effective_message.reply_text(
                f"✅ Сделка на покупку создана!\n"
                f"ID: #{deal_id}\n"
                f"Товар: {item}\n"
                f"Сумма: {amount} ₽\n"
                f"Остаток: {balance - amount} ₽"
            )
        else:
            await update.effective_message.reply_text(
                f"❌ Недостаточно средств\n"
                f"Баланс: {balance} ₽\n"
                f"Нужно: {amount} ₽"
            )
    
    @staticmethod
    async def handle_create_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, user_id: int):
        deal_type = data.get('type', 'buy')
        item = data.get('item', 'Неизвестно')
        quantity = data.get('quantity', 1)
        price = data.get('price', 0)
        total_price = data.get('totalPrice', price * quantity)
        
        if deal_type == 'buy':
            balance = db.get_balance(user_id)
            if balance < total_price:
                await update.effective_message.reply_text("❌ Недостаточно средств")
                return
            db.update_balance(user_id, -total_price, f"Сделка на покупку: {item}")
        
        deal_id = db.add_deal(user_id, deal_type, item, 'custom', quantity, price)
        
        await update.effective_message.reply_text(
            f"✅ Сделка создана!\n"
            f"ID: #{deal_id}\n"
            f"Тип: {'Покупка' if deal_type == 'buy' else 'Продажа'}\n"
            f"Товар: {item}\n"
            f"Количество: {quantity}\n"
            f"Сумма: {total_price} ₽"
        )
    
    @staticmethod
    async def handle_get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        balance = db.get_balance(user_id)
        await update.effective_message.reply_text(f"💰 Баланс: {balance} ₽")
    
    @staticmethod
    async def handle_get_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        inventory = db.get_inventory(user_id)
        
        if inventory:
            text = "📦 Ваш инвентарь:\n\n"
            for item in inventory:
                text += f"• {item[2]} x{item[4]} - {item[6]} ₽\n"
        else:
            text = "📦 Инвентарь пуст"
        
        await update.effective_message.reply_text(text)
    
    @staticmethod
    async def handle_get_deals(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        deals = db.get_user_deals(user_id, 5)
        
        if deals:
            text = "📊 Последние сделки:\n\n"
            for deal in deals:
                status_emoji = {
                    'active': '🟢',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(deal[8], '⚪')
                
                text += f"{status_emoji} #{deal[0]}: {deal[3]} - {deal[7]} ₽\n"
        else:
            text = "📊 У вас пока нет сделок"
        
        await update.effective_message.reply_text(text)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Добавляем пользователя в базу
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    db.update_last_active(user.id)
    
    # Проверяем не забанен ли пользователь
    if db.is_banned(user.id):
        await update.message.reply_text("❌ Вы заблокированы в боте")
        return
    
    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton("🎮 Открыть маркет", web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton("💰 Баланс", callback_data="balance"),
            InlineKeyboardButton("📦 Инвентарь", callback_data="inventory")
        ],
        [
            InlineKeyboardButton("📊 Мои сделки", callback_data="deals"),
            InlineKeyboardButton("⭐ Мой рейтинг", callback_data="rating")
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
            InlineKeyboardButton("📞 Поддержка", callback_data="support")
        ]
    ]
    
    # Добавляем админ-кнопки
    if db.is_admin(user.id):
        keyboard.append([InlineKeyboardButton("👑 Админ панель", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    balance = db.get_balance(user.id)
    rating = db.get_user_rating(user.id)
    stats = db.get_user_stats(user.id)
    
    welcome_text = (
        f"🎮 Добро пожаловать в PlayerOK Market, {user.first_name}!\n\n"
        f"💰 Баланс: {balance} ₽\n"
        f"⭐ Рейтинг: {rating:.1f}\n"
        f"📊 Сделок: {stats['total_deals']}\n\n"
        f"Здесь вы можете:\n"
        f"✅ Покупать цифровые товары\n"
        f"✅ Продавать свои предметы\n"
        f"✅ Создавать безопасные сделки\n\n"
        f"Нажмите кнопку ниже, чтобы открыть маркет!"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db.update_last_active(user_id)
    
    if db.is_banned(user_id):
        await query.edit_message_text("❌ Вы заблокированы в боте")
        return
    
    if query.data == "balance":
        balance = db.get_balance(user_id)
        await query.edit_message_text(f"💰 Ваш баланс: {balance} ₽")
        
    elif query.data == "inventory":
        inventory = db.get_inventory(user_id)
        
        if inventory:
            text = "📦 Ваш инвентарь:\n\n"
            for item in inventory:
                text += f"• {item[2]} x{item[4]} - {item[6]} ₽\n"
        else:
            text = "📦 Ваш инвентарь пуст\n\nКупите что-нибудь в маркете!"
        
        keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data="inventory")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif query.data == "deals":
        deals = db.get_active_deals(user_id)
        
        if deals:
            text = "📊 Активные сделки:\n\n"
            for deal in deals:
                text += f"• #{deal[0]}: {deal[3]} - {deal[7]} ₽\n"
        else:
            text = "📊 Нет активных сделок"
        
        keyboard = [[InlineKeyboardButton("📋 Все сделки", callback_data="all_deals")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif query.data == "all_deals":
        deals = db.get_user_deals(user_id, 10)
        
        if deals:
            text = "📋 Все сделки:\n\n"
            for deal in deals:
                status_emoji = {
                    'active': '🟢',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(deal[8], '⚪')
                
                text += f"{status_emoji} #{deal[0]}: {deal[3]} - {deal[7]} ₽\n"
        else:
            text = "📋 У вас пока нет сделок"
        
        await query.edit_message_text(text)
        
    elif query.data == "rating":
        rating = db.get_user_rating(user_id)
        stats = db.get_user_stats(user_id)
        
        text = (
            f"⭐ Ваш рейтинг: {rating:.1f}\n\n"
            f"📊 Статистика:\n"
            f"• Всего сделок: {stats['total_deals']}\n"
            f"• Активных: {stats['active_deals']}\n"
            f"• Завершенных: {stats['completed_deals']}\n"
            f"• Объем торгов: {stats['total_volume']} ₽"
        )
        
        await query.edit_message_text(text)
        
    elif query.data == "help":
        help_text = (
            "ℹ️ Помощь по использованию:\n\n"
            "1. Нажмите 🎮 Открыть маркет\n"
            "2. Выберите товар для покупки\n"
            "3. Или продайте свой товар\n"
            "4. Создавайте безопасные сделки\n\n"
            "Команды:\n"
            "/start - Главное меню\n"
            "/balance - Проверить баланс\n"
            "/deals - Мои сделки\n"
            "/inventory - Инвентарь\n"
            "/help - Помощь\n\n"
            "По вопросам: @admin"
        )
        await query.edit_message_text(help_text)
        
    elif query.data == "support":
        await query.edit_message_text(
            "📞 Поддержка\n\n"
            "По всем вопросам обращайтесь к администратору:\n"
            "@admin\n\n"
            "Или напишите в чат поддержки: @support_chat"
        )
        
    elif query.data == "admin" and db.is_admin(user_id):
        await show_admin_panel(query)
    
    elif query.data.startswith("admin_"):
        if db.is_admin(user_id):
            await handle_admin_actions(query, context)

async def show_admin_panel(query):
    text = (
        "👑 Админ панель\n\n"
        "Выберите действие:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📋 Все сделки", callback_data="admin_deals")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔨 Бан", callback_data="admin_ban")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_admin_actions(query, context):
    action = query.data.replace("admin_", "")
    
    if action == "stats":
        users = db.get_all_users()
        deals = db.get_all_deals()
        
        total_users = len(users)
        active_deals = sum(1 for d in deals if d[8] == 'active')
        completed_deals = sum(1 for d in deals if d[8] == 'completed')
        total_volume = sum(d[7] for d in deals if d[7] is not None)
        
        text = (
            f"📊 Общая статистика:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"📈 Активных сделок: {active_deals}\n"
            f"✅ Завершенных сделок: {completed_deals}\n"
            f"💰 Общий объем: {total_volume} ₽\n\n"
            f"Последние пользователи:\n"
        )
        
        for user in users[:5]:
            text += f"• {user[2]} (@{user[1]}) - {user[3]} ₽\n"
        
        await query.edit_message_text(text)
    
    elif action == "users":
        users = db.get_all_users()
        
        text = "👥 Список пользователей:\n\n"
        for user in users[:10]:
            text += f"• ID: {user[0]} | {user[2]} (@{user[1]})\n"
            text += f"  Баланс: {user[3]} ₽ | Сделок: {user[4]}\n"
            text += f"  Зарегистрирован: {user[5]}\n\n"
        
        await query.edit_message_text(text)
    
    elif action == "deals":
        deals = db.get_all_deals()
        
        text = "📋 Все сделки:\n\n"
        for deal in deals[:10]:
            status_emoji = {
                'active': '🟢',
                'completed': '✅',
                'cancelled': '❌'
            }.get(deal[8], '⚪')
            
            text += f"{status_emoji} #{deal[0]}: {deal[3]} - {deal[7]} ₽\n"
            text += f"  Пользователь: {deal[1]} | {deal[2]}\n"
            text += f"  Дата: {deal[9]}\n\n"
        
        await query.edit_message_text(text)
    
    elif action == "broadcast":
        context.user_data['broadcast_mode'] = True
        await query.edit_message_text(
            "📢 Режим рассылки\n\n"
            "Отправьте сообщение для рассылки всем пользователям:"
        )
    
    elif action == "ban":
        context.user_data['ban_mode'] = True
        await query.edit_message_text(
            "🔨 Режим бана\n\n"
            "Отправьте ID пользователя для блокировки:"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Рассылка
    if context.user_data.get('broadcast_mode') and db.is_admin(user_id):
        users = db.get_all_users()
        sent = 0
        
        await update.message.reply_text("📢 Начинаю рассылку...")
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user[0],
                    text=f"📢 Рассылка:\n\n{text}"
                )
                sent += 1
                await asyncio.sleep(0.05)
            except:
                continue
        
        await update.message.reply_text(f"✅ Рассылка завершена!\nОтправлено: {sent} пользователям")
        context.user_data['broadcast_mode'] = False
    
    # Бан пользователя
    elif context.user_data.get('ban_mode') and db.is_admin(user_id):
        try:
            ban_id = int(text)
            db.ban_user(ban_id)
            await update.message.reply_text(f"✅ Пользователь {ban_id} заблокирован")
        except:
            await update.message.reply_text("❌ Неверный ID")
        
        context.user_data['ban_mode'] = False

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = db.get_balance(user_id)
    await update.message.reply_text(f"💰 Ваш баланс: {balance} ₽")

async def deals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    deals = db.get_user_deals(user_id)
    
    if deals:
        text = "📊 Ваши сделки:\n\n"
        for deal in deals[:10]:
            status_emoji = {
                'active': '🟢',
                'completed': '✅',
                'cancelled': '❌'
            }.get(deal[8], '⚪')
            
            text += f"{status_emoji} #{deal[0]}: {deal[3]} - {deal[7]} ₽\n"
    else:
        text = "📊 У вас пока нет сделок"
    
    await update.message.reply_text(text)

async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    inventory = db.get_inventory(user_id)
    
    if inventory:
        text = "📦 Ваш инвентарь:\n\n"
        for item in inventory:
            text += f"• {item[2]} x{item[4]} - {item[6]} ₽\n"
    else:
        text = "📦 Ваш инвентарь пуст"
    
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ Доступные команды:\n\n"
        "/start - Главное меню\n"
        "/balance - Проверить баланс\n"
        "/deals - Мои сделки\n"
        "/inventory - Инвентарь\n"
        "/help - Это сообщение\n\n"
        "Для покупки/продажи используйте мини-приложение 🎮 Открыть маркет"
    )
    await update.message.reply_text(help_text)

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("deals", deals_command))
    application.add_handler(CommandHandler("inventory", inventory_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчик callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Добавляем обработчик данных из WebApp
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, WebAppHandler.process_data))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    print(f"👑 Администратор: {ADMIN_ID}")
    print(f"🔗 WebApp URL: {WEB_APP_URL}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
