#!/usr/bin/env python3
import argparse
import os
import pickle
import sys
import threading
from datetime import datetime
from os import listdir
from os.path import isfile, isdir, join
from pathlib import Path
from time import sleep
from typing import Any
from urllib import parse

import filetype
from hurry.filesize import size
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

home: str = 'https://www.facebook.com/'
folder = ""
index_file = 1
index_to_album = 0
size_to_album = 0
cookie_filename = f"fb.pkl"  # todo в название файла логин добавить
progress_filename = f"progress.pkl"
splited_size = 20
renew_cookie = False
root_folder = ''

threadLocal = threading.local()

def get_driver() -> WebDriver:
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2  # 1:allow, 2:block
        })

        driver = webdriver.Chrome(options=chrome_options)  #todo добавить опцию не показывать браузер
        setattr(threadLocal, 'driver', driver)

    return driver


def login(driver, usr, pwd):
    # Enter user email
    elem = driver.find_element(By.ID, "email")
    elem.send_keys(usr)
    # Enter user password
    elem = driver.find_element(By.ID, "pass")
    elem.send_keys(pwd)
    # Login
    elem.send_keys(Keys.RETURN)


def two_step_verification_wait(driver):
    """
    бесконечное ожидание, пока я вход на телефоне не подтвержу
    :param driver:
    """
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Проверьте уведомления на другом устройстве']")))
    WebDriverWait(driver, 1000).until(lambda x: not driver.current_url.find('/two_step_verification/two_factor/') != -1)

def add_trusted_device(driver):
    """
    Если появится кпонка "Сделать устройство доверенным"
    :param driver:
    """

    try:
        button = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Сделать это устройство доверенным']")))
        button.click()
    except NoSuchElementException:
        pass

    sleep(5)


def save_cookies(driver, filename):
    pickle.dump(driver.get_cookies(), open(filename, 'wb'))
    print("cookies saved successfully")


def add_cookies(driver, filename):
    try:
        cookies = pickle.load(open(filename, 'rb'))
    except FileNotFoundError:
        return False

    if cookies:
        now_timestamp = datetime.timestamp(datetime.now())
        #[{'domain': '.facebook.com', 'expiry': 1735714471, 'httpOnly': True, 'name': 'fr', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '05ph6f0hw4tuSzo9F.AWU-O3D10vsFCE9voUFq_NNXPMQ.Bm_j9b..AAA.0.0.Bm_j-m.AWU8cqDJJyc'}, {'domain': '.facebook.com', 'expiry': 1759474424, 'httpOnly': True, 'name': 'xs', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '35%3A0UNfy0QwpAuLmw%3A2%3A1727938422%3A-1%3A14476'}, {'domain': '.facebook.com', 'expiry': 1759474424, 'httpOnly': False, 'name': 'c_user', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '100007859116486'}, {'domain': '.facebook.com', 'expiry': 1728543205, 'httpOnly': False, 'name': 'locale', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'ru_RU'}, {'domain': '.facebook.com', 'httpOnly': False, 'name': 'presence', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1727938473890%2C%22v%22%3A1%7D'}, {'domain': '.facebook.com', 'expiry': 1728543273, 'httpOnly': False, 'name': 'wd', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '929x873'}, {'domain': '.facebook.com', 'expiry': 1762498397, 'httpOnly': True, 'name': 'datr', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'Wz_-ZubvX8PhEuJo2hFYXuKA'}, {'domain': '.facebook.com', 'expiry': 1762498424, 'httpOnly': True, 'name': 'sb', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'Wz_-ZluV4_krp6As8GZW3_l_'}]
        for cookie in cookies:
            if cookie.get('expiry') and cookie['expiry'] < now_timestamp:
                print("cookies expired")
                return False
            driver.add_cookie(cookie)
        print("cookies added successfully")
        return True
    else:
        return False

def save_progress(album_id, file_number, album_name):
    pickle.dump([album_id, file_number, album_name], open(progress_filename, 'wb'))

def clear_saved_progress():
    if os.path.isfile(progress_filename):
        os.remove(progress_filename)

def restore_progress() -> bool | tuple[Any]:
    try:
        progress = pickle.load(open(progress_filename, 'rb'))
    except FileNotFoundError:
        return False

    return *progress,


