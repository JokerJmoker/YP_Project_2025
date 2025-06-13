import json
import easygui
from pathlib import Path

def extract_data_from_jsonl():
    # 1. Выбор файла через проводник
    file_path = easygui.fileopenbox(
        title="Выберите JSONL файл",
        default="*.jsonl",
        filetypes=["*.jsonl", "*.txt"]
    )
    
    if not file_path:
        return
    
    # 2. Запрос имени тега
    tag_name = easygui.enterbox(
        msg="Введите имя тега для извлечения (например 'name'):",
        title="Имя тега",
        default="name"
    )
    
    if not tag_name:
        easygui.msgbox("Имя тега не может быть пустым", "Ошибка")
        return
    
    # 3. Чтение и обработка файла
    extracted_data = []
    line_count = 0
    error_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                try:
                    data = json.loads(line)
                    if tag_name in data:
                        extracted_data.append(data[tag_name])
                except json.JSONDecodeError:
                    error_count += 1
                    continue
        
        # 4. Сохранение результата
        input_path = Path(file_path)
        output_path = input_path.with_name(f"{input_path.stem}_{tag_name}_extracted.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
        # 5. Отчет о результатах
        easygui.msgbox(
            f"Успешно обработано {line_count} строк\n"
            f"Найдено ошибок: {error_count}\n"
            f"Извлечено значений: {len(extracted_data)}\n\n"
            f"Результат сохранен в:\n{output_path}",
            title="Готово"
        )
    
    except Exception as e:
        easygui.exceptionbox(
            f"Произошла ошибка при обработке файла:\n{str(e)}",
            "Ошибка"
        )

if __name__ == "__main__":
    extract_data_from_jsonl()