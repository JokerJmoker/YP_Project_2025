import subprocess

def main():
    table_name = input("Введите имя таблицы для очистки: ").strip()
    if not table_name:
        print("Имя таблицы не может быть пустым.")
        return

    try:
        # Формируем SQL для очистки таблицы в схеме pc_components
        sql_commands = f"""
        \\c mydb
        TRUNCATE TABLE "pc_components"."{table_name}";
        \\q
        """

        print(f"[INFO] Очистка таблицы pc_components.{table_name} в базе данных mydb...")
        subprocess.run(
            ['sudo', '-u', 'postgres', 'psql'],
            input=sql_commands,
            text=True,
            check=True
        )

        print(f"[SUCCESS] Таблица pc_components.{table_name} успешно очищена (все данные удалены).")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при выполнении команды: {e}")

if __name__ == "__main__":
    main()