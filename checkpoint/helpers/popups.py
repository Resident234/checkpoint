from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from checkpoint import globals as gb
from checkpoint.helpers.utils import print_function_name


@print_function_name
def get_popup(driver: WebDriver, text: str) -> Optional[WebElement]:
    """
    Ищет и возвращает диалог по тексту внутри него
    
    Args:
        driver: WebDriver instance
        text: Текст для поиска внутри диалога
        
    Returns:
        WebElement: Найденный элемент диалога или None если не найден
    """   
    try:
        dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
        if text in dialog.text:
            gb.rc.print(f"✅ Найден диалог с текстом: {text}", style="green")
            return dialog
    except NoSuchElementException:
        pass
    
    gb.rc.print(f"⚠️ Диалог с текстом '{text}' не найден", style="yellow")
    return None


@print_function_name
def get_button(dialog: WebElement, aria_label: str = "OK") -> Optional[WebElement]:
    """
    Ищет кнопку внутри диалога по aria-label
    
    Args:
        dialog: WebElement диалога, внутри которого нужно искать кнопку
        aria_label: Значение атрибута aria-label для поиска (по умолчанию "OK")
        
    Returns:
        WebElement: Найденная кнопка или None если не найдена
    """
    try:
        button = dialog.find_element(By.XPATH, f".//button[@aria-label='{aria_label}']")
        if button:
            gb.rc.print(f"✅ Найдена кнопка с aria-label='{aria_label}'", style="green")
            return button
    except NoSuchElementException:
        gb.rc.print(f"⚠️ Кнопка с aria-label='{aria_label}' не найдена в диалоге", style="yellow")
    
    return None


@print_function_name
def get_ok_button(dialog: WebElement) -> Optional[WebElement]:
    """
    Ищет кнопку OK внутри диалога
    
    Args:
        dialog: WebElement диалога, внутри которого нужно искать кнопку
        
    Returns:
        WebElement: Найденная кнопка OK или None если не найдена
    """
    return get_button(dialog, aria_label="OK")


@print_function_name
def get_close_button(dialog: WebElement) -> Optional[WebElement]:
    """
    Ищет кнопку Закрыть внутри диалога
    
    Args:
        dialog: WebElement диалога, внутри которого нужно искать кнопку
        
    Returns:
        WebElement: Найденная кнопка Закрыть или None если не найдена
    """
    return get_button(dialog, aria_label="Закрыть")


@print_function_name
def check_popup(driver: WebDriver, popup_type: str) -> bool:
    """
    Проверяет наличие различных типов всплывающих окон
    
    Args:
        driver: WebDriver instance
        popup_type: Тип проверяемого popup'а (например, "session_timeout")
        
    Returns:
        bool: True если найден указанный popup, False в противном случае
    """
    try:
        if popup_type == "session_timeout":
            # Пробуем найти элемент с точным текстом "Время сеанса истекло"
            try:
                element = driver.find_element(By.XPATH, "//*[contains(text(), 'Время сеанса истекло')]")
                if element:
                    gb.rc.print("⚠️ Обнаружен диалог: Время сеанса истекло", style="yellow")
                    return True
            except NoSuchElementException:
                pass
            
            # Альтернативный способ: ищем div с role="dialog" и проверяем текст
            try:
                dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
                if "Время сеанса истекло" in dialog.text:
                    gb.rc.print("⚠️ Обнаружен диалог: Время сеанса истекло", style="yellow")
                    return True
            except NoSuchElementException:
                pass
            
    except NoSuchElementException:
        # Диалог не найден - это нормально
        pass
    
    return False
