from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
import os
import re
import shutil
import time



def unvalid_url(unvalid_list):
    with open("unvalid.txt", "w") as file:
        print(unvalid_list, file=file, sep="\n")
def process_pdf_files(folder_path):
    downloads_path = os.path.join(folder_path, "downloads")

    # Проверяем, что папка "downloads" существует
    if not os.path.exists(downloads_path):
        print(f"Папка {downloads_path} не существует.")
        return

    # Получаем список всех файлов в папке "downloads"
    file_list = os.listdir(downloads_path)

    # Проходимся по каждому файлу
    for file_name in file_list:
        file_path = os.path.join(downloads_path, file_name)

        # Проверяем, что файл имеет расширение PDF
        if file_name.lower().endswith('.pdf'):
            # Разделяем имя файла по символу подчеркивания
            parts = file_name.split('_')

            # Проверяем, что у нас есть достаточно элементов после разделения
            if len(parts) > 3:
                # Получаем цифры из третьего элемента
                folder_name = parts[2]

                # Создаем папку внутри "downloads"
                folder_path_new = os.path.join(downloads_path, folder_name)
                if not os.path.exists(folder_path_new):
                    os.makedirs(folder_path_new)

                # Перемещаем файл в созданную папку
                new_file_path = os.path.join(folder_path_new, file_name)
                shutil.move(file_path, new_file_path)

                print(f"Файл {file_name} перемещен в папку {folder_name}.")
            else:
                # Получаем цифры из второго элемента
                folder_name = parts[1]

                # Создаем папку внутри "downloads"
                folder_path_new = os.path.join(downloads_path, folder_name)
                if not os.path.exists(folder_path_new):
                    os.makedirs(folder_path_new)

                # Перемещаем файл в созданную папку
                new_file_path = os.path.join(folder_path_new, file_name)
                shutil.move(file_path, new_file_path)

                print(f"Файл {file_name} перемещен в папку {folder_name}.")

    print("Обработка файлов завершена.")


def get_data(url_list):
    unvalid_list = []
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    os.makedirs(data_folder, exist_ok=True)
    chrome_options = Options()
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    chrome_options.add_argument('--headless')

    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "download.default_directory": data_folder
    })
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    for url in url_list:
        driver.get(url)
        # time.sleep(1.5)


        # Ожидание загрузки элемента "Протокол итогов"
        protocol_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".m-dropdown__header button")))
        protocol_button.click()

        # Ожидание загрузки элемента "Скачать"
        try:
            download_link = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "Протокол итогов")))
            download_link.click()
        except Exception:
            try:
                download_link = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.LINK_TEXT, "Протокол итогов переговоров")))
                download_link.click()
            except Exception:
                print("Протокол отсутствует!")
                close_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".m-modal__close-button a")))
                close_button.click()
                unvalid_list.append(url)
                continue

        # Ожидание загрузки кнопки "Закрыть"
        close_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".m-modal__close-button a")))
        close_button.click()
    time.sleep(10)
    unvalid_url(unvalid_list)


def main():
    url_list = []
    with open('urls.txt', 'r') as file:
        for line in file:
            line = line.strip()
            url_list.append(line)

    # Разделение списка ссылок на 5 частей
    chunk_size = len(url_list) // 5
    url_chunks = [url_list[i:i + chunk_size] for i in range(0, len(url_list), chunk_size)]

    # Создание ThreadPoolExecutor с 5 потоками
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Запуск парсера для каждой части ссылок
        for chunk in url_chunks:
            executor.submit(get_data, chunk)

    folder_path = './'
    process_pdf_files(folder_path)


if __name__ == '__main__':
    main()

