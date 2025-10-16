from checkpoint.helpers.utils import *
from checkpoint.errors import *
from checkpoint.objects.base import SmartObj

from typing import *
import threading

from rich.console import Console

class TMPrinter():
    """
        Print temporary text, on the same line.
    """
    def __init__(self, rc: Console=Console(highlight=False)):
        self.max_len = 0
        self.rc = rc

    def out(self, text: str, style: str=""):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        self.rc.print(text, end='\r', style=style)
    def clear(self):
        self.rc.print(" " * self.max_len, end="\r")


class TaskSynchronizer:
    """
    Класс для синхронизации выполнения задач.
    
    Обеспечивает механизм взаимного исключения для задач,
    позволяя только одной задаче выполняться в определенный момент времени.
    """
    
    def __init__(self):
        """Инициализация синхронизатора задач."""
        self._current_running_task: Optional[str] = None
        self._lock = threading.Lock()
    
    def get_current_running_task(self) -> Optional[str]:
        """Получить имя текущего выполняющегося таска.
        
        Returns:
            str: Имя текущего таска или None если все таски на паузе
        """
        with self._lock:
            return self._current_running_task
    
    def set_current_running_task(self, task_name: Optional[str]) -> None:
        """Установить имя текущего выполняющегося таска.
        
        Args:
            task_name: Имя таска или None для освобождения
        """
        with self._lock:
            self._current_running_task = task_name
    
    def is_task_running(self, task_name: Optional[str] = None) -> bool:
        """Проверить, выполняется ли какой-либо таск или конкретный таск.
        
        Args:
            task_name: Имя таска для проверки. Если None, проверяет выполняется ли любой таск
        
        Returns:
            bool: True если таск выполняется
        """
        with self._lock:
            if task_name is None:
                return self._current_running_task is not None
            return self._current_running_task == task_name
    
    def can_run_task(self, task_name: str) -> bool:
        """Проверить, может ли таск начать выполнение.
        
        Args:
            task_name: Имя таска который хочет начать выполнение
        
        Returns:
            bool: True если таск может начать выполнение (нет других активных тасков или это уже активный таск)
        """
        with self._lock:
            return self._current_running_task is None or self._current_running_task == task_name
    
    def reset(self) -> None:
        """Сбросить синхронизатор, освободив текущий таск."""
        with self._lock:
            self._current_running_task = None