<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PlayerOK Маркет</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        :root {
            --bg-dark: #0B0E12;
            --bg-card: #1A1E24;
            --bg-secondary: #242932;
            --border-color: #333A45;
            --accent-primary: #FF6B4A;
            --accent-secondary: #FF4A3D;
            --text-primary: #FFFFFF;
            --text-secondary: #8E9AAB;
            --blue-accent: #4A9EFF;
            --success: #00C853;
            --warning: #FFB300;
        }

        body {
            background-color: var(--bg-dark);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }

        .app-container {
            max-width: 400px;
            width: 100%;
            background-color: var(--bg-card);
            min-height: 100vh;
            position: relative;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }

        /* Header */
        .header {
            background: linear-gradient(145deg, #2A2F38, #1F232A);
            padding: 20px 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo-icon {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            width: 32px;
            height: 32px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            color: white;
        }

        .logo-text {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 18px;
        }

        .profile-badge {
            background-color: var(--bg-secondary);
            border-radius: 30px;
            padding: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.2s;
        }

        .profile-badge:active {
            transform: scale(0.98);
            background-color: var(--border-color);
        }

        .profile-avatar {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .profile-name {
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 500;
            padding-right: 8px;
        }

        /* Balance Card */
        .balance-card {
            background: linear-gradient(145deg, #2F3540, #242932);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
        }

        .balance-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .balance-label {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .balance-amount {
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 700;
        }

        .balance-currency {
            color: var(--accent-primary);
            font-size: 16px;
            margin-left: 4px;
        }

        /* Main Action Buttons */
        .action-buttons {
            display: flex;
            padding: 16px;
            gap: 8px;
            background-color: var(--bg-card);
        }

        .action-btn {
            flex: 1;
            padding: 16px 8px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .action-btn.sell {
            background-color: var(--bg-secondary);
            color: var(--accent-primary);
            border: 1px solid var(--border-color);
        }

        .action-btn.buy {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border: none;
            box-shadow: 0 4px 10px rgba(255, 107, 74, 0.3);
        }

        .action-btn.deal {
            background-color: var(--bg-secondary);
            color: var(--blue-accent);
            border: 1px solid var(--border-color);
        }

        .action-btn:active {
            transform: scale(0.96);
        }

        /* Content Sections */
        .content-section {
            padding: 20px 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .section-title {
            color: var(--text-primary);
            font-size: 18px;
            font-weight: 600;
        }

        .section-link {
            color: var(--accent-primary);
            font-size: 14px;
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 20px;
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            cursor: pointer;
        }

        .section-link:active {
            background-color: var(--border-color);
        }

        /* Products Grid */
        .products-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .product-card {
            background-color: var(--bg-secondary);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            transition: all 0.2s;
        }

        .product-card:active {
            transform: scale(0.98);
            border-color: var(--accent-primary);
        }

        .product-image {
            width: 100%;
            height: 120px;
            background: linear-gradient(145deg, #2F3540, #1F232A);
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
        }

        .product-title {
            color: var(--text-primary);
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .product-price {
            color: var(--accent-primary);
            font-weight: 700;
            font-size: 18px;
            margin-bottom: 12px;
        }

        .product-price span {
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 400;
            margin-left: 4px;
        }

        .buy-btn {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            transition: all 0.2s;
        }

        .buy-btn:active {
            opacity: 0.8;
            transform: scale(0.98);
        }

        /* Inventory List */
        .inventory-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .inventory-item {
            background-color: var(--bg-secondary);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .item-icon {
            width: 56px;
            height: 56px;
            background: linear-gradient(145deg, #2F3540, #1F232A);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }

        .item-info {
            flex: 1;
        }

        .item-name {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 6px;
        }

        .item-details {
            color: var(--text-secondary);
            font-size: 14px;
            display: flex;
            gap: 16px;
        }

        .item-quantity {
            color: var(--accent-primary);
            font-weight: 600;
        }

        .sell-small {
            background-color: var(--bg-secondary);
            color: var(--accent-primary);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .sell-small:active {
            background-color: var(--border-color);
            transform: scale(0.96);
        }

        /* Deals List */
        .deals-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .deal-card {
            background-color: var(--bg-secondary);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .deal-info h4 {
            color: var(--text-primary);
            font-size: 16px;
            margin-bottom: 8px;
        }

        .deal-meta {
            display: flex;
            gap: 20px;
            color: var(--text-secondary);
            font-size: 14px;
        }

        .deal-status {
            padding: 6px 12px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
        }

        .status-active {
            background-color: rgba(74, 158, 255, 0.15);
            color: var(--blue-accent);
            border: 1px solid rgba(74, 158, 255, 0.3);
        }

        .status-completed {
            background-color: rgba(0, 200, 83, 0.15);
            color: var(--success);
            border: 1px solid rgba(0, 200, 83, 0.3);
        }

        /* Bottom Navigation */
        .bottom-nav {
            position: sticky;
            bottom: 0;
            background-color: var(--bg-card);
            border-top: 1px solid var(--border-color);
            display: flex;
            padding: 8px 12px;
            gap: 4px;
        }

        .nav-item {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 10px 4px;
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 12px;
            cursor: pointer;
            border-radius: 12px;
            transition: all 0.2s;
        }

        .nav-item.active {
            color: var(--accent-primary);
            background-color: var(--bg-secondary);
        }

        .nav-item span {
            font-size: 22px;
        }

        .nav-item:active {
            background-color: var(--border-color);
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0,0,0,0.8);
            align-items: center;
            justify-content: center;
            padding: 20px;
            z-index: 1000;
            backdrop-filter: blur(5px);
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background-color: var(--bg-secondary);
            border-radius: 24px;
            padding: 24px;
            width: 100%;
            max-width: 360px;
            border: 1px solid var(--border-color);
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-title {
            color: var(--text-primary);
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 24px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 14px;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            color: var(--text-primary);
            font-size: 16px;
            transition: all 0.2s;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--accent-primary);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .deal-type {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }

        .deal-type label {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 16px;
        }

        .deal-type input[type="radio"] {
            width: 18px;
            height: 18px;
            accent-color: var(--accent-primary);
        }

        .modal-buttons {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .modal-btn {
            flex: 1;
            padding: 16px;
            border: none;
            border-radius: 14px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .modal-btn.primary {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
        }

        .modal-btn.secondary {
            background-color: var(--bg-card);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }

        .modal-btn:active {
            transform: scale(0.96);
        }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            left: 20px;
            right: 20px;
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px 20px;
            color: var(--text-primary);
            font-size: 15px;
            text-align: center;
            z-index: 2000;
            animation: slideUp 0.3s ease;
            max-width: 360px;
            margin: 0 auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Header -->
        <div class="header">
            <div class="header-top">
                <div class="logo">
                    <div class="logo-icon">P</div>
                    <div class="logo-text">PlayerOK</div>
                </div>
                <div class="profile-badge" onclick="showProfile()">
                    <div class="profile-avatar" id="userAvatar">U</div>
                    <span class="profile-name" id="userName">Загрузка...</span>
                </div>
            </div>

            <div class="balance-card">
                <div class="balance-row">
                    <span class="balance-label">Баланс</span>
                    <span class="balance-amount"><span id="userBalance">5,000</span> <span class="balance-currency">₽</span></span>
                </div>
                <div class="balance-row">
                    <span class="balance-label">Активных сделок</span>
                    <span class="balance-amount" style="font-size: 20px;" id="activeDeals">3</span>
                </div>
                <div class="balance-row">
                    <span class="balance-label">Рейтинг</span>
                    <span class="balance-amount" style="font-size: 20px;">⭐ 4.8</span>
                </div>
            </div>
        </div>

        <!-- Main Action Buttons -->
        <div class="action-buttons">
            <button class="action-btn sell" onclick="openModal('sellModal')">
                <span>💰</span> Продать
            </button>
            <button class="action-btn buy" onclick="openModal('buyModal')">
                <span>🛒</span> Купить
            </button>
            <button class="action-btn deal" onclick="openModal('dealModal')">
                <span>📝</span> Сделку
            </button>
        </div>

        <!-- Popular Products -->
        <div class="content-section">
            <div class="section-header">
                <h3 class="section-title">🔥 Горячие товары</h3>
                <span class="section-link" onclick="showAllProducts()">Все 24 →</span>
            </div>
            <div class="products-grid" id="productsGrid"></div>
        </div>

        <!-- Inventory -->
        <div class="content-section">
            <div class="section-header">
                <h3 class="section-title">📦 Мой инвентарь</h3>
                <span class="section-link" onclick="showAllInventory()">Все 8 →</span>
            </div>
            <div class="inventory-list" id="inventoryList"></div>
        </div>

        <!-- Active Deals -->
        <div class="content-section">
            <div class="section-header">
                <h3 class="section-title">📋 Активные сделки</h3>
                <span class="section-link" onclick="showAllDeals()">Все 5 →</span>
            </div>
            <div class="deals-list" id="dealsList"></div>
        </div>

        <!-- Bottom Navigation -->
        <div class="bottom-nav">
            <button class="nav-item active" onclick="switchTab('home', this)">
                <span>🏠</span>
                Главная
            </button>
            <button class="nav-item" onclick="switchTab('catalog', this)">
                <span>🔍</span>
                Каталог
            </button>
            <button class="nav-item" onclick="switchTab('deals', this)">
                <span>📊</span>
                Сделки
            </button>
            <button class="nav-item" onclick="switchTab('profile', this)">
                <span>👤</span>
                Профиль
            </button>
        </div>

        <!-- Sell Modal -->
        <div id="sellModal" class="modal">
            <div class="modal-content">
                <h3 class="modal-title">💰 Продажа товара</h3>
                <div class="form-group">
                    <label>Выберите товар</label>
                    <select id="sellItemSelect">
                        <option value="CS:GO Skin">CS:GO Skin (2,500 ₽)</option>
                        <option value="V-Bucks 1000">V-Bucks 1000 (450 ₽)</option>
                        <option value="Discord Nitro">Discord Nitro (299 ₽)</option>
                        <option value="Steam Gift">Steam Gift (500 ₽)</option>
                        <option value="Netflix Premium">Netflix Premium (350 ₽)</option>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Количество</label>
                        <input type="number" id="sellQuantity" value="1" min="1">
                    </div>
                    <div class="form-group">
                        <label>Цена за шт.</label>
                        <input type="number" id="sellPrice" value="2500" min="1">
                    </div>
                </div>
                <div class="modal-buttons">
                    <button class="modal-btn primary" onclick="createSellDeal()">Продать</button>
                    <button class="modal-btn secondary" onclick="closeModal('sellModal')">Отмена</button>
                </div>
            </div>
        </div>

        <!-- Buy Modal -->
        <div id="buyModal" class="modal">
            <div class="modal-content">
                <h3 class="modal-title">🛒 Покупка товара</h3>
                <div class="form-group">
                    <label>Название товара</label>
                    <input type="text" id="buyItemName" placeholder="Например: CS:GO Prime">
                </div>
                <div class="form-group">
                    <label>Сумма покупки (₽)</label>
                    <input type="number" id="buyAmount" placeholder="Введите сумму">
                </div>
                <div class="modal-buttons">
                    <button class="modal-btn primary" onclick="createBuyDeal()">Купить</button>
                    <button class="modal-btn secondary" onclick="closeModal('buyModal')">Отмена</button>
                </div>
            </div>
        </div>

        <!-- Create Deal Modal -->
        <div id="dealModal" class="modal">
            <div class="modal-content">
                <h3 class="modal-title">📝 Создание сделки</h3>
                <div class="deal-type">
                    <label>
                        <input type="radio" name="dealType" value="buy" checked> 🛒 Покупка
                    </label>
                    <label>
                        <input type="radio" name="dealType" value="sell"> 💰 Продажа
                    </label>
                </div>
                <div class="form-group">
                    <label>Товар</label>
                    <input type="text" id="dealItemName" placeholder="Что продаете/покупаете?">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Количество</label>
                        <input type="number" id="dealQuantity" value="1" min="1">
                    </div>
                    <div class="form-group">
                        <label>Цена за шт.</label>
                        <input type="number" id="dealPrice" placeholder="0">
                    </div>
                </div>
                <button class="modal-btn primary" onclick="createDeal()" style="width: 100%; margin-top: 10px;">Создать сделку</button>
            </div>
        </div>
    </div>

    <script>
        // Telegram WebApp initialization
        const tg = window.Telegram.WebApp;
        const userId = '7678755832';
        const botToken = '8795895107:AAF1gHb_Qe6ampB-UF9iEpBZKhU6TGi8PRY';
        
        // App state
        let appState = {
            balance: 5000,
            activeDeals: 3,
            products: [
                { id: 1, name: 'CS:GO Prime', icon: '🎮', price: 1200, orders: 234 },
                { id: 2, name: 'V-Bucks 1000', icon: '💎', price: 450, orders: 567 },
                { id: 3, name: 'Discord Nitro', icon: '⚡', price: 299, orders: 892 },
                { id: 4, name: 'Steam Gift', icon: '🎁', price: 500, orders: 445 },
                { id: 5, name: 'Netflix Premium', icon: '🎬', price: 350, orders: 678 },
                { id: 6, name: 'Spotify Premium', icon: '🎵', price: 199, orders: 723 }
            ],
            inventory: [
                { id: 1, name: 'CS:GO Skin (AK-47)', icon: '🔫', price: 2500, quantity: 2 },
                { id: 2, name: 'V-Bucks 2800', icon: '💎', price: 1250, quantity: 3 },
                { id: 3, name: 'Discord Nitro Year', icon: '⚡', price: 2990, quantity: 1 },
                { id: 4, name: 'Steam Wallet 1000', icon: '🎮', price: 850, quantity: 2 }
            ],
            deals: [
                { id: 23456, name: 'Покупка CS:GO Prime', price: 1200, status: 'active', date: '2024-01-15' },
                { id: 23457, name: 'Продажа V-Bucks', price: 450, status: 'completed', date: '2024-01-14' },
                { id: 23458, name: 'Покупка Discord Nitro', price: 299, status: 'active', date: '2024-01-15' }
            ]
        };

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            tg.ready();
            tg.expand();
            
            // Set user info
            const user = tg.initDataUnsafe?.user;
            if (user) {
                document.getElementById('userName').textContent = user.first_name || 'Player';
                document.getElementById('userAvatar').textContent = (user.first_name || 'P')[0];
            } else {
                document.getElementById('userName').textContent = 'Player_7678';
            }
            
            // Load data
            loadProducts();
            loadInventory();
            loadDeals();
            
            // Set main button
            tg.MainButton.setText('Закрыть магазин');
            tg.MainButton.onClick(function() {
                tg.close();
            });
            
            // Send start message to bot
            fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: userId,
                    text: '✅ PlayerOK Market запущен! Добро пожаловать!'
                })
            });
        });

        // Load products
        function loadProducts() {
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = '';
            
            appState.products.slice(0, 4).forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <div class="product-image">${product.icon}</div>
                    <div class="product-title">${product.name}</div>
                    <div class="product-price">${product.price.toLocaleString()} <span>₽</span></div>
                    <button class="buy-btn" onclick="quickBuy('${product.name}', ${product.price})">Купить</button>
                `;
                grid.appendChild(card);
            });
        }

        // Load inventory
        function loadInventory() {
            const list = document.getElementById('inventoryList');
            list.innerHTML = '';
            
            appState.inventory.slice(0, 2).forEach(item => {
                const element = document.createElement('div');
                element.className = 'inventory-item';
                element.innerHTML = `
                    <div class="item-icon">${item.icon}</div>
                    <div class="item-info">
                        <div class="item-name">${item.name}</div>
                        <div class="item-details">
                            <span>💰 ${item.price.toLocaleString()} ₽</span>
                            <span class="item-quantity">📦 x${item.quantity}</span>
                        </div>
                    </div>
                    <button class="sell-small" onclick="sellFromInventory('${item.name}', ${item.price})">Продать</button>
                `;
                list.appendChild(element);
            });
        }

        // Load deals
        function loadDeals() {
            const list = document.getElementById('dealsList');
            list.innerHTML = '';
            
            appState.deals.slice(0, 2).forEach(deal => {
                const element = document.createElement('div');
                element.className = 'deal-card';
                element.innerHTML = `
                    <div class="deal-info">
                        <h4>${deal.name}</h4>
                        <div class="deal-meta">
                            <span>№ ${deal.id}</span>
                            <span>💰 ${deal.price.toLocaleString()} ₽</span>
                        </div>
                    </div>
                    <span class="deal-status status-${deal.status}">${deal.status === 'active' ? '🟢 Активна' : '✅ Завершена'}</span>
                `;
                list.appendChild(element);
            });
        }

        // Modal functions
        function openModal(modalId) {
            document.getElementById(modalId).classList.add('active');
            tg.HapticFeedback.impactOccurred('light');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        // Action functions
        function quickBuy(item, price) {
            if (appState.balance >= price) {
                appState.balance -= price;
                updateBalance();
                showNotification(`✅ Куплено: ${item} за ${price.toLocaleString()} ₽`);
                tg.HapticFeedback.notificationOccurred('success');
                
                // Send to bot
                sendToBot('purchase', { item, price });
            } else {
                showNotification('❌ Недостаточно средств');
                tg.HapticFeedback.notificationOccurred('error');
            }
        }

        function sellFromInventory(item, price) {
            document.getElementById('sellItemSelect').value = item;
            document.getElementById('sellPrice').value = price;
            openModal('sellModal');
        }

        function createSellDeal() {
            const item = document.getElementById('sellItemSelect').value;
            const quantity = document.getElementById('sellQuantity').value;
            const price = document.getElementById('sellPrice').value;
            const totalPrice = price * quantity;
            
            appState.activeDeals++;
            document.getElementById('activeDeals').textContent = appState.activeDeals;
            
            showNotification(`✅ Сделка на продажу создана! ${item}, ${quantity} шт. на ${totalPrice.toLocaleString()} ₽`);
            closeModal('sellModal');
            tg.HapticFeedback.notificationOccurred('success');
            
            // Add to deals
            appState.deals.unshift({
                id: Math.floor(Math.random() * 90000) + 10000,
                name: `Продажа ${item}`,
                price: totalPrice,
                status: 'active',
                date: new Date().toISOString().split('T')[0]
            });
            loadDeals();
            
            // Send to bot
            sendToBot('sell_deal', { item, quantity, price, totalPrice });
        }

        function createBuyDeal() {
            const item = document.getElementById('buyItemName').value;
            const amount = document.getElementById('buyAmount').value;
            
            if (item && amount) {
                if (appState.balance >= amount) {
                    appState.balance -= parseInt(amount);
                    updateBalance();
                    
                    appState.activeDeals++;
                    document.getElementById('activeDeals').textContent = appState.activeDeals;
                    
                    showNotification(`✅ Сделка на покупку создана! ${item} на ${Number(amount).toLocaleString()} ₽`);
                    
                    // Add to deals
                    appState.deals.unshift({
                        id: Math.floor(Math.random() * 90000) + 10000,
                        name: `Покупка ${item}`,
                        price: parseInt(amount),
                        status: 'active',
                        date: new Date().toISOString().split('T')[0]
                    });
                    loadDeals();
                    
                    tg.HapticFeedback.notificationOccurred('success');
                    
                    // Send to bot
                    sendToBot('buy_deal', { item, amount });
                } else {
                    showNotification('❌ Недостаточно средств');
                    tg.HapticFeedback.notificationOccurred('error');
                }
            } else {
                showNotification('❌ Заполните все поля');
            }
            closeModal('buyModal');
        }

        function createDeal() {
            const dealType = document.querySelector('input[name="dealType"]:checked').value;
            const item = document.getElementById('dealItemName').value;
            const quantity = document.getElementById('dealQuantity').value;
            const price = document.getElementById('dealPrice').value;
            
            if (item && quantity && price) {
                const totalPrice = parseInt(price) * parseInt(quantity);
                const typeText = dealType === 'buy' ? 'покупку' : 'продажу';
                
                if (dealType === 'buy' && appState.balance < totalPrice) {
                    showNotification('❌ Недостаточно средств');
                    tg.HapticFeedback.notificationOccurred('error');
                    return;
                }
                
                if (dealType === 'buy') {
                    appState.balance -= totalPrice;
                    updateBalance();
                }
                
                appState.activeDeals++;
                document.getElementById('activeDeals').textContent = appState.activeDeals;
                
                showNotification(`✅ Сделка на ${typeText} создана! ${item}, ${quantity} шт.`);
                
                // Add to deals
                appState.deals.unshift({
                    id: Math.floor(Math.random() * 90000) + 10000,
                    name: `${dealType === 'buy' ? 'Покупка' : 'Продажа'} ${item}`,
                    price: totalPrice,
                    status: 'active',
                    date: new Date().toISOString().split('T')[0]
                });
                loadDeals();
                
                tg.HapticFeedback.notificationOccurred('success');
                
                // Send to bot
                sendToBot('create_deal', { type: dealType, item, quantity, price, totalPrice });
                
                closeModal('dealModal');
            } else {
                showNotification('❌ Заполните все поля');
            }
        }

        function sendToBot(action, data) {
            const message = `🎮 PlayerOK Market\nДействие: ${action}\nДанные: ${JSON.stringify(data)}\nПользователь: ${userId}`;
            
            fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: userId,
                    text: message
                })
            });
        }

        function showNotification(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        function updateBalance() {
            document.getElementById('userBalance').textContent = appState.balance.toLocaleString();
        }

        function switchTab(tab, element) {
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            element.classList.add('active');
            
            tg.HapticFeedback.impactOccurred('light');
            
            if (tab === 'profile') {
                showProfile();
            } else if (tab === 'catalog') {
                showNotification('📱 Открыт каталог товаров');
            } else if (tab === 'deals') {
                showNotification('📋 Все сделки');
            }
        }

        function showProfile() {
            const user = tg.initDataUnsafe?.user;
            const profileInfo = user ? 
                `👤 Профиль:\nID: ${user.id}\nИмя: ${user.first_name}\nUsername: @${user.username || 'отсутствует'}` :
                `👤 Профиль\nID: ${userId}\nСтатус: Активен`;
            
            showNotification(profileInfo);
            
            // Send to bot
            sendToBot('profile_view', { userId: userId });
        }

        function showAllProducts() {
            showNotification('📱 Открыт полный каталог (24 товара)');
        }

        function showAllInventory() {
            showNotification(`📦 Весь инвентарь (${appState.inventory.length} предметов)`);
        }

        function showAllDeals() {
            showNotification(`📋 Все сделки (${appState.deals.length} записей)`);
        }

        // Close modals on outside click
        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('active');
            }
        });

        // Send data to bot via Telegram WebApp
        function sendDataToBot(data) {
            tg.sendData(JSON.stringify({
                userId: userId,
                ...data
            }));
        }
    </script>
</body>
</html>
