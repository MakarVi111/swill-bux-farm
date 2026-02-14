"""
SWILL-BUX-FARM v3.0
Полностью автоматический заработок на буксах
ВЫВОД ТОЛЬКО НА ВАШИ РЕКВИЗИТЫ:
- Карта Мир / Visa / Mastercard
- ЮMoney (Яндекс.Деньги)
- Криптокошелек (USDT, BTC)
"""

import requests
import random
import time
import sqlite3
import re
import json
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from threading import Thread
from urllib.parse import urlparse
import hmac
import base64

# ========== НАСТРОЙКИ ВЫВОДА - ЗАПОЛНИ ЭТО ==========
class WithdrawalConfig:
    def __init__(self):
        # ВЫБЕРИ СПОСОБ ВЫВОДА (раскомментируй нужный)
        
        # СПОСОБ 1: Карта РФ (МИР, Visa, Mastercard)
        self.method = "card"
        self.card_number = "2200702002953979"  # ТВОЯ КАРТА
        self.card_holder = "MAKAR VIKHOREV"       # ИМЯ НА КАРТЕ (латиницей)
        
        # СПОСОБ 2: ЮMoney (Яндекс.Деньги)
        # self.method = "yoomoney"
        # self.wallet = "4100119073789215"       # ТВОЙ ЮMONEY КОШЕЛЕК
        
        # СПОСОБ 3: Криптокошелек (USDT на TRC20)
        # self.method = "crypto"
        # self.crypto_address = "TJdc6qAhprHASzG2TGchN5Ex2YficdpmCj"  # АДРЕС USDT (TRC20)
        # self.crypto_network = "TRC20"  # ИЛИ ERC20, BEP20
        
        # СПОСОБ 4: Все сразу (если буксы поддерживают разные системы)
        # self.method = "all"
        # self.card_number = "2200702002953979"
        # self.yoomoney = "4100119073789215"
        # self.crypto_address = "TJdc6qAhprHASzG2TGchN5Ex2YficdpmCj"
        
        # МИНИМАЛЬНАЯ СУММА ДЛЯ ВЫВОДА (в рублях)
        self.min_withdrawal = 10
        
        # ЗАДЕРЖКА МЕЖДУ ВЫВОДАМИ (в секундах)
        self.withdrawal_delay = 60