def upload_to_album(driver, album_id: int, files: list[str], files_meta: dict):
    # Открытие созданного альбома на редактирование и догрузка в него остальных файлов
    global index_file, index_to_album, size_to_album

    print(f"ID альбома: {album_id}")

    driver.get(f"{home}media/set/edit/a.{album_id}")

    # Загрузка файлов
    files_input = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    set_files_to_field(files_input, files, files_meta)

    # Кнопка "Добавить в альбом"
    sleep(5)
    while True:
        check_popups(driver)

        add_dialogs = driver.find_elements(By.XPATH, "//*[text()='Добавить в альбом']")  # "//*[@aria-label='Добавление в альбом' and @role='dialog']"
        add_dialogs = add_dialogs[::-1]
        print(f"Открытых диалоговых окон: {len(add_dialogs)}")

        if not add_dialogs:
            break

        for index, button in enumerate(add_dialogs):
            try:
                button.click()
            except WebDriverException:
                continue

            print(f"Сохранение фото")
            del add_dialogs[index]

            # После клика дождаться пока опубликуется
            wait = WebDriverWait(driver, 50)
            wait.until(lambda x: not driver.find_elements(By.XPATH, "//*[text()='Публикация']"))

            break  # После отправки формы список диалоговых окон нужно получать заново, т.к. самого верхнего окна в списке больше не осталось

    submit_button = driver.find_element(By.XPATH, "//*[text()='К альбому']") # todo предусмотреть если вместо этой кнопки кнопка Сохранить
    submit_label = driver.find_element(By.XPATH, "//*[@aria-label='К альбому']")

    while True:
        sleep(1)
        try:
            if submit_label.get_attribute('aria-disabled'):
                continue

            submit_button.click()
        except WebDriverException:
            continue
        print("Отправка формы")
        break

    x, x, album_name = restore_progress()
    save_progress(album_id, index_file, album_name)

def create_album(driver, files: list[str], files_meta: dict):
    """

    :param driver:
    :param files:
    :param files_meta:
    :return: album_id
    """
    global index_file, index_to_album
    driver.get(home + "media/set/create")

    files_input = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    set_files_to_field(files_input, files, files_meta)

    # Ввести название альбома
    album_name = folder.split("\\")
    album_name = list(filter(None, album_name))

    del album_name[0]
    del album_name[0]
    album_name = '\\'.join(album_name)
    album_name = album_name.replace('\\\\', '\\')
    elem = driver.find_element(By.XPATH, "//input[@type='text']")
    elem.send_keys(album_name)
    print(f"Название альбома: {album_name}")

    # Дождаться загрузки файлов и нажать кнопку создания альбома
    submit_button = driver.find_element(By.XPATH, "//*[text()='Отправить']")
    submit_label = driver.find_element(By.XPATH, "//*[@aria-label='Отправить']")

    retry_count = 0
    while True:
        # проверка на ошибки загрузки отдельных файлов
        try:
            repeat_button = driver.find_element(By.XPATH, "//*[text()='Повторить попытку']")
            repeat_button.click()
            retry_count += 1
            print(f"Повторная загрузка файлов с ошибками. Попытка {retry_count}")
        except NoSuchElementException:
            pass
        except WebDriverException:
            retry_count += 1

        sleep(1)

        if retry_count >= 10:
            try:
                print("Снятие проблемных файлов с загрузки")
                delete_item_labels = driver.find_elements(By.XPATH, "//*[@aria-label='Удалить видео']")
                for label in delete_item_labels:
                    label.click()
                    sleep(1)
            except WebDriverException:
                pass
            retry_count = 0

        try:
            if submit_label.get_attribute('aria-disabled'):
                continue

            album_description = driver.find_element(By.XPATH, "//*[@aria-label='Описание (необязательно)']").find_element(By.XPATH, '//textarea')
            album_description.send_keys(album_name)

            submit_button.click()
        except WebDriverException:
            continue

        print("Отправка формы")

        break

    wait = WebDriverWait(driver, 100)
    wait.until(lambda x: driver.current_url.find('&set=') != -1) # ожидание когда завершится перенаправление на страницу созданного альбома

    query_def = parse.parse_qs(parse.urlparse(driver.current_url).query).get('set')[0]
    album_id = query_def.lstrip('a.')
    save_progress(album_id, index_file, album_name)

    return (int(album_id), album_name)

def parse_cli_args():
    """
    Пример ввода
    run.py --folder "D:\\PHOTO\\Домашние\\АРХИВЫ\\РАЗНОЕ\\Мамина работа\\к педсовету" --renewcookie --splitedsize=30
    run.py --folder "Стар. фото из Протасово -родня" --splitedsize=10 --rootfolder "D:\\PHOTO"
    """
    global folder, renew_cookie, splited_size, root_folder

    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', dest='folder', type=str, help='Full path to the folder', required=True)
    parser.add_argument('--renewcookie', help='Force renew cookie', action="store_true")
    parser.add_argument('--splitedsize', help='How many files to send to the album per iteration', type=int, default=20)
    parser.add_argument('--rootfolder', help='Root folder for target folder', type=str)
    args = parser.parse_args()
    folder = args.folder
    renew_cookie = args.renewcookie
    splited_size = args.splitedsize
    root_folder = args.rootfolder

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f"{prefix} |{bar}| {percent}% {suffix}")
    # Print New Line on Complete
    if iteration == total:
        print()

