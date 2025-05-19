import subprocess

def main():
    table_name = input("Введите имя таблицы для удаления: ").strip()
    if not table_name:
        print("Имя таблицы не может быть пустым.")
        return

    try:
        # Формируем SQL для удаления таблицы из схемы pc_components
        sql_commands = f"""
        \\c mydb
        DROP TABLE IF EXISTS "pc_components"."{table_name}";
        \\q
        """

        print(f"[INFO] Удаление таблицы pc_components.{table_name} из базы данных mydb...")
        subprocess.run(
            ['sudo', '-u', 'postgres', 'psql'],
            input=sql_commands,
            text=True,
            check=True
        )

        print(f"[SUCCESS] Таблица pc_components.{table_name} успешно удалена (если существовала).")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при выполнении команды: {e}")

if __name__ == "__main__":
    main()
