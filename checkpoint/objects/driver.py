import threading

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver


class DriverManager():
    def __init__(self, is_headless=False):
        self.is_headless = is_headless
        self.driver = None
        self.threadLocal = threading.local()

    def get_driver(self) -> WebDriver:
        self.driver = getattr(self.threadLocal, 'driver', None)
        if self.driver is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2  # 1:allow, 2:block
            })
            if self.is_headless:
                chrome_options.add_argument("--headless")

            self.driver = webdriver.Chrome(options=chrome_options)
            setattr(self.threadLocal, 'driver', self.driver)

        return self.driver

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