def set_files_to_field(files_input: WebElement, files: list, files_meta: dict):
    global index_file, index_to_album, size_to_album

    files_count = len(files_meta)
    size_all_files = sum(files_meta.values())

    # Initial call to print 0% progress
    print_progress_bar(size_to_album, size_all_files, prefix='Progress:', suffix='Complete', length=50)

    for file in files:
        ipath = '\\'.join([folder, file])
        print(f"Загрузка фото: {file} {size(files_meta[file])}")
        files_input.send_keys(ipath)
        sys.stdout.flush()
        index_file += 1
        index_to_album += 1
        size_to_album += files_meta[file]
        print(
            f"Загружено {index_to_album} фото из {files_count} ({size(size_to_album)} из {size(size_all_files)})",
            flush=True
        )
        print_progress_bar(size_to_album, size_all_files, prefix='Progress:', suffix='Complete', length=50)
        sleep(0.2)

def check_popups(driver):
    """
    Попапы "Мы удалили вашу публикацию" и "Вы временно заблокированы" обрабатывать
    :param driver:
    """
    need_return = False
    popup_text = None
    try:
        popup = driver.find_element(By.XPATH, "//*[text()='Вы временно заблокированы' or text()='Мы удалили вашу публикацию']")
        popup_text = popup.text
        button = driver.find_element(By.XPATH, "//*[text()='OK']")
        button.click()
    except WebDriverException:
        need_return = True


    if need_return:
        return need_return

    print(f"Обнаружен попап {popup_text}")
    sleep(10 * 60)
    return True

def search_folder_recursive(folder: str, root_path: str = '.') -> str|None:
    """

    :return:
    :rtype: object
    :return:
    :param root_path:
    :type folder: object
    """

    def listdir_r(dirpath, searching_folder):
        paths = []
        for path in listdir(dirpath):
            rpath = join(dirpath, path)
            if isdir(rpath):
                if searching_folder == path:
                    paths.append(rpath)
                    break
                else:
                    subdirs = listdir_r(rpath, searching_folder)
                    if not subdirs == []:
                        paths.extend(subdirs)
        return paths if paths else []

    paths = listdir_r(root_path, folder)

    return paths[0] if paths else None


def main():
    global index_file, folder

    # Your Facebook account user and password
    usr = config.USER_NAME
    pwd = config.PASSWORD

    parse_cli_args()

    driver = get_driver()

    # Go to facebook.com
    driver.get(home)

    if renew_cookie or not add_cookies(driver, cookie_filename):
        login(driver, usr, pwd)
        two_step_verification_wait(driver)
        add_trusted_device(driver)
        save_cookies(driver, cookie_filename)

    #todo обрыв связи обрабатывать
    #todo очистка списка от дубликатов
    #todo распознавать капчу и ждать ввода

    #todo пройтись по структуре папок и собрать папки на аплоад и создание альбомов
    #folder = "D:\\PHOTO\\Домашние\\АРХИВЫ\\ПРИРОДА виды улица интерьеры животные\\2012 г" #todo дозакинуть

    if folder.split('\\').__len__() == 1:
        # Задано только название папки, а не полный путь - найти папку
        folder = search_folder_recursive(folder, root_folder.replace('\\\\', '\\') if root_folder else 'D:\\')

    print(f"Полный путь к папке {folder}")

    files = [(f, os.path.getsize(join(folder, f))) for f in listdir(folder) if isfile(join(folder, f)) and filetype.is_image(join(folder, f))]

    progress = restore_progress()
    if progress:
        index_file = progress[1]
        del files[0:index_file]

    files_count = len(files)
    files_meta = dict(files)
    files, files_sizes = zip(*files)

    print(f"Найдено файлов для загрузки {files_count} {size(sum(files_sizes))}")

    files_splited = [files[x:x + splited_size] for x in range(0, len(files), splited_size)]

    if not progress:
        # Создание альбома и загрузка файлов
        album_id, album_name = create_album(driver, files_splited[0], files_meta)
        del files_splited[0]
    else:
        album_id = progress[0]
        album_name = progress[2]

    while True:
        if not files_splited:
            break
        upload_to_album(driver, album_id=album_id, files=files_splited[0], files_meta=files_meta)
        del files_splited[0]

    print("Загрузка завершена\n")
    print(f"Название альбома: {album_name}")
    print(f"ID альбома: {album_id}")
    print(f"Загружено файлов: {files_count} {size(sum(files_sizes))}")
    clear_saved_progress()

    sleep(500)# todo Менять видимость альбома

    driver.close()


if __name__ == '__main__':
    main()
