import easygui
import pyperclip
from pages_parser import ProductLinksParser

def run_parser_gui():
    try:
        clipboard_url = pyperclip.paste()
        if not clipboard_url.startswith("http"):
            clipboard_url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/"
    except Exception:
        clipboard_url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/"

    msg = "Введите параметры для парсинга страницы продуктов:"
    title = "Настройка парсера DNS"
    field_names = ["URL каталога",
                   "Имя выходного файла (с .txt)",
                   "Начальный индекс продукта",
                   "Конечный индекс продукта"]
    field_values = easygui.multenterbox(msg, title, field_names,
                                        [clipboard_url,
                                         "product_links.txt",
                                         "0",
                                         "30"])

    if field_values:
        try:
            url = field_values[0]
            output_file = field_values[1]
            start_index = int(field_values[2])
            end_index = int(field_values[3]) if field_values[3] else None

            parser = ProductLinksParser()
            logs = []

            def log_collector(message):
                logs.append(message)

            parser.parse_products_page(
                url,
                output_file=output_file,
                start_index=start_index,
                end_index=end_index,
                notify_callback=log_collector
            )
            parser.close()

            easygui.textbox("Результат парсинга:", "Парсинг завершен", "\n".join(logs))
        except Exception as e:
            easygui.exceptionbox(f"Произошла ошибка: {e}", title="Ошибка")

if __name__ == "__main__":
    run_parser_gui()
