from logic import Main
import time
import os

m = Main()
m.clear_screen()

def main():
    while True:
        print("=== БАНКОВСКАЯ СИСТЕМА ===")
        print("1. Создать новую карту")
        print("2. Показать все карты")
        print("3. Проверить баланс")
        print("4. Пополнить счет")
        print("5. Поддержка")
        print("6. Установить/поменять пин код")
        print("7. Выбрать активную карту")
        print("8. Выход")
        print("=" * 25)
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            m.clear_screen()
            print("=== СОЗДАНИЕ НОВОЙ КАРТЫ ===")
            card_id = m.create_new_card()
            if card_id:
                print(f"Новая карта создана! ID карты: {card_id}")
            time.sleep(3)
            m.clear_screen()
            
        elif choice == "2":
            m.clear_screen()
            print("=== ВАШИ КАРТЫ ===")
            m.show_all_cards()
            time.sleep(5)
            m.clear_screen()
            
        elif choice == "3":
            m.clear_screen()
            print("=== ПРОВЕРКА БАЛАНСА ===")
            m.check_balance()
            time.sleep(4)
            m.clear_screen()
            
        elif choice == "4":
            m.clear_screen()
            print("=== ПОПОЛНЕНИЕ СЧЕТА ===")
            m.deposit_money()
            time.sleep(4)
            m.clear_screen()
            
        elif choice == "5":
            m.clear_screen()
            print("=== ПОДДЕРЖКА ===")
            print("Email: support@bank.com")
            print("Телефон: 8-800-555-35-35")
            time.sleep(4)
            m.clear_screen()
            
        elif choice == "6":
            m.clear_screen()
            print("=== УПРАВЛЕНИЕ PIN-КОДОМ ===")
            m.pin_manager()
            time.sleep(3)
            m.clear_screen()
            
        elif choice == "7":
            m.clear_screen()
            print("=== ВЫБОР АКТИВНОЙ КАРТЫ ===")
            m.select_active_card()
            time.sleep(3)
            m.clear_screen()
            
        elif choice == "8":
            print("Выход из программы...")
            m.close_database()
            break
            
        else:
            print("Неверный выбор!")
            time.sleep(2)
            m.clear_screen()

if __name__ == "__main__":
    main()