import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import time
import os
import json

class ProductParser:
    def __init__(self, images_dir=None):
        # Настройки драйвера
        self.options = uc.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--lang=ru-RU')
        self.options.add_argument('--window-size=1920,1080')
        self.options.page_load_strategy = 'none'
        
        self.driver = uc.Chrome(options=self.options)
        self.start_time = None
        self.product_data = {
            'name': None,
            'price': None,
            'image_url': None,
            'image_path': None,
            'specs': {}
        }

        if images_dir is None:
            self.images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        else:
            self.images_dir = images_dir

        os.makedirs(self.images_dir, exist_ok=True)

    def parse_product(self, url):
        """Основной метод для парсинга страницы товара"""
        self.start_time = time.time()
        print(f"Начинаем парсинг товара по URL: {url}")
        
        try:
            self._load_page(url)
            self._get_product_name()
            self._get_product_price()
            self._get_product_image()
            self._expand_specifications()
            self._get_specifications()

            # Сохраняем результат после парсинга
            self._save_output_to_file(url)
            
            return self.product_data
            
        except Exception as e:
            print(f"Ошибка при парсинге товара: {e}")
            return None
        
        finally:
            self._close_driver()

    def _load_page(self, url):
        print("Загружаем страницу товара...")
        self.driver.get(url)
        time.sleep(2)

    def _get_product_name(self):
        print("Ищем название продукта...")
        try:
            name_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-card-top__title'))
            )
            self.product_data['name'] = name_elem.text.strip()
            print(f"Найдено название: {self.product_data['name']}")
        except TimeoutException:
            print("Название продукта не найдено")

    def _get_product_price(self):
        print("Ищем цену товара...")
        try:
            price_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-buy__price'))
            )
            self.product_data['price'] = price_elem.text.strip()
            print(f"Найдена цена: {self.product_data['price']}")
        except TimeoutException:
            print("Цена товара не найдена")

    def _get_product_image(self):
        print("Ищем изображение товара...")
        try:
            img_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img.product-images-slider__img'))
            )
            img_src = img_elem.get_attribute('src')
            self.product_data['image_url'] = img_src
            print(f"Найдена картинка: {img_src}")

            if img_src:
                img_response = requests.get(img_src)
                if img_response.status_code == 200:
                    if self.product_data['name']:
                        filename = self._sanitize_filename(self.product_data['name']) + '.jpg'
                    else:
                        filename = os.path.basename(self.driver.current_url.rstrip('/')) + '.jpg'
                    
                    image_path = os.path.join(self.images_dir, filename)
                    
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    self.product_data['image_path'] = image_path
                    print(f"Изображение сохранено в: {image_path}")
                else:
                    print("Ошибка загрузки изображения")
        except TimeoutException:
            print("Изображение товара не найдено")

    def _sanitize_filename(self, filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:100]

    def _expand_specifications(self):
        print("Раскрываем характеристики...")
        try:
            WebDriverWait(self.driver, 20, poll_frequency=0.1).until(
                lambda d: (
                    d.find_element(By.CSS_SELECTOR, 'button.product-characteristics__expand').is_displayed()
                    if d.find_elements(By.CSS_SELECTOR, 'button.product-characteristics__expand')
                    else (d.execute_script("window.scrollBy(0, 1000); return false;"))
                )
            )

            expand_button = self.driver.find_element(By.CSS_SELECTOR, 'button.product-characteristics__expand')
            self.driver.execute_script("arguments[0].click();", expand_button)
            print("Характеристики раскрыты")
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            try:
                WebDriverWait(self.driver, 5, poll_frequency=0.2).until(
                    lambda d: d.execute_script("return document.body.scrollHeight") > last_height
                )
            except TimeoutException:
                pass

        except TimeoutException:
            print("Не удалось раскрыть характеристики")

    def _get_specifications(self):
        print("Собираем характеристики...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-characteristics__group'))
            )
            
            spec_groups = self.driver.find_elements(By.CLASS_NAME, 'product-characteristics__group')
            
            for group in spec_groups:
                try:
                    group_title_elem = group.find_element(By.CLASS_NAME, 'product-characteristics__group-title')
                    group_title = group_title_elem.text.strip() if group_title_elem else 'Без названия'
                    
                    group_specs = {}
                    spec_items = group.find_elements(By.CLASS_NAME, 'product-characteristics__spec')
                    
                    for item in spec_items:
                        try:
                            title = item.find_element(
                                By.CLASS_NAME, 'product-characteristics__spec-title-content'
                            ).text.strip()
                            value = item.find_element(
                                By.CLASS_NAME, 'product-characteristics__spec-value'
                            ).text.strip()
                            group_specs[title] = value
                        except Exception:
                            continue
                    
                    self.product_data['specs'][group_title] = group_specs
                    
                except Exception:
                    continue
            
            print("Характеристики собраны")
            
        except TimeoutException:
            print("Характеристики не найдены")

    def _save_output_to_file(self, url):
        """Сохраняет результат парсинга в файл в виде JSON-строки"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_dir, 'parsed_products.jsonl')

            product_id = url.strip('/').split('/')[-1]

            output_data = {
                'id': product_id,
                'name': self.product_data.get('name'),
                'price': self.product_data.get('price'),
                'image_url': self.product_data.get('image_url'),
                'image_path': self.product_data.get('image_path'),
                'specs': self.product_data.get('specs')
            }

            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(output_data, ensure_ascii=False) + '\n')

            print(f"Результаты сохранены в файл: {output_file}")

        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")

    def _close_driver(self):
        if self.driver:
            self.driver.quit()
            print("Браузер закрыт.")
        
        if self.start_time:
            end_time = time.time()
            print(f"Время выполнения: {end_time - self.start_time:.2f} сек.")
