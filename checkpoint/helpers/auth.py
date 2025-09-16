import sys

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from checkpoint import config
from checkpoint.errors import *
from checkpoint.helpers.captha import *
from checkpoint.helpers.pages import *
from checkpoint.helpers.utils import *
from checkpoint.knowledge.pages import urls
from checkpoint.objects.base import CheckPointCreds, Inp


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
def two_step_verification_wait(driver: WebDriver): #todo неправильный ввод обрабатывать
    """
    бесконечное ожидание, пока я вход на телефоне не подтвержу
    :param driver:
    """
    title = driver.find_element(By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве' or text()='Проверьте сообщения WhatsApp']")
    inp = Inp(f'{title.text} и введите код: ').get()
    if inp:
        print(f'Ввод принят: {inp}')
        elem = driver.find_element(By.XPATH, "//input[@type='text']")
        elem.send_keys(inp)
        sleep(1)
        submit_button = driver.find_element(By.XPATH, "//*[text()='Продолжить']")
        submit_button.click()
    try:
        WebDriverWait(driver, 1000).until(EC.invisibility_of_element_located((By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве' or text()='Проверьте сообщения WhatsApp']")))
    except WebDriverException:
        driver.close()
        sys.exit('Код из уведомления не был введен')

@print_function_name
def add_trusted_device(driver: WebDriver):
    """
    Если появится кнопка "Сделать устройство доверенным"
    :param driver:
    """
    try:
        button = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Сделать это устройство доверенным']")))
        button.click()
    except NoSuchElementException:
        pass


