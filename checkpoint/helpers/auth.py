import sys
import json
import re
import threading
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from checkpoint import config
from checkpoint.errors import *
from checkpoint.helpers.temp_dir import get_temp_path
from checkpoint.helpers.captha import *
from checkpoint.helpers.pages import *
from checkpoint.helpers.utils import *
from checkpoint.knowledge import external, fs, pauses, retries
from checkpoint.knowledge.pages import urls
from checkpoint.objects.base import CheckPointCreds, Inp

# XPath селекторы для двухфакторной аутентификации
VERIFICATION_CODE_INPUT_XPATH = "//input[@type='text']"
VERIFICATION_SUBMIT_BUTTON_XPATH = "//*[text()='Продолжить']"


@print_function_name
async def check_cookies(driver: WebDriver, cookies) -> bool:
    """Checks the validity of given cookies."""
    driver.get(urls["home"])

    if check_page(driver, 'index') or check_page(driver, 'authorized'):
        return True

    if not cookies:
        return False

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.refresh()

    return check_page(driver, 'index') or check_page(driver, 'authorized')

@print_function_name
async def gen_cookies(driver: WebDriver, checkpoint_creds: CheckPointCreds):
    driver.get(urls["home"])

    loop_counter = 0
    while True:
        loop_counter += 1

        if loop_counter > 2:
            driver.refresh()
            loop_counter = 0

        if check_page(driver, 'login'):
            login(driver, config.USER_NAME, config.PASSWORD)
        if check_page(driver, 'captcha'):
            solve_captcha(driver)
        if check_page(driver, 'two_step_verification'):
            two_step_verification_wait(driver)
        if check_page(driver, 'add_trusted_device'):
            add_trusted_device(driver)
        if check_page(driver, 'index'):
            break
        if check_page(driver, 'authorized'):
            break

    checkpoint_creds.cookies = driver.get_cookies()

@print_function_name
async def check_and_gen(driver: WebDriver, checkpoint_creds: CheckPointCreds, renew: bool = False):
    """Checks the validity of the cookies and generate new ones if needed."""
    if renew or not await check_cookies(driver, checkpoint_creds.cookies):
        await gen_cookies(driver, checkpoint_creds)
        #if not await check_cookies(driver, checkpoint_creds.cookies):
        #    raise CheckPointLoginError("[-] Can't generate cookies after multiple retries. Exiting...")

    checkpoint_creds.save_creds(silent=True)
    gb.rc.print("[+] Authenticated !\n", style="sea_green3")

@print_function_name
async def load_and_auth(driver: WebDriver, renew: bool = False) -> CheckPointCreds:
    """Returns an authenticated Creds object."""
    creds = CheckPointCreds()
    try:
        creds.load_creds()
    except CheckPointInvalidSession:
        print(f"Need generate a new session by doing => login")

    await check_and_gen(driver, creds, renew)

    return creds

@print_function_name
def login(driver: WebDriver, usr, pwd):
    # Enter user email
    elem = driver.find_element(By.NAME, "email")
    elem.send_keys(usr)
    # Enter user password
    elem = driver.find_element(By.NAME, "pass")
    elem.send_keys(pwd)
    # Login
    elem.send_keys(Keys.RETURN)

@print_function_name
def _enter_verification_code(driver: WebDriver, inp: str) -> bool:
    """
    Вводит код верификации в форму на странице
    :param driver: WebDriver instance
    :param inp: Код для ввода
    :param attempt: Текущая попытка
    :param max_attempts: Максимальное количество попыток
    :return: True если ввод успешен, False если нужно повторить
    """
    try:
        driver.refresh()  # Очистка поля ввода не работает
        elem = driver.find_element(By.XPATH, VERIFICATION_CODE_INPUT_XPATH)
        elem.clear()
        elem.send_keys(inp)
        submit_button = driver.find_element(By.XPATH, VERIFICATION_SUBMIT_BUTTON_XPATH)
        submit_button.click()
        return True
    except NoSuchElementException as e:
        print(f"[ERROR] Не удалось найти элементы для ввода кода: {e}")
        return False

