# This file is only intended to serve global variables at a project-wide level.
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
import os
from checkpoint.objects.base import DualConsole

# Глобальная переменная для хранения имени текущего модуля
current_module_name: str = "Unknown"

# Глобальный синхронизатор задач
task_sync = None



def init_globals():
    from checkpoint.objects.utils import TMPrinter, TaskSynchronizer

    global config, tmprinter, rc, args, task_sync
    
    from checkpoint import config
    tmprinter = TMPrinter()
    rc = DualConsole(highlight=True)  # Используем систему двойного вывода
    task_sync = TaskSynchronizer()  # Инициализируем синхронизатор задач
    
def cleanup_globals():
    """Корректно завершает работу с глобальными объектами"""
    global rc
    if 'rc' in globals() and hasattr(rc, 'close'):
        rc.close()


def add_global(name: str, value: Any):
    """Add a new global variable that can be accessed from anywhere in the application.

    Args:
        name (str): Name of the global variable
        value (any): Value to assign to the global variable
    """
    globals()[name] = value
