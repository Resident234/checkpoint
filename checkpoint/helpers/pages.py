from selenium.common import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from checkpoint.helpers.utils import print_function_name

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