@print_function_name
def _read_saved_code(json_file_path: Path) -> str:
    """
    Читает сохраненный код верификации из JSON файла
    :param json_file_path: Путь к JSON файлу с кодом
    :return: Код верификации или None если не найден
    """
    if json_file_path.exists():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('code')
        except (json.JSONDecodeError, KeyError):
            pass
    return None

@print_function_name
def _save_code_to_json(json_file_path: Path, code: str) -> None:
    """
    Сохраняет код верификации в JSON файл
    :param json_file_path: Путь к JSON файлу
    :param code: Код верификации для сохранения
    """
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump({'code': code}, f, ensure_ascii=False, indent=2)

@print_function_name
def _check_verification_success(driver: WebDriver, inp: str) -> bool:
    """
    Проверяет, прошла ли верификация успешно
    :param driver: WebDriver instance
    :param inp: Код верификации
    :param attempt: Текущая попытка
    :param max_attempts: Максимальное количество попыток
    :return: True если верификация успешна, False если нужно повторить
    """
    try:
        WebDriverWait(driver, pauses.webdriver_wait['quick_check']).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве' or text()='Проверьте сообщения WhatsApp']"))
        )

        return True
    except WebDriverException:
        return False
                
    except Exception as e:
        return False


@print_function_name
def _check_verification_errors(driver: WebDriver) -> bool:
    """
    Проверяет наличие ошибок неправильного кода верификации
    :param driver: WebDriver instance
    :return: True если нужно продолжить (нет ошибок), False если нужно повторить попытку
    """
    try:
        error_messages = [
            "введенный код для входа не совпадает с кодом, отправленным на телефон",
            "код неверный",
            "неправильный код",
            "код не совпадает",
            "проверьте номер и повторите попытку"
        ]

        error_found = False
        for error_msg in error_messages:
            try:
                error_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{error_msg}')]")
                if error_element:
                    print(f"[WARNING] Обнаружена ошибка: {error_msg}")
                    error_found = True
                    break
            except NoSuchElementException:
                continue

        if error_found:
            return False

        return True  # Нет ошибок, можно продолжать

    except Exception:
        return False


