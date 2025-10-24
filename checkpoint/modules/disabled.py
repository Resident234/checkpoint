from pathlib import Path

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from checkpoint import globals as gb
from checkpoint import config
from checkpoint.helpers.pages import check_page, load_allowed_pages, save_allowed_pages, get_page_title
from checkpoint.helpers.email import *
from checkpoint.helpers.popups import check_popup
from checkpoint.helpers.utils import sleep
from checkpoint.knowledge import fs, pauses
from checkpoint.knowledge.pages import urls
from checkpoint.modules import login
from checkpoint.objects.archive import ArchiveManager
from checkpoint.objects.media import MediaManager
from checkpoint.objects.stats import PhotoStatsManager
from checkpoint.objects.cleanup import CleanupManager

# Глобальные переменные для менеджеров
archive_manager = None
media_manager = None
stats_manager = None
cleanup_manager = None




def handle_download_ready(driver: WebDriver, download_folder: Path) -> None:
    """
    Обрабатывает страницу с готовыми для скачивания файлами
    
    Args:
        driver: WebDriver instance
        download_folder: Путь к папке для скачивания
    """
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
                    sleep(pauses.download['button_click'], "Пауза после прокрутки к кнопке")
                    button.click()
                    sleep(pauses.download['button_click'], "Пауза после клика по кнопке")
                    
                    # Ждем начала скачивания
                    sleep(pauses.download['download_start'], "Ожидание начала скачивания")
                    gb.rc.print(f"✅ Кнопка {i} нажата, файл отправлен на скачивание", style="green")
                    
                except Exception as e:
                    gb.rc.print(f"❌ Ошибка при нажатии кнопки {i}: {e}", style="red")
                    continue

            gb.rc.print(f"📊 Всего отправлено на скачивание: {len(download_buttons)} файлов", style="blue")

            # Отправляем уведомление на email
            send_download_completion_notification(config.NOTIFY_EMAIL, len(download_buttons))

            gb.rc.print("⏳ Ожидаем завершения всех скачиваний...", style="yellow")
            sleep(pauses.download['post_download'], "Пауза после завершения скачиваний")
            gb.rc.print("⏰ Пауза завершена, продолжаем работу", style="green")

    except NoSuchElementException:
        pass


async def run(driver: WebDriver = None, download_path: str = None, root_folder: str = None):
    # Устанавливаем имя текущего модуля
    gb.current_module_name = "disabled"
    
    gb.rc.print("\n🗺️ Disabled account page", style="green4")

    # Отправляем уведомление о запуске модуля
    send_module_start_notification(config.NOTIFY_EMAIL, "Disabled Account Page")

    # Настройка папки для скачивания
    if download_path is None:
        download_path = fs.path['download_path']

    if root_folder is None:
        root_folder = fs.path['root_folder']

    download_folder = Path(download_path)
    root_folder = Path(root_folder)

    # Проверяем, существует ли указанная папка
    if not download_folder.exists():
        gb.rc.print(f"❌ Папка {download_folder} недоступна!", style="red")
        return False
    
    gb.rc.print(f"📁 Файлы будут сохраняться в: {download_folder}", style="blue")
    
    # Инициализируем и запускаем менеджер архивов
    global archive_manager, media_manager, stats_manager, cleanup_manager
    archive_manager = ArchiveManager(download_folder)
    archive_manager.start_monitor()
    
    # Инициализируем и запускаем менеджер медиа
    media_path = download_folder / fs.path['facebook_media_subpath']
    gb.rc.print(f"📁 Медиа файлы будут перемещаться в: {root_folder}", style="blue")
    media_manager = MediaManager(media_path, root_folder)
    media_manager.start_monitor()
    
    # Инициализируем и запускаем менеджер статистики
    # Размещаем папку stats_logs в корне проекта (рядом с папкой logs)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # checkpoint/modules/disabled.py -> CheckPoint/
    stats_logs_path = project_root / fs.path['stats_logs_dir']
    stats_logs_path.mkdir(parents=True, exist_ok=True)
    gb.rc.print(f"📊 Логи статистики будут сохраняться в: {stats_logs_path}", style="blue")
    stats_manager = PhotoStatsManager(root_folder, stats_logs_path, send_email=True)
    stats_manager.start_monitor()
    
    # Инициализируем и запускаем менеджер очистки
    gb.rc.print(f"🧹 Мониторинг очистки файлов в: {download_folder}", style="blue")
    cleanup_manager = CleanupManager(download_folder)
    cleanup_manager.start_monitor()
    
    # Загружаем allowed_pages из JSON файла или используем значения по умолчанию
    allowed_pages = load_allowed_pages()

    try:
        while True:

            if 'disabled_account' in allowed_pages and check_page(driver, 'disabled_account'):
                get_page_title(driver)
                button = driver.find_element(By.XPATH, "//*[text()='Скачать информацию']")
                if button:
                    button.click()

            if 'download_account' in allowed_pages and check_page(driver, 'download_account'):
                get_page_title(driver)
                button = driver.find_element(By.XPATH, "//*[text()='Запросить файл']")
                if button:
                    button.click()
                    allowed_pages.append('download_ready')
                    save_allowed_pages(allowed_pages)

            if 'creation_backup_is_processing' in allowed_pages and check_page(driver, 'creation_backup_is_processing'):
                get_page_title(driver)
                sleep(pauses.download['backup_processing'], "Ожидание обработки бэкапа")

            if 'login' in allowed_pages and check_page(driver, 'login'):
                get_page_title(driver)
                await login.check_and_login(driver)

            #allowed_pages.remove('download_ready')
            #allowed_pages.append('download_ready')
            if 'download_ready' in allowed_pages and check_page(driver, 'download_ready'):
                get_page_title(driver)
                handle_download_ready(driver, download_folder)
                allowed_pages.remove('download_ready')
                save_allowed_pages(allowed_pages)

            # Проверка на истечение времени сеанса
            if check_popup(driver, "session_timeout"):
                gb.rc.print("🏠 Переходим на главную страницу из-за истечения сеанса", style="cyan")
                driver.get(urls["home"])
                continue

            driver.refresh()
            
    except KeyboardInterrupt:
        gb.rc.print("⚠️ Получен сигнал прерывания, завершаем работу...", style="yellow")
    except Exception as e:
        gb.rc.print(f"❌ Критическая ошибка в модуле disabled: {e}", style="red")
    finally:
        # Останавливаем мониторинг ZIP файлов при выходе
        if archive_manager:
            archive_manager.stop_monitor()
        
        # Останавливаем мониторинг медиа папок при выходе
        if media_manager:
            media_manager.stop_monitor()
        
        # Останавливаем мониторинг статистики при выходе
        if stats_manager:
            stats_manager.stop_monitor()
        
        # Останавливаем мониторинг очистки при выходе
        if cleanup_manager:
            cleanup_manager.stop_monitor()


