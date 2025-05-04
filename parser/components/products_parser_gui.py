import easygui
import pyperclip
import os
import json
from products_parser import ProductParser

def run_product_parser_gui():
    title = "Парсер товаров DNS"

    # Запрашиваем имя выходного файла и папки с изображениями
    fields = ["Имя выходного файла (с .jsonl)", "Папка для сохранения изображений"]
    defaults = ["parsed_products.jsonl", "images"]
    vals = easygui.multenterbox("Введите параметры парсинга:", title, fields, defaults)
    if not vals:
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, vals[0])
    images_dir = os.path.join(script_dir, vals[1])

    if not os.path.exists(images_dir):
        os.makedirs(images_dir, exist_ok=True)

    # Кнопка для выбора файла с ссылками
    clip = pyperclip.paste()
    msg = "Выберите файл с ссылками." + (f"\n(Буфер: {clip[:50]}...)" if clip else "")
    while True:
        if easygui.buttonbox(msg, title, ["Выбрать файл", "Отмена"]) != "Выбрать файл":
            return
        links_file = easygui.fileopenbox("Файл с URL-адресами:", title, default="*.txt")
        if links_file:
            break

    try:
        with open(links_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            easygui.msgbox("Файл пуст.", title="Ошибка")
            return

        logs = []
        for idx, url in enumerate(urls, 1):
            logs.append(f"[{idx}] {url}")
            parser = ProductParser(images_dir=images_dir)
            data = parser.parse_product(url)
            if data:
                with open(output_file, 'a', encoding='utf-8') as out:
                    json.dump(data, out, ensure_ascii=False)
                    out.write('\n')
                logs.append(f"{data.get('name', 'Без названия')} - {data.get('price')}")
            else:
                logs.append("Ошибка парсинга")

        easygui.textbox("Результаты:", title, "\n".join(logs))
    except Exception as e:
        easygui.exceptionbox(f"Ошибка: {e}", title)

if __name__ == "__main__":
    run_product_parser_gui()