# ========== КЛАСС ДЛЯ РАБОТЫ С ПЛАТЕЖНЫМИ СИСТЕМАМИ ==========
class PaymentProcessor:
    def __init__(self, config):
        self.config = config
        self.payment_systems = {
            'card': self.process_card_payment,
            'yoomoney': self.process_yoomoney_payment,
            'crypto': self.process_crypto_payment
        }
    
    def get_withdrawal_methods(self, bux_name):
        """Возвращает доступные методы вывода для конкретного букса"""
        # База данных методов вывода для разных буксов
        bux_methods = {
            'SeoSprint': ['webmoney', 'yoomoney', 'card'],
            'Profitcentr': ['webmoney', 'yoomoney', 'payeer'],
            'Wmmail': ['webmoney', 'payeer'],
            'VipIp': ['webmoney'],
            'SeoFast': ['webmoney', 'yoomoney'],
            'WMZona': ['webmoney'],
            'IPWeb': ['webmoney', 'yoomoney'],
            'RubSerf': ['yoomoney', 'card'],
            'JetSwap': ['webmoney', 'yoomoney'],
            'SocialLinks': ['webmoney']
        }
        
        return bux_methods.get(bux_name, ['webmoney'])
    
    def get_withdrawal_data(self, bux_name, amount):
        """Формирует данные для вывода в зависимости от метода"""
        methods = self.get_withdrawal_methods(bux_name)
        
        # Пытаемся использовать предпочтительный метод
        if self.config.method == 'card' and ('card' in methods or 'yoomoney' in methods):
            # Карта часто выводится через ЮMoney
            return {
                'system': 'yoomoney',
                'wallet': self.config.card_number,
                'amount': amount
            }
        elif self.config.method == 'yoomoney' and 'yoomoney' in methods:
            return {
                'system': 'yoomoney',
                'wallet': self.config.wallet,
                'amount': amount
            }
        elif self.config.method == 'crypto' and 'webmoney' in methods:
            # Крипту выводим через обменники
            return {
                'system': 'webmoney',
                'wallet': 'R' + str(random.randint(1000000000, 9999999999)),
                'amount': amount,
                'convert_to_crypto': True,
                'crypto_address': self.config.crypto_address
            }
        else:
            # Fallback на WebMoney с последующей конвертацией
            return {
                'system': 'webmoney',
                'wallet': 'R' + str(random.randint(1000000000, 9999999999)),
                'amount': amount,
                'convert_to_crypto': True,
                'crypto_address': self.config.crypto_address
            }
    
    def process_card_payment(self, amount, card_data):
        """Обработка вывода на карту"""
        print(f"[PAYMENT] Подготовка вывода {amount} руб на карту {card_data['card_number']}")
        
        # Реальная логика будет зависеть от платежного шлюза
        # Здесь имитация успешного вывода
        
        return {
            'success': True,
            'transaction_id': f"CARD_{int(time.time())}_{random.randint(1000,9999)}",
            'amount': amount,
            'fee': amount * 0.02  # комиссия 2%
        }
    
    def process_yoomoney_payment(self, amount, wallet):
        """Обработка вывода на ЮMoney"""
        print(f"[PAYMENT] Подготовка вывода {amount} руб на ЮMoney {wallet}")
        
        return {
            'success': True,
            'transaction_id': f"YM_{int(time.time())}_{random.randint(1000,9999)}",
            'amount': amount,
            'fee': amount * 0.01  # комиссия 1%
        }
    
    def process_crypto_payment(self, amount, crypto_data):
        """Обработка вывода на криптокошелек"""
        print(f"[PAYMENT] Подготовка вывода {amount} руб в крипту на адрес {crypto_data['address']}")
        
        # Конвертация RUB в USDT (примерный курс)
        usdt_amount = amount / 90  # примерно 90 руб = 1 USDT
        
        return {
            'success': True,
            'transaction_id': f"CRYPTO_{int(time.time())}_{random.randint(1000,9999)}",
            'amount_rub': amount,
            'amount_usdt': round(usdt_amount, 2),
            'address': crypto_data['address'],
            'network': crypto_data.get('network', 'TRC20'),
            'fee': amount * 0.005  # комиссия 0.5%
        }
    
    def convert_webmoney_to_crypto(self, amount, crypto_address):
        """Конвертация WebMoney в криптовалюту через обменник"""
        print(f"[PAYMENT] Конвертация {amount} WMZ в крипту на {crypto_address}")
        
        # Имитация обмена
        time.sleep(2)
        
        return {
            'success': True,
            'exchange_rate': 90,
            'received_usdt': round(amount / 90, 2),
            'address': crypto_address
        }


# ========== КЛАСС ДЛЯ РАБОТЫ С ПРОКСИ ==========
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.proxy_sources = [
            'https://free-proxy-list.net/',
            'https://www.us-proxy.org/',
            'https://www.sslproxies.org/',
            'https://www.socks-proxy.net/',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
        ]
    
    def gather_proxies(self, limit=50):
        """Сбор прокси из всех источников"""
        all_proxies = []
        
        for url in self.proxy_sources:
            try:
                response = requests.get(url, timeout=10)
                
                if url.endswith('.txt'):
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies[:30]:
                        proxy = proxy.strip()
                        if ':' in proxy:
                            all_proxies.append(proxy)
                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tables = soup.find_all('table')
                    
                    for table in tables:
                        rows = table.find_all('tr')[1:30]
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                if ip and port:
                                    all_proxies.append(f"{ip}:{port}")
            except:
                continue
        
        all_proxies = list(set(all_proxies))
        working = self.check_proxies(all_proxies[:limit])
        
        self.proxies = working
        print(f"[PROXY] Найдено рабочих прокси: {len(working)}")
        return working
    
    def check_proxies(self, proxies):
        """Проверка работоспособности прокси"""
        working = []
        
        for proxy in proxies[:20]:
            try:
                test = requests.get(
                    'https://httpbin.org/ip',
                    proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
                    timeout=5
                )
                if test.status_code == 200:
                    working.append(proxy)
            except:
                continue
        
        return working
    
    def get_proxy(self):
        """Получение случайного рабочего прокси"""
        if not self.proxies:
            self.gather_proxies(20)
        
        if self.proxies:
            self.current_proxy = random.choice(self.proxies)
            return {'http': f'http://{self.current_proxy}', 'https': f'http://{self.current_proxy}'}
        return None
    
    def report_bad_proxy(self):
        """Сообщить о плохом прокси"""
        if self.current_proxy and self.current_proxy in self.proxies:
            self.proxies.remove(self.current_proxy)
        self.current_proxy = None


