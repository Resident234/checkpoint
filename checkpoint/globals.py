# This file is only intended to serve global variables at a project-wide level.
from typing import Any
from pathlib import Path
from datetime import datetime
from rich.console import Console
import os
from checkpoint.objects.base import DualConsole



def init_globals():
    from checkpoint.objects.utils import TMPrinter

    global config, tmprinter, rc, args
    
    from checkpoint import config
    tmprinter = TMPrinter()
    rc = DualConsole(highlight=True)  # Используем систему двойного вывода
    
def cleanup_globals():
    """Корректно завершает работу с глобальными объектами"""
    global rc
    if 'rc' in globals() and hasattr(rc, 'close'):
        rc.close()


def add_global(name: str, value: any):
    """Add a new global variable that can be accessed from anywhere in the application.

    Args:
        name (str): Name of the global variable
        value (any): Value to assign to the global variable
    """
    globals()[name] = value