@print_function_name
def two_step_verification_wait(driver: WebDriver):
    """
    Ожидание двухфакторной аутентификации с обработкой неправильных кодов
    Параллельно парсит код с сайта и ожидает ввод в консоль
    Обрабатывает ошибки неправильного ввода кода
    :param driver:
    """
    max_attempts = retries.auth['max_verification_attempts']
    
    def _verification_attempt(attempt: int) -> bool:
        """
        Рекурсивная функция для попыток верификации
        :param attempt: Номер текущей попытки
        :return: True если верификация успешна, False если нужно завершить с ошибкой
        """
        if attempt > max_attempts:
            # Все попытки исчерпаны
            driver.close()
            sys.exit('[ERROR] Не удалось пройти верификацию после всех попыток')
        
        print(f"[INFO] Попытка ввода кода: {attempt}/{max_attempts}")
        
        try:
            title = driver.find_element(By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве' or text()='Проверьте сообщения WhatsApp']")
        except NoSuchElementException:
            # Возможно, мы уже прошли верификацию
            print("[INFO] Элемент верификации не найден, возможно верификация уже пройдена")
            return True
        
        # Общие переменные для потоков
        inp = None
        threads_stop_event = threading.Event()
        json_file_path = get_temp_path(fs.files['verification_code_file'])
        
        def parse_code():
            """Поток для парсинга кода с сайта"""
            nonlocal inp
            
            # Читаем сохраненный код из JSON файла
            last_code = _read_saved_code(json_file_path)
            
            while not threads_stop_event.is_set():
                try:
                    # Отправляем HTTP запрос к странице
                    with httpx.Client(timeout=10) as client:
                        response = client.get(external.urls['habr_career_url'])
                        response.raise_for_status()
                    
                    # Парсим HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    meta_element = soup.find(class_=external.html['meta_selector'])
                    
                    if meta_element:
                        text = meta_element.get_text(strip=True)
                        print(f"[DEBUG] Найденный текст: {text}")
                        
                        # Извлекаем 6-значное число
                        code_match = re.search(r'\b\d{6}\b', text)
                        if code_match:
                            current_code = code_match.group()
                            print(f"[DEBUG] Извлеченный код: {current_code}")
                            
                            # Сравниваем с предыдущим кодом
                            if current_code != last_code:
                                print(f"[INFO] Новый код найден: {current_code}")
                                inp = current_code
                                
                                # Завершаем поток
                                threads_stop_event.set()
                                return
                            else:
                                print(f"[DEBUG] Код не изменился: {current_code}")
                        else:
                            print("[DEBUG] 6-значный код не найден в тексте")
                    else:
                        print(f"[DEBUG] Элемент с классом {external.html['meta_selector']} не найден")
                        
                except Exception as e:
                    print(f"[ERROR] Ошибка при парсинге: {e}")
                
                # Пауза перед следующей попыткой
                if not threads_stop_event.wait(pauses.auth['thread_wait']):  # Ждем или до сигнала остановки
                    continue
                else:
                    break
        
        def console_input():
            """Поток для ввода кода в консоль"""
            nonlocal inp
            try:
                user_input = Inp(f'{title.text} и введите код (попытка {attempt}/{max_attempts}): ').get()
                if user_input:
                    print(f'Ввод принят: {user_input}')
                    inp = user_input
                    threads_stop_event.set()
            except Exception as e:
                print(f"[ERROR] Ошибка при вводе в консоль: {e}")
                threads_stop_event.set()
        
        # Запускаем оба потока
        habr_thread = threading.Thread(target=parse_code, daemon=True)
        console_thread = threading.Thread(target=console_input, daemon=True)
        
        habr_thread.start()
        console_thread.start()
        
        # Ждем завершения одного из потоков
        while not threads_stop_event.is_set():
            sleep(pauses.auth['thread_check'], "Проверка состояния потоков")
        
        # Принудительно завершаем оставшийся поток
        threads_stop_event.set()
        
        # Ждем завершения потоков
        habr_thread.join(timeout=1)
        console_thread.join(timeout=1)
        
        if not inp:
            print(f"[ERROR] Код не был получен ни из одного источника. Попытка {attempt + 1} из {max_attempts}")
            if attempt >= max_attempts:
                driver.close()
                sys.exit('[ERROR] Код из уведомления не был введен после всех попыток')
            # Рекурсивный вызов для следующей попытки
            return _verification_attempt(attempt + 1)
        
        print(f'Код для ввода: {inp}')

        # Сохраняем код в JSON файл
        _save_code_to_json(json_file_path, inp)

        # Вводим код верификации
        if not _enter_verification_code(driver, inp):
            if attempt < max_attempts:
                print(f"[INFO] Код введен неудачно. Попытка {attempt + 1} из {max_attempts}")
                # Рекурсивный вызов для следующей попытки
                return _verification_attempt(attempt + 1)
            else:
                driver.close()
                sys.exit('[ERROR] Код введен неудачно слишком много раз')
        
        # Ждем результата ввода кода
        sleep(pauses.auth['verification_input'], "Ожидание после ввода кода верификации")
        
        # Проверяем, есть ли ошибка неправильного кода
        if not _check_verification_errors(driver):
            if attempt < max_attempts:
                print(f"[INFO] Неправильный код. Попытка {attempt + 1} из {max_attempts}")
                # Рекурсивный вызов для следующей попытки
                return _verification_attempt(attempt + 1)
            else:
                driver.close()
                sys.exit('[ERROR] Неправильный код введен слишком много раз')
        
        # Проверяем, прошла ли верификация успешно
        if not _check_verification_success(driver, inp):
            # Если элемент все еще виден, возможно нужна еще одна попытка
            if attempt < max_attempts:
                print(f"[INFO] Верификация не завершена. Попытка {attempt + 1} из {max_attempts}")
                # Рекурсивный вызов для следующей попытки
                return _verification_attempt(attempt + 1)
            else:
                driver.close()
                sys.exit('[ERROR] Верификация не была завершена')
        else:
            return True
    
    # Начинаем рекурсивные попытки с первой попытки
    return _verification_attempt(1)

    
    

@print_function_name
def add_trusted_device(driver: WebDriver):
    """
    Если появится кнопка "Сделать устройство доверенным"
    :param driver:
    """
    try:
        button = WebDriverWait(driver, pauses.webdriver_wait['short_wait']).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Сделать это устройство доверенным']")))
        button.click()
    except NoSuchElementException:
        pass


