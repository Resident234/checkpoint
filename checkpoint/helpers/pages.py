import json
from pathlib import Path

from selenium.common import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from checkpoint import globals as gb
from checkpoint.helpers.utils import print_function_name
from checkpoint.knowledge import fs, pages

WAIT_TIMEOUT = 3


@print_function_name
def check_page(driver: WebDriver, page: str) -> str | bool:
    match page:
        case 'captcha': # страница запроса капчи
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Введите символы, которые вы видите']")))
            except WebDriverException:
                return False
            return True

        case 'index':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Ваш профиль']")))
            except WebDriverException:
                return False
            return True

        case 'login':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Недавние входы' or @name='login' or text()='Войти на Facebook']")))
            except WebDriverException:
                return False
            return True

        case 'two_step_verification':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве' or text()='Проверьте сообщения WhatsApp']")))
            except WebDriverException:
                return False
            return True

        case 'add_trusted_device':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве']")))
            except WebDriverException:
                return False
            return True

        case 'authorized':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Управление аккаунтом и его настройки']")))
            except WebDriverException:
                return False
            return True

        case 'disabled_account':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Мы отключили ваш аккаунт']")))
            except WebDriverException:
                return False
            return True

        case 'download_account':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Скачать информацию']")))
            except WebDriverException:
                return False
            return True

        case 'creation_backup_is_processing':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Мы создаем файл с вашей информацией']")))
            except WebDriverException:
                return False
            return True

        case 'download_ready':
            try:
                WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Файл с вашей информацией готов']")))
            except WebDriverException:
                return False
            return True

        case _:
            return False


def load_allowed_pages():
    """Загружает allowed_pages из JSON файла или возвращает значения по умолчанию"""
    json_file_path = Path(fs.files['allowed_pages_file'])
    
    if json_file_path.exists():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                allowed_pages = data.get('allowed_pages', pages.allowed_pages)
                gb.rc.print(f"📄 Загружены allowed_pages из файла: {allowed_pages}", style="cyan")
                return allowed_pages
        except (json.JSONDecodeError, KeyError) as e:
            gb.rc.print(f"⚠️ Ошибка при чтении файла allowed_pages: {e}", style="yellow")
            gb.rc.print(f"🔄 Используем значения по умолчанию", style="yellow")
            return pages.allowed_pages
    else:
        gb.rc.print(f"📄 Файл allowed_pages не найден, используем значения по умолчанию", style="yellow")
        return pages.allowed_pages


def save_allowed_pages(allowed_pages):
    """Сохраняет allowed_pages в JSON файл"""
    json_file_path = Path(fs.files['allowed_pages_file'])
    
    try:
        data = {'allowed_pages': allowed_pages}
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        gb.rc.print(f"💾 Сохранены allowed_pages в файл: {allowed_pages}", style="green")
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при сохранении allowed_pages: {e}", style="red")
