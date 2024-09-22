#!/usr/bin/env python3
from selenium.common import NoSuchElementException

import config
from pathlib import Path
from time import sleep
from os import listdir
from os.path import isfile, join

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


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
    driver.implicitly_wait(15)  # seconds

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
    driver.refresh()
    body = driver.find_element(By.CSS_SELECTOR, "body")
    body.click()

    try:
        button = driver.find_element(By.XPATH, "//*[text()='Сделать это устройство доверенным']")
        button.click()
    except NoSuchElementException:
        pass

    #todo сохранить куки, чтобы подтверждение не вводить каждый раз
    sleep(5)
    driver.get("https://www.facebook.com/media/set/create")
    sleep(15)

    folder = "D:\\PHOTO\\Домашние\\АРХИВЫ\\ПРИРОДА виды улица интерьеры животные\\2012 г"
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    print(f"Найдено файлов для загрузки {len(files)}")

    files_input = driver.find_element(By.XPATH, "//input[@type='file']")

    index = 1
    for file in files:
        ipath = '\\'.join([folder, file])
        print(f"Загрузка фото: {file}")
        files_input.send_keys(ipath)
        print(f"Загружено {index} фото", flush=True)
        index += 1
        if index == 100:
            break
        sleep(1)

    # Ввести название альбома
    album_name = folder.split("\\")
    del album_name[0]
    album_name = '\\'.join(album_name)
    elem = driver.find_element(By.XPATH, "//input[@type='text']")
    elem.send_keys(album_name)
    print(f"Название альбома: {album_name}")

    #

    sleep(170)

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

    driver.close()

if __name__ == '__main__':
    main()
