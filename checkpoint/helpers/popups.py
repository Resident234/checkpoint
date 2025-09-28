from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from checkpoint import globals as gb


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
        # Ищем div с role="dialog"
        dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
        
        if popup_type == "session_timeout":
            # Проверяем, содержит ли диалог текст "Время сеанса истекло"
            if "Время сеанса истекло" in dialog.text:
                gb.rc.print("⚠️ Обнаружен диалог: Время сеанса истекло", style="yellow")
                return True
            
    except NoSuchElementException:
        # Диалог не найден - это нормально
        pass
    
    return False
