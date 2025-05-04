import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class ProductLinksParser:
    def __init__(self):
        self.options = uc.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--lang=ru-RU')
        self.options.add_argument('--window-size=1920,1080')
        self.options.page_load_strategy = 'none'
        
        self.driver = uc.Chrome(options=self.options)
        self.base_url = 'https://www.dns-shop.ru'
    
    def parse_products_page(self, url, 
                            max_scroll_attempts=50, 
                            output_file='product_links.txt',
                            start_index=0,
                            end_index=None,
                            notify_callback=None):
        """
        Основной метод парсинга.
        :param notify_callback: функция для логов (например для GUI)
        """
        start_time = time.time()  # Старт замера времени

        self._log(notify_callback, f"Загружаем страницу с продуктами: {url}")
        self.driver.get(url)
        time.sleep(3)
        
        product_links = []
        processed_links = set()
        scroll_attempt = 0
        no_new_items_count = 0
        no_new_items_limit = 1  # остановка после 3х пустых циклов

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.catalog-product__name-wrapper'))
        )

        while scroll_attempt < max_scroll_attempts:
            new_links_found = False

            # Обновляем список всех найденных товаров
            current_products = self.driver.find_elements(
                By.CSS_SELECTOR, 'div.catalog-product__name-wrapper > a.catalog-product__name'
            )

            for element in current_products[len(product_links):]:
                try:
                    href = element.get_attribute('href')
                    if href and href not in processed_links:
                        if not href.startswith('http'):
                            href = self.base_url + href
                        processed_links.add(href)

                        current_index = len(product_links)
                        
                        if current_index < start_index:
                            product_links.append(href)
                            continue
                        if end_index is not None and current_index >= end_index:
                            self._save_to_file(product_links, output_file, notify_callback)
                            total_time = time.time() - start_time
                            self._log(notify_callback, f"Достигнут end_index {end_index}. Завершение. Время выполнения: {total_time:.2f} сек.")
                            return product_links

                        product_links.append(href)
                        new_links_found = True
                        self._log(notify_callback, f"[{current_index}] Найдена ссылка: {href}")
                except Exception as e:
                    self._log(notify_callback, f"Ошибка при обработке элемента: {e}")

            total_links_count = len(product_links)
            self._log(notify_callback, f"Всего собрали: {total_links_count} ссылок")

            if total_links_count < start_index:
                self._log(notify_callback, f"Достигаем start_index ({start_index}), продолжаем подгрузку...")
            else:
                if not new_links_found:
                    no_new_items_count += 1
                    self._log(notify_callback, f"Нет новых элементов при скролле (попытка {no_new_items_count}/{no_new_items_limit})")
                else:
                    no_new_items_count = 0

                if no_new_items_count >= no_new_items_limit:
                    self._log(notify_callback, "Новых элементов больше нет. Завершение парсинга.")
                    break

            # Скроллим для поиска кнопки 'Показать еще'
            self._log(notify_callback, "Скроллим для поиска кнопки 'Показать еще'...")
            scroll_step = 500
            inner_scrolls = 0
            max_inner_scrolls = 20  # оставить как было

            found_show_more = False
            while not found_show_more and inner_scrolls < max_inner_scrolls:
                try:
                    show_more_button = self.driver.find_element(
                        By.CSS_SELECTOR, 'button.pagination-widget__show-more-btn'
                    )
                    if show_more_button.is_displayed():
                        found_show_more = True
                        show_more_button.click()
                        self._log(notify_callback, "Нажата кнопка 'Показать еще'")
                        time.sleep(2)
                        break
                except:
                    pass

                self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                inner_scrolls += 1
                time.sleep(0.5)

            if not found_show_more:
                self._log(notify_callback, "Кнопка 'Показать еще' не найдена после скролла.")

            scroll_attempt += 1

        # Финальная проверка
        if end_index is not None and len(product_links) < end_index:
            self._log(
                notify_callback,
                f"Внимание: всего найдено {len(product_links)} элементов, меньше чем запрошено (end_index={end_index}). Завершаем."
            )

        self._save_to_file(product_links, output_file, notify_callback)
        total_time = time.time() - start_time  # Конец замера времени
        self._log(notify_callback, f"Парсинг завершён. Время выполнения: {total_time:.2f} сек.")
        return product_links
            
    def _save_to_file(self, links, filename, notify_callback=None):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(link + '\n')
            self._log(notify_callback, f"Ссылки успешно сохранены в файл: {file_path}")
        except Exception as e:
            self._log(notify_callback, f"Ошибка при сохранении файла: {e}")
    
    def _log(self, callback, message):
        print(message)
        if callback:
            callback(message)
    
    def close(self):
        self.driver.quit()
