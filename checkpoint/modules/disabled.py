from pathlib import Path
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from checkpoint import globals as gb
from checkpoint.helpers.pages import check_page, load_allowed_pages, save_allowed_pages
from checkpoint.helpers.email import *
from checkpoint.knowledge import fs
from checkpoint.modules import login


async def run(driver: WebDriver = None, download_path: str = None):
    gb.rc.print("\n🗺️ Disabled account page", style="green4")

    # Отправляем уведомление о запуске модуля
    send_module_start_notification("gsu1234@mail.ru", "Disabled Account Page")

    # Настройка папки для скачивания
    if download_path is None:
        download_path = fs.path['download_path']

    download_folder = Path(download_path)

    # Проверяем, существует ли указанная папка
    if not download_folder.exists():
        gb.rc.print(f"❌ Папка {download_folder} недоступна!", style="red")
        return False
    
    gb.rc.print(f"📁 Файлы будут сохраняться в: {download_folder}", style="blue")
    
    # Загружаем allowed_pages из JSON файла или используем значения по умолчанию
    allowed_pages = load_allowed_pages()

    while True:

        if 'disabled_account' in allowed_pages and check_page(driver, 'disabled_account'):
            button = driver.find_element(By.XPATH, "//*[text()='Скачать информацию']")
            if button:
                button.click()

        if 'download_account' in allowed_pages and check_page(driver, 'download_account'):
            button = driver.find_element(By.XPATH, "//*[text()='Запросить файл']")
            if button:
                button.click()
                allowed_pages.append('download_ready')
                save_allowed_pages(allowed_pages)

        if 'creation_backup_is_processing' in allowed_pages and check_page(driver, 'creation_backup_is_processing'): #todo вывод в консоль текущего теста со страницы
            sleep(100)

        if 'login' in allowed_pages and check_page(driver, 'login'):
            import asyncio
            asyncio.run(login.check_and_login(driver))

        if 'download_ready' in allowed_pages and check_page(driver, 'download_ready'):
            # Поиск всех кнопок с текстом "Скачать * файлов из *"
            try:
                download_buttons = driver.find_elements(
                    By.XPATH, 
                    "//*[contains(text(), 'Скачать') and contains(text(), 'файлов из')]"
                )
                
                if download_buttons:
                    gb.rc.print(f"🔍 Найдено {len(download_buttons)} кнопок для скачивания", style="yellow")
                    
                    for i, button in enumerate(download_buttons, 1):
                        try:
                            button_text = button.text
                            gb.rc.print(f"📥 Нажимаем кнопку {i}: {button_text}", style="cyan")
                            
                            # Настройка Chrome для скачивания в указанную папку
                            driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                                'behavior': 'allow',
                                'downloadPath': str(download_folder)
                            })
                            
                            # Прокручиваем до кнопки и кликаем
                            driver.execute_script("arguments[0].scrollIntoView();", button)
                            sleep(1)
                            button.click()
                            
                            # Ждем начала скачивания
                            sleep(2)
                            gb.rc.print(f"✅ Кнопка {i} нажата, файл отправлен на скачивание", style="green")
                            
                        except Exception as e:
                            gb.rc.print(f"❌ Ошибка при нажатии кнопки {i}: {e}", style="red")
                            continue

                    allowed_pages.remove('download_ready')
                    save_allowed_pages(allowed_pages)

                    gb.rc.print(f"📊 Всего отправлено на скачивание: {len(download_buttons)} файлов", style="blue")

                    # Отправляем уведомление на email
                    send_download_completion_notification("gsu1234@mail.ru", len(download_buttons))

                    gb.rc.print("⏳ Ожидаем завершения всех скачиваний...", style="yellow")
                    gb.rc.print("😴 Пауза на 6 часов после завершения скачиваний...", style="magenta")
                    sleep(21600)  # 6 часов = 21600 секунд
                    gb.rc.print("⏰ Пауза завершена, продолжаем работу", style="green")


            except NoSuchElementException:
                pass


        driver.refresh()