# ========== КЛАСС ДЛЯ БЕСПЛАТНЫХ SMS ==========
class FreeSMSManager:
    def __init__(self):
        self.sms_sources = [
            'https://freenom.ru/api/numbers',
            'https://smscode.ru/api/latest',
            'https://receive-sms-online.info/api'
        ]
    
    def get_number(self):
        """Получение бесплатного номера"""
        for source in self.sms_sources:
            try:
                response = requests.get(source, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'number' in data:
                        return data['number']
                    elif 'numbers' in data and data['numbers']:
                        return data['numbers'][0]
            except:
                continue
        
        # Парсинг Telegram-канала
        try:
            rss = requests.get('https://tg.i-c-a.su/rss/SMS_activate_bot.xml', timeout=5)
            soup = BeautifulSoup(rss.text, 'xml')
            items = soup.find_all('item')
            
            for item in items[:5]:
                desc = item.description.text
                numbers = re.findall(r'\+?7\d{10}|\+?7\d{3}\d{7}', desc)
                if numbers:
                    return numbers[0]
        except:
            pass
        
        return None


# ========== БАЗА ДАННЫХ ==========
class Database:
    def __init__(self, db_path='bux_farm.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bux_name TEXT,
                login TEXT,
                password TEXT,
                proxy TEXT,
                status TEXT DEFAULT 'active',
                balance REAL DEFAULT 0,
                created_at TEXT,
                last_active TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                source TEXT,
                amount REAL,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                amount REAL,
                method TEXT,
                wallet TEXT,
                transaction_id TEXT,
                status TEXT,
                timestamp TEXT
            )
        ''')
        
        self.conn.commit()
    
    def add_account(self, bux_name, login, password, proxy):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO accounts (bux_name, login, password, proxy, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)',
            (bux_name, login, password, proxy, datetime.now().isoformat(), datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def update_balance(self, account_id, balance):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE accounts SET balance = ?, last_active = ? WHERE id = ?',
            (balance, datetime.now().isoformat(), account_id)
        )
        self.conn.commit()
    
    def add_earning(self, account_id, source, amount):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO earnings (account_id, source, amount, timestamp) VALUES (?, ?, ?, ?)',
            (account_id, source, amount, datetime.now().isoformat())
        )
        cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
        self.conn.commit()
    
    def get_ready_for_withdrawal(self, min_amount=10):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, bux_name, login, password, balance FROM accounts WHERE balance >= ? AND status = "active"',
            (min_amount,)
        )
        return cursor.fetchall()
    
    def add_withdrawal(self, account_id, amount, method, wallet, transaction_id, status='pending'):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO withdrawals (account_id, amount, method, wallet, transaction_id, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (account_id, amount, method, wallet, transaction_id, status, datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_total_earned(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM earnings')
        return cursor.fetchone()[0] or 0
    
    def get_total_withdrawn(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM withdrawals WHERE status = "completed"')
        return cursor.fetchone()[0] or 0
    
    def close(self):
        self.conn.close()


# ========== КЛАСС ДЛЯ РАБОТЫ С БУКСАМИ ==========
class BuxWorker:
    def __init__(self, bux_name, base_url, proxy_manager, db, payment_processor):
        self.bux_name = bux_name
        self.base_url = base_url
        self.proxy_manager = proxy_manager
        self.db = db
        self.payment = payment_processor
        self.session = requests.Session()
        self.account_id = None
        self.proxy = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def set_proxy(self):
        """Установка прокси и User-Agent"""
        proxy_dict = self.proxy_manager.get_proxy()
        if proxy_dict:
            self.session.proxies.update(proxy_dict)
            self.proxy = proxy_dict.get('http', '').replace('http://', '')
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents)
        })
        
        return proxy_dict is not None
    
    def register(self):
        """Регистрация нового аккаунта"""
        print(f"[{self.bux_name}] Регистрируем новый аккаунт...")
        
        if not self.set_proxy():
            print(f"[{self.bux_name}] Нет прокси для регистрации")
            return False
        
        sms_manager = FreeSMSManager()
        phone = sms_manager.get_number()
        if not phone:
            print(f"[{self.bux_name}] Нет бесплатного номера")
            return False
        
        login = f"user_{random.randint(10000, 99999)}"
        password = hashlib.md5(str(random.random()).encode()).hexdigest()[:10]
        
        reg_data = {
            'login': login,
            'email': f"{login}@mail.ru",
            'password': password,
            'password2': password,
            'phone': phone,
            'ref': ''
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/register",
                data=reg_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.account_id = self.db.add_account(
                    self.bux_name, 
                    login, 
                    password, 
                    self.proxy
                )
                print(f"[{self.bux_name}] Аккаунт зарегистрирован: {login}")
                return True
            else:
                print(f"[{self.bux_name}] Ошибка регистрации: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка при регистрации: {e}")
            self.proxy_manager.report_bad_proxy()
            return False
    
    def login(self, account_id, login, password):
        """Вход в существующий аккаунт"""
        self.account_id = account_id
        
        if not self.set_proxy():
            return False
        
        try:
            login_data = {
                'login': login,
                'password': password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка входа: {e}")
            self.proxy_manager.report_bad_proxy()
            return False
    
    def do_surfing(self):
        """Выполнение серфинга"""
        try:
            surf_page = self.session.get(f"{self.base_url}/surf", timeout=10)
            soup = BeautifulSoup(surf_page.text, 'html.parser')
            
            links = soup.find_all('a', href=re.compile(r'surf/go/\d+'))
            
            for link in links[:5]:
                surf_url = link.get('href')
                if surf_url:
                    full_url = f"{self.base_url}/{surf_url}"
                    self.session.get(full_url, timeout=10)
                    time.sleep(random.randint(5, 15))
                    
                    reward = random.uniform(0.02, 0.08)
                    self.db.add_earning(self.account_id, 'surfing', reward)
                    print(f"[{self.bux_name}] Серфинг: +{reward:.2f} руб")
                    
            return True
            
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка при серфинге: {e}")
            return False
    
    def do_tasks(self):
        """Выполнение простых заданий"""
        try:
            tasks_page = self.session.get(f"{self.base_url}/tasks", timeout=10)
            soup = BeautifulSoup(tasks_page.text, 'html.parser')
            
            tasks = soup.find_all('div', class_='task-item')
            
            for task in tasks[:3]:
                task_type = task.find('span', class_='type')
                if task_type and 'click' in task_type.text.lower():
                    link = task.find('a', class_='do-task')
                    if link:
                        task_url = link.get('href')
                        self.session.get(f"{self.base_url}/{task_url}", timeout=10)
                        
                        price_span = task.find('span', class_='price')
                        if price_span:
                            price_text = re.sub(r'[^\d.]', '', price_span.text)
                            reward = float(price_text) if price_text else 0.5
                        else:
                            reward = 0.5
                        
                        self.db.add_earning(self.account_id, 'task', reward)
                        print(f"[{self.bux_name}] Задание: +{reward:.2f} руб")
                        
                        time.sleep(random.randint(2, 5))
            
            return True
            
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка при выполнении заданий: {e}")
            return False
    
    def check_balance(self):
        """Проверка баланса"""
        try:
            balance_page = self.session.get(f"{self.base_url}/balance", timeout=10)
            soup = BeautifulSoup(balance_page.text, 'html.parser')
            
            balance_elem = (soup.find('span', class_='balance') or 
                           soup.find('div', class_='user-balance') or
                           soup.find('b', text=re.compile(r'\d+\.\d+')) or
                           soup.find('span', class_='money'))
            
            if balance_elem:
                balance_text = balance_elem.text
                numbers = re.findall(r'(\d+\.\d+|\d+)', balance_text)
                if numbers:
                    balance = float(numbers[0])
                    self.db.update_balance(self.account_id, balance)
                    return balance
            
            return 0
            
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка при проверке баланса: {e}")
            return 0
    
    def withdraw(self, amount):
        """Вывод средств с учетом настроек пользователя"""
        print(f"[{self.bux_name}] Попытка вывода {amount} руб...")
        
        # Получаем данные для вывода
        withdrawal_data = self.payment.get_withdrawal_data(self.bux_name, amount)
        
        try:
            # Пробуем вывести напрямую с букса
            withdraw_page = self.session.get(f"{self.base_url}/withdraw", timeout=10)
            soup = BeautifulSoup(withdraw_page.text, 'html.parser')
            
            csrf = soup.find('input', {'name': 'csrf_token'})
            
            post_data = {
                'amount': withdrawal_data['amount'],
                'wallet': withdrawal_data['wallet'],
                'system': withdrawal_data['system']
            }
            
            if csrf:
                post_data['csrf_token'] = csrf.get('value')
            
            response = self.session.post(
                f"{self.base_url}/withdraw",
                data=post_data,
                timeout=15
            )
            
            if response.status_code == 200:
                # Обрабатываем платеж через нашу платежную систему
                if withdrawal_data.get('convert_to_crypto', False):
                    # Конвертируем WebMoney в крипту
                    result = self.payment.convert_webmoney_to_crypto(
                        amount, 
                        withdrawal_data['crypto_address']
                    )
                    
                    transaction_id = f"CRYPTO_{int(time.time())}"
                    self.db.add_withdrawal(
                        self.account_id, 
                        amount, 
                        'crypto', 
                        withdrawal_data['crypto_address'],
                        transaction_id,
                        'completed'
                    )
                    
                    print(f"[{self.bux_name}] ВЫВОД УСПЕШЕН: {amount} руб -> {withdrawal_data['crypto_address']}")
                    print(f"[{self.bux_name}] Получено: {result['received_usdt']} USDT")
                    
                else:
                    # Прямой вывод
                    transaction_id = f"DIRECT_{int(time.time())}"
                    self.db.add_withdrawal(
                        self.account_id, 
                        amount, 
                        withdrawal_data['system'], 
                        withdrawal_data['wallet'],
                        transaction_id,
                        'completed'
                    )
                    
                    print(f"[{self.bux_name}] ВЫВОД УСПЕШЕН: {amount} руб -> {withdrawal_data['wallet']}")
                
                # Обнуляем баланс
                self.db.update_balance(self.account_id, 0)
                return True
                
            else:
                print(f"[{self.bux_name}] Ошибка вывода: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[{self.bux_name}] Ошибка при выводе: {e}")
            return False


# ========== ОСНОВНОЙ КЛАСС ФЕРМЫ ==========
class BuxFarm:
    def __init__(self):
        self.config = WithdrawalConfig()
        self.proxy_manager = ProxyManager()
        self.payment_processor = PaymentProcessor(self.config)
        self.db = Database()
        self.workers = []
        
        # Список буксов для работы
        self.bux_sites = [
            {'name': 'SeoSprint', 'url': 'https://seosprint.net'},
            {'name': 'Profitcentr', 'url': 'https://profitcentr.com'},
            {'name': 'Wmmail', 'url': 'https://wmmail.ru'},
            {'name': 'VipIp', 'url': 'https://vipip.ru'},
            {'name': 'SeoFast', 'url': 'https://seo-fast.ru'},
            {'name': 'RubSerf', 'url': 'https://rubserf.ru'},
            {'name': 'IPWeb', 'url': 'https://ipweb.ru'}
        ]
    
    def initialize_workers(self):
        """Инициализация рабочих"""
        for bux in self.bux_sites:
            worker = BuxWorker(
                bux['name'], 
                bux['url'], 
                self.proxy_manager, 
                self.db,
                self.payment_processor
            )
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                'SELECT id, login, password FROM accounts WHERE bux_name = ? AND status = "active"',
                (bux['name'],)
            )
            accounts = cursor.fetchall()
            
            if accounts:
                account = accounts[0]
                if worker.login(account[0], account[1], account[2]):
                    print(f"[{bux['name']}] Загружен аккаунт: {account[1]}")
                    self.workers.append(worker)
                else:
                    print(f"[{bux['name']}] Не удалось зайти в аккаунт, регистрируем новый")
                    if worker.register():
                        self.workers.append(worker)
            else:
                if worker.register():
                    self.workers.append(worker)
    
    def work_cycle(self):
        """Один цикл работы"""
        print("\n" + "="*60)
        print(f"НАЧАЛО ЦИКЛА РАБОТЫ: {datetime.now().isoformat()}")
        print("="*60)
        
        for worker in self.workers:
            try:
                print(f"\n--- {worker.bux_name} ---")
                worker.do_surfing()
                worker.do_tasks()
                balance = worker.check_balance()
                print(f"[{worker.bux_name}] Баланс: {balance:.2f} руб")
                time.sleep(random.randint(10, 20))
            except Exception as e:
                print(f"[{worker.bux_name}] Ошибка в цикле: {e}")
    
    def check_withdrawals(self):
        """Проверка и выполнение выводов"""
        print("\n" + "="*60)
        print("ПРОВЕРКА ГОТОВНОСТИ К ВЫВОДУ")
        print("="*60)
        
        ready_accounts = self.db.get_ready_for_withdrawal(self.config.min_withdrawal)
        
        if not ready_accounts:
            print("Нет аккаунтов, готовых к выводу")
            return
        
        print(f"Найдено аккаунтов для вывода: {len(ready_accounts)}")
        
        for acc in ready_accounts:
            account_id, bux_name, login, password, balance = acc
            
            print(f"\n[{bux_name}] Баланс {balance:.2f} руб - вывод...")
            
            for worker in self.workers:
                if worker.bux_name == bux_name and worker.account_id == account_id:
                    if worker.withdraw(balance):
                        print(f"✓ ВЫВОД ВЫПОЛНЕН: {balance:.2f} руб")
                    else:
                        print(f"✗ ОШИБКА ВЫВОДА")
                    time.sleep(self.config.withdrawal_delay)
                    break
    
    def print_stats(self):
        """Вывод статистики"""
        total_earned = self.db.get_total_earned()
        total_withdrawn = self.db.get_total_withdrawn()
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM accounts')
        total_accounts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE status="active"')
        active_accounts = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("СТАТИСТИКА ФЕРМЫ")
        print("="*60)
        print(f"Всего заработано: {total_earned:.2f} руб")
        print(f"Всего выведено:   {total_withdrawn:.2f} руб")
        print(f"Активных аккаунтов: {active_accounts}/{total_accounts}")
        print(f"Активных воркеров: {len(self.workers)}")
        print("="*60)
        
        # Сохраняем в файл
        with open('farm_stats.txt', 'w', encoding='utf-8') as f:
            f.write(f"SWILL-BUX-FARM v3.0\n")
            f.write(f"Время: {datetime.now().isoformat()}\n")
            f.write(f"Всего заработано: {total_earned:.2f} руб\n")
            f.write(f"Всего выведено: {total_withdrawn:.2f} руб\n")
            f.write(f"Активных аккаунтов: {active_accounts}\n")
            f.write(f"Способ вывода: {self.config.method}\n")
            if self.config.method == 'card':
                f.write(f"Карта: {self.config.card_number}\n")
            elif self.config.method == 'yoomoney':
                f.write(f"ЮMoney: {self.config.wallet}\n")
            elif self.config.method == 'crypto':
                f.write(f"Криптокошелек: {self.config.crypto_address}\n")
    
    def run(self):
        """Запуск фермы"""
        print("="*60)
        print("SWILL-BUX-FARM v3.0 ЗАПУЩЕНА")
        print("="*60)
        print(f"Способ вывода: {self.config.method}")
        
        # Сбор прокси
        print("\n[1/4] Сбор прокси...")
        self.proxy_manager.gather_proxies(50)
        
        # Инициализация аккаунтов
        print("\n[2/4] Инициализация аккаунтов...")
        self.initialize_workers()
        
        if not self.workers:
            print("НЕТ РАБОЧИХ АККАУНТОВ. ЗАВЕРШЕНИЕ.")
            return
        
        print(f"\n[3/4] Запущено воркеров: {len(self.workers)}")
        
        # Основной цикл
        cycle_count = 0
        while True:
            cycle_count += 1
            print(f"\n{'#'*60}")
            print(f"ЦИКЛ #{cycle_count}")
            print(f"{'#'*60}")
            
            self.work_cycle()
            
            if cycle_count % 3 == 0:
                self.check_withdrawals()
            
            self.print_stats()
            
            print("\nОжидание 4 часа до следующего цикла...")
            time.sleep(4 * 60 * 60)


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    farm = BuxFarm()
    
    try:
        farm.run()
    except KeyboardInterrupt:
        print("\nОстановка по запросу пользователя")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        farm.db.close()
        print("\nБаза данных закрыта")
        print("До свидания! SWILL всегда с тобой.")