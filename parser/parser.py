import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import time
import os

# URL страницы
url = 'https://www.dns-shop.ru/product/5a7b4c6d0bc3c823/videokarta-msi-geforce-210-n210-1gd3lp/'

# Настройки драйвера
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--lang=ru-RU')
options.add_argument('--window-size=1920,1080')
options.page_load_strategy = 'none'  # НЕ ЖДАТЬ полной загрузки страницы

driver = uc.Chrome(options=options)

start_time = time.time()  # Старт замера времени

try:
    print("Загружаем страницу (без ожидания полной загрузки)...")
    driver.get(url)

    # Даём странице немного времени для первичной отрисовки
    time.sleep(2)

    # 🔥 --- БЛОК ПОИСКА И КОПИРОВАНИЯ КАРТИНКИ ---
    print("Ожидаем появления изображения товара...")
    try:
        img_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img.product-images-slider__img'))
        )
        img_src = img_elem.get_attribute('src')
        print(f"Найдена картинка: {img_src}")

        # Копируем картинку локально
        img_response = requests.get(img_src)
        if img_response.status_code == 200:
            with open("product_image.jpg", 'wb') as f:
                f.write(img_response.content)
            print("Изображение сохранено как product_image.jpg")
        else:
            print(f"Ошибка загрузки изображения: статус {img_response.status_code}")

    except TimeoutException:
        print("Изображение товара не найдено после тайм-аута.")

    # 🔥 --- ОСТАЛЬНАЯ ЛОГИКА, КАК БЫЛО ---

    print("Ожидаем появления кнопки 'Развернуть все'...")
    try:
        WebDriverWait(driver, 20, poll_frequency=0.1).until(
            lambda d: (
                d.find_element(By.CSS_SELECTOR, 'button.product-characteristics__expand').is_displayed()
                if d.find_elements(By.CSS_SELECTOR, 'button.product-characteristics__expand')
                else (d.execute_script("window.scrollBy(0, 1000); return false;"))
            )
        )

        print("Найдена кнопка 'Развернуть все'!")
        print("Найдена кнопка 'Развернуть все'!")
        expand_button = driver.find_element(By.CSS_SELECTOR, 'button.product-characteristics__expand')
        driver.execute_script("arguments[0].click();", expand_button)  # <-- заменили на JS-клик
        #expand_button.click()
        print("Кнопка нажата.")

    except TimeoutException:
        print("Кнопка 'Развернуть все' не найдена после тайм-аута.")

    # Скроллим до конца страницы и ждём полной подгрузки
    print("Скроллим до конца страницы и ждём полной подгрузки...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        WebDriverWait(driver, 5, poll_frequency=0.2).until(
            lambda d: d.execute_script("return document.body.scrollHeight") > last_height
        )
    except TimeoutException:
        pass

    print("Достигнут конец страницы.")

    # Скриншот для проверки
    driver.save_screenshot("debug_screen_uc.png")
    print("Скриншот сохранён как debug_screen_uc.png")

    # Ждём появления блока характеристик
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-characteristics__group')))
    print("Найден блок характеристик!")

    spec_groups = driver.find_elements(By.CLASS_NAME, 'product-characteristics__group')

    for group in spec_groups:
        try:
            group_title_elem = group.find_element(By.CLASS_NAME, 'product-characteristics__group-title')
            group_title = group_title_elem.text.strip() if group_title_elem else 'Без названия группы'
            print(f"\n{group_title}")

            spec_items = group.find_elements(By.CLASS_NAME, 'product-characteristics__spec')
            for item in spec_items:
                title_elem = item.find_element(By.CLASS_NAME, 'product-characteristics__spec-title-content')
                value_elem = item.find_element(By.CLASS_NAME, 'product-characteristics__spec-value')

                title = title_elem.text.strip() if title_elem else 'N/A'
                value = value_elem.text.strip() if value_elem else 'N/A'
                print(f'{title}: {value}')
        except Exception as e:
            print(f"Пропущен элемент из-за ошибки: {e}")

except Exception as e:
    print(f"Ошибка: {e}")

finally:
    driver.quit()
    end_time = time.time()  # Конец замера времени
    print("Браузер закрыт.")
    print(f"Общее время выполнения: {end_time - start_time:.2f} сек.")
