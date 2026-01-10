import sqlite3
import time
import os
import string
import random
from datetime import datetime

class Main:
    def __init__(self):
        self.db_name = 'bank_cards.db'
        self.active_card_id = None
        self.init_database()
        self.load_active_card()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица для карт
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT UNIQUE NOT NULL,
                pin_code TEXT NOT NULL,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица для истории операций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                operation_type TEXT,
                amount INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_active_card(self):
        """Загрузка активной карты из базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM cards WHERE is_active = 1 LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            self.active_card_id = result[0]
        
        conn.close()
    
    def select_active_card(self):
        """Выбор активной карты"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, card_number FROM cards")
        cards = cursor.fetchall()
        
        if not cards:
            print("У вас нет карт. Создайте новую карту.")
            conn.close()
            return
        
        print("Доступные карты:")
        for card in cards:
            active_mark = " ✓" if card[0] == self.active_card_id else ""
            print(f"{card[0]}. {card[1]}{active_mark}")
        
        try:
            card_id = int(input("\nВведите ID карты для активации: "))
            
            # Проверяем существование карты
            cursor.execute("SELECT id FROM cards WHERE id = ?", (card_id,))
            if cursor.fetchone():
                # Сбрасываем все флаги активных карт
                cursor.execute("UPDATE cards SET is_active = 0")
                # Устанавливаем новую активную карту
                cursor.execute("UPDATE cards SET is_active = 1 WHERE id = ?", (card_id,))
                conn.commit()
                self.active_card_id = card_id
                print(f"Карта ID {card_id} теперь активна!")
            else:
                print("Карта с таким ID не найдена.")
        
        except ValueError:
            print("Введите корректный ID карты (число).")
        
        conn.close()
    
    def get_active_card_info(self):
        """Получение информации об активной карте"""
        if not self.active_card_id:
            return None
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT card_number, pin_code, balance FROM cards WHERE id = ?", 
                      (self.active_card_id,))
        card_info = cursor.fetchone()
        
        conn.close()
        return card_info
    
    def generate_card_number(self):
        """Генерация номера карты"""
        chars = string.digits + string.ascii_uppercase
        num = ''.join(random.choices(chars, k=16))
        return f"{num[0:4]}-{num[4:8]}-{num[8:12]}-{num[12:16]}"
    
    def create_new_card(self):
        """Создание новой карты"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Генерируем уникальный номер карты
        while True:
            card_number = self.generate_card_number()
            cursor.execute("SELECT id FROM cards WHERE card_number = ?", (card_number,))
            if not cursor.fetchone():
                break
        
        # Запрашиваем PIN-код
        while True:
            pin_code = input("Введите PIN-код (4 цифры): ").strip()
            if len(pin_code) == 4 and pin_code.isdigit():
                break
            print("PIN-код должен содержать ровно 4 цифры!")
        
        # Вставляем новую карту
        cursor.execute('''
            INSERT INTO cards (card_number, pin_code, balance, is_active)
            VALUES (?, ?, 0, 0)
        ''', (card_number, pin_code))
        
        conn.commit()
        card_id = cursor.lastrowid
        
        # Если это первая карта, делаем её активной
        if card_id == 1:
            cursor.execute("UPDATE cards SET is_active = 1 WHERE id = ?", (card_id,))
            self.active_card_id = card_id
            conn.commit()
        
        conn.close()
        return card_id
    
    def show_all_cards(self):
        """Показать все карты"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, card_number, balance FROM cards ORDER BY id")
        cards = cursor.fetchall()
        
        if not cards:
            print("У вас нет карт.")
        else:
            for card in cards:
                active_mark = " (активная)" if card[0] == self.active_card_id else ""
                print(f"ID: {card[0]}, Карта: {card[1]}, Баланс: {card[2]} руб.{active_mark}")
        
        conn.close()
    
    def check_balance(self):
        """Проверка баланса активной карты"""
        card_info = self.get_active_card_info()
        
        if not card_info:
            print("Нет активной карты. Выберите карту в меню (пункт 7).")
            return
        
        card_number, pin_code, balance = card_info
        
        print(f"Ваша карта: {card_number}")
        entered_pin = input("Введите PIN-код: ").strip()
        
        if entered_pin == pin_code:
            print(f"Баланс карты: {balance} руб.")
            
            # Показываем последние операции
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT operation_type, amount, timestamp 
                FROM transactions 
                WHERE card_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''', (self.active_card_id,))
            
            transactions = cursor.fetchall()
            if transactions:
                print("\nПоследние операции:")
                for trans in transactions:
                    sign = "+" if trans[0] == 'deposit' else "-"
                    print(f"  {trans[2]}: {sign}{trans[1]} руб. ({trans[0]})")
            
            conn.close()
        else:
            print("Неверный PIN-код!")
    
    def deposit_money(self):
        """Пополнение счета активной карты"""
        card_info = self.get_active_card_info()
        
        if not card_info:
            print("Нет активной карты. Выберите карту в меню (пункт 7).")
            return
        
        card_number, pin_code, balance = card_info
        
        print(f"Ваша карта: {card_number}")
        print(f"Текущий баланс: {balance} руб.")
        entered_pin = input("Введите PIN-код: ").strip()
        
        if entered_pin != pin_code:
            print("Неверный PIN-код!")
            return
        
        try:
            amount = int(input("Введите сумму для пополнения (до 50000 руб.): "))
            
            if amount < 0:
                print("Сумма должна быть положительной!")
                return

            
            # Анимация загрузки
            self.show_loading_animation()
            
            # Обновляем баланс в базе данных
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            new_balance = balance + amount
            cursor.execute("UPDATE cards SET balance = ? WHERE id = ?", 
                         (new_balance, self.active_card_id))
            
            # Записываем транзакцию
            cursor.execute('''
                INSERT INTO transactions (card_id, operation_type, amount)
                VALUES (?, 'deposit', ?)
            ''', (self.active_card_id, amount))
            
            conn.commit()
            conn.close()
            
            print(f"\nСчет пополнен на {amount} руб.")
            print(f"Новый баланс: {new_balance} руб.")
            
        except ValueError:
            print("Введите корректную сумму (число).")
    
    def show_loading_animation(self):
        """Анимация загрузки"""
        for i in range(3):
            print("Обработка" + "." * (i % 3 + 1))
            time.sleep(0.5)
            self.clear_screen()
    
    def pin_manager(self):
        """Управление PIN-кодом"""
        card_info = self.get_active_card_info()
        
        if not card_info:
            print("Нет активной карты. Выберите карту в меню (пункт 7).")
            return
        
        card_number, old_pin, _ = card_info
        
        print(f"Управление PIN-кодом для карты: {card_number}")
        
        entered_pin = input("Введите текущий PIN-код: ").strip()
        
        if entered_pin != old_pin:
            print("Неверный PIN-код!")
            return
        
        while True:
            new_pin = input("Введите новый PIN-код (4 цифры): ").strip()
            
            if len(new_pin) == 4 and new_pin.isdigit():
                # Обновляем PIN в базе данных
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                
                cursor.execute("UPDATE cards SET pin_code = ? WHERE id = ?", 
                             (new_pin, self.active_card_id))
                conn.commit()
                conn.close()
                
                print("PIN-код успешно изменен!")
                break
            else:
                print("PIN-код должен содержать ровно 4 цифры!")
    
    def close_database(self):
        """Закрытие соединения с базой данных (формальность для SQLite)"""
        print("База данных сохранена.")
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')