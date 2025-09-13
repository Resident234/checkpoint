from typing import *

import httpx
from pathlib import Path

from checkpoint import globals as gb, config
from checkpoint.helpers.utils import *
from checkpoint.helpers import auth
from checkpoint.objects.base import CheckPointCreds
from checkpoint.errors import CheckPointInvalidSession
from selenium.webdriver.chrome.webdriver import WebDriver


@print_function_name
async def check_and_login(driver: WebDriver = None, renewcookie: bool=False) -> None:
    """Check the users credentials validity, and generate new ones."""

    checkpoint_creds = CheckPointCreds()

    if renewcookie:
        creds_path = Path(checkpoint_creds.creds_path)
        if creds_path.is_file():
            creds_path.unlink()
            print(f"[+] Credentials file at {creds_path} deleted !")
        else:
            print(f"Credentials file at {creds_path} doesn't exists, no need to delete.")
        exit()

    try:
        checkpoint_creds = await auth.load_and_auth(driver, renew=renewcookie, help=False)
    except CheckPointInvalidSession as e:
        print(f"[-] {e}\n")

    driver.refresh()

    checkpoint_creds.save_creds()
