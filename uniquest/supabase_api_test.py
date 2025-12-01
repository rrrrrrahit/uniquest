import os
from supabase import create_client, Client

# --- ТВОИ ДАННЫЕ SUPABASE ---
SUPABASE_URL = "https://fcnnggrxrepzzkpbnsqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjbm5nZ3J4cmVwenprcGJuc3FyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2MDIxODgsImV4cCI6MjA4MDE3ODE4OH0.opKrZNkxKGn0hdSJ1hb2D3seRZTE3v_8McoDmWpcNzI"

# Создаем объект клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ТАБЛИЦЫ ---
TABLES = ["students", "teachers", "courses", "grades"]

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ТАБЛИЦАМИ ---
def get_all(table_name):
    response = supabase.table(table_name).select("*").execute()
    if response.data:
        print(f"\nВсе записи из {table_name}:")
        for row in response.data:
            print(row)
    else:
        print(f"{table_name} пусто или ошибка:", response)

def add_record(table_name, data):
    response = supabase.table(table_name).insert(data).execute()
    if response.data:
        print(f"Запись добавлена в {table_name}:", response.data)
    else:
        print("Ошибка при добавлении:", response)

def update_record(table_name, record_id, **kwargs):
    response = supabase.table(table_name).update(kwargs).eq("id", record_id).execute()
    if response.data:
        print(f"Запись в {table_name} обновлена:", response.data)
    else:
        print("Ошибка при обновлении:", response)

def delete_record(table_name, record_id):
    response = supabase.table(table_name).delete().eq("id", record_id).execute()
    if response.data:
        print(f"Запись из {table_name} удалена:", response.data)
    else:
        print("Ошибка при удалении:", response)

# --- МЕНЮ ДЛЯ КОНСОЛИ ---
def menu():
    while True:
        print("\n--- SUPABASE API TEST ---")
        print("Выберите таблицу:")
        for i, table in enumerate(TABLES, 1):
            print(f"{i}. {table}")
        print("0. Выход")

        choice = input("Введите номер: ")
        if choice == "0":
            break

        if choice.isdigit() and 1 <= int(choice) <= len(TABLES):
            table_name = TABLES[int(choice) - 1]
        else:
            print("Неверный выбор")
            continue

        print(f"\nВыбрана таблица: {table_name}")
        print("1. Посмотреть все записи")
        print("2. Добавить запись")
        print("3. Обновить запись")
        print("4. Удалить запись")
        action = input("Введите номер действия: ")

        if action == "1":
            get_all(table_name)

        elif action == "2":
            data = {}
            print("Введите данные в формате ключ=значение. Для окончания оставьте пустую строку.")
            while True:
                entry = input()
                if entry == "":
                    break
                if "=" in entry:
                    key, value = entry.split("=", 1)
                    data[key.strip()] = value.strip()
            add_record(table_name, data)

        elif action == "3":
            record_id = input("Введите ID записи для обновления: ")
            updates = {}
            print("Введите данные для обновления в формате ключ=значение. Для окончания оставьте пустую строку.")
            while True:
                entry = input()
                if entry == "":
                    break
                if "=" in entry:
                    key, value = entry.split("=", 1)
                    updates[key.strip()] = value.strip()
            update_record(table_name, record_id, **updates)

        elif action == "4":
            record_id = input("Введите ID записи для удаления: ")
            delete_record(table_name, record_id)

        else:
            print("Неверное действие")

if __name__ == "__main__":
    menu()
