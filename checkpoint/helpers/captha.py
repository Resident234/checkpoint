import requests
from selenium.webdriver.support import expected_conditions as EC

from selenium.common import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import speech_recognition as sr
from pydub import AudioSegment
from checkpoint.helpers.utils import sleep


def solve_captcha(driver: WebDriver):
    """
    Распознавать страницу запроса капчу и ждать ввода
    :param driver:
    """
    captcha_text = solve_audio_captcha(driver)

    print("Текст капчи:" + captcha_text)
    input = driver.find_element(By.XPATH, "//input[@type='text']")
    input.send_keys(captcha_text)
    sleep(1, "Ожидание после ввода капчи")
    submit_button = driver.find_element(By.XPATH, "//*[text()='Продолжить']")
    submit_button.click()

    # todo инструкцию по развертыванию написать и первый ответ тоже https://stackoverflow.com/questions/55669182/how-to-fix-filenotfounderror-winerror-2-the-system-cannot-find-the-file-speci
    # todo мониторить сообщение "Не удалось добавить медиафайлы в этот альбом". Релоадить страницу и начинать загрузку фото заново. Засекать проблемный файл и выкидывать его из списка
    # todo в консоль записывать имена файлов, которые сохраняются

    try:
        WebDriverWait(driver, 1000).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[text()='Введите символы, которые вы видите']")))
    except WebDriverException:
        pass

def solve_audio_captcha(driver: WebDriver):
    audio_src = driver.find_element(By.XPATH, "//*[text()='воспроизвести аудио']").get_attribute('href')
    driver.execute_script("window.open('');")
    # Switch to the new window
    driver.switch_to.window(driver.window_handles[1])
    driver.get(audio_src)

    sleep(10, "Ожидание загрузки аудио капчи")  # todo дождаться пока загрузится

    audio_element = driver.find_element(By.CSS_SELECTOR, "audio")
    audio_url = audio_element.get_attribute('src')
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(r"C:\Users\Professional\audio.mp3",
                  'wb') as f:  # @todo имена и расположение файлов а так же их очистка
            f.write(response.content)

    driver.switch_to.window(driver.window_handles[0])

    # convert mp3 file to wav
    src = r"C:\Users\Professional\audio.mp3"
    sound = AudioSegment.from_mp3(src)
    sound.export(r"C:\Users\Professional\audio.wav", format="wav")

    file_audio = sr.AudioFile(r"C:\Users\Professional\audio.wav")  # todo путь поправить

    # use the audio file as the audio source
    r = sr.Recognizer()
    with file_audio as source:
        audio_text = r.record(source)

    captcha_text = r.recognize_google(audio_text)
    captcha_text = captcha_text.replace(" ", "")

    return captcha_text