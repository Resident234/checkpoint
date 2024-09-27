#!/usr/bin/env python3
from os import listdir
from os.path import isfile, join
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config


def main():
    # Your Facebook account user and password
    usr = config.USER_NAME
    pwd = config.PASSWORD

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2  # 1:allow, 2:block
    })

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(150)  # seconds

    # Go to facebook.com
    driver.get("http://www.facebook.com")
    sleep(2)
    # Enter user email
    elem = driver.find_element(By.ID, "email")
    elem.send_keys(usr)
    # Enter user password
    elem = driver.find_element(By.ID, "pass")
    elem.send_keys(pwd)
    # Login
    elem.send_keys(Keys.RETURN)
    sleep(70)

    # Если появится кпонка "Сделать устройство доверенным"
    # todo включить бесконечное ожидание, пока я вход на телефоне не подтвержу
    # todo папку задавать на входе, полный путь к ней иска самостоятельно
    body = driver.find_element(By.CSS_SELECTOR, "body")
    body.click()

    try:
        button = driver.find_element(By.XPATH, "//*[text()='Сделать это устройство доверенным']")
        button.click()
    except NoSuchElementException:
        pass

    #todo сохранить куки, чтобы подтверждение не вводить каждый раз
    #todo обрыв связи обрабатывать
    #todo очистка списка от дубликатов
    sleep(5)
    driver.get("https://www.facebook.com/media/set/create")
    sleep(5)

    #todo пройтись по структуре папок и собрать папки на аплоад и создание альбомов
    #folder = "D:\\PHOTO\\Домашние\\АРХИВЫ\\ПРИРОДА виды улица интерьеры животные\\2012 г" #todo дозакинуть
    folder = "D:\PHOTO\Домашние\АРХИВЫ\ПРИРОДА виды улица интерьеры животные\с 2007 по 2009 г\Москва 2009"

    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    print(f"Найдено файлов для загрузки {len(files)}") #todo вес файла вычислять и выводить

    files_input = driver.find_element(By.XPATH, "//input[@type='file']")

    index = 1
    for file in files:
        ipath = '\\'.join([folder, file])
        print(f"Загрузка фото: {file}")
        files_input.send_keys(ipath)
        print(f"Загружено {index} фото", flush=True)#todo со сбросом буфера разобраться
        index += 1
        sleep(0.2)

    # Ввести название альбома
    album_name = folder.split("\\")
    del album_name[0]
    del album_name[0]
    album_name = '\\'.join(album_name)
    elem = driver.find_element(By.XPATH, "//input[@type='text']")
    elem.send_keys(album_name)
    print(f"Название альбома: {album_name}")

    sleep(2)

    # Дождаться загрузки файлов и нажать кнопку создания альбома
    #todo прогресс аплоада файлов в консоль передавать
    submit_button = driver.find_element(By.XPATH, "//*[text()='Отправить']")
    submit_label = driver.find_element(By.XPATH, "//*[@aria-label='Отправить']")

    retry_count = 0
    while True:
        sleep(1)
        # проверка на ошибки загрузки отдельных файлов
        try:
            repeat_button = driver.find_element(By.XPATH, "//*[text()='Повторить попытку']")
            repeat_button.click()
            print(f"Повторная загрузка файлов с ошибками")
            retry_count += 1
            if retry_count >= 10:
                # Снять проблемные файлы с загрузки
                delete_item_labels = driver.find_elements(By.XPATH, "//*[@aria-label='Удалить видео']")
                for label in delete_item_labels:
                    label.click()
                    sleep(1)
                retry_count = 1
            sleep(5)
        except WebDriverException:
            pass

        try:
            if submit_label.get_attribute('aria-disabled'):
                continue
            submit_button.click()
        except WebDriverException:
            continue
        print("Отправка формы")
        break

    sleep(100)

    driver.close()


    '''
    for group in grp:
    
        driver.get(group)
    
        try:
    
            try:
    
                commentr = WebDriverWait(driver,10).until(EC.element_to_be_clickable( (By.XPATH, "//*[@name='xhpc_message_text']") ))
                commentr.click()
    
            except Exception:
                commentr = WebDriverWait(driver,10).until(EC.element_to_be_clickable( (By.XPATH, "//*[@loggingname='status_tab_selector']") ))
                commentr.click()
    
    
    
            commentr = WebDriverWait(driver,10).until(EC.element_to_be_clickable( (By.XPATH, "//*[@class='_3u15']") ))
            commentr.click()
    
            sleep(3)
            l=driver.find_elements_by_tag_name('input')
            sleep(1)
    
            for g in l:
                if g==driver.find_element_by_xpath("//input[@type='file'][@class='_n _5f0v']"):
                    sleep(1)
                    g.send_keys(ipath)
                    print('image loaded')
    
    
    
    
            sleep(10)
            driver.find_element_by_xpath("//*[@class='_1mf _1mj']").send_keys(message)
    
            sleep(1)
            buttons = driver.find_elements_by_tag_name("button")
            sleep(1)
            for button in buttons:
                    if button.text == "Post":
                        sleep(5)
                        button.click()
                        sleep(10)
    
        except Exception:
            pass
            print ('image not posted in '+group)
    '''



if __name__ == '__main__':
    main()
