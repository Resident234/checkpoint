# This file is only intended to serve global variables at a project-wide level.
from typing import Any


def init_globals():
    from checkpoint.objects.utils import TMPrinter
    from rich.console import Console

    global config, tmprinter, rc, args
    
    from checkpoint import config
    tmprinter = TMPrinter()
    rc = Console(highlight=False) # Rich Console
    
def add_global(name: str, value: any):
    """Add a new global variable that can be accessed from anywhere in the application.

    Args:
        name (str): Name of the global variable
        value (any): Value to assign to the global variable
    """
    globals()[name] = value
