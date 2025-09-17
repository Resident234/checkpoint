import pickle
from typing import *
from pathlib import Path
from datetime import datetime


from threading import Thread

from selenium.common import InvalidCookieDomainException



# class SmartObj(Slots): # Not Python 3.13 compatible so FUCK it fr fr
#     pass

class SmartObj():
    pass

class Inp:
    inp = None

    def __init__(self, hint=None):
        t = Thread(target=self.get_input, args=(hint,))
        t.daemon = True
        t.start()
        t.join(timeout=500)

    def get_input(self, hint):
        self.inp = input(hint)

    def get(self):
        return self.inp

class CheckPointCreds(SmartObj):
    """
        This object stores all the needed credentials that CheckPoint uses,
        such as cookies
    """
    
    def __init__(self, creds_path: str = "") -> None:
        self.cookies: Dict[str, str] = {}

        if not creds_path:
            cwd_path = Path().home()
            ghunt_folder = cwd_path / ".malfrats/checkpoint"
            if not ghunt_folder.is_dir():
                ghunt_folder.mkdir(parents=True, exist_ok=True)
            creds_path = ghunt_folder / "creds.pkl"
        self.creds_path: str = creds_path

    def are_creds_loaded(self) -> bool:
        return all([self.cookies])

    def load_creds(self, silent=False) -> bool:
        """Loads cookies"""

        try:
            cookies = pickle.load(open(self.creds_path, 'rb'))
        except FileNotFoundError:
            return False

        if cookies:
            try:
                now_timestamp = datetime.timestamp(datetime.now())
                # [{'domain': '.facebook.com', 'expiry': 1735714471, 'httpOnly': True, 'name': 'fr', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '05ph6f0hw4tuSzo9F.AWU-O3D10vsFCE9voUFq_NNXPMQ.Bm_j9b..AAA.0.0.Bm_j-m.AWU8cqDJJyc'}, {'domain': '.facebook.com', 'expiry': 1759474424, 'httpOnly': True, 'name': 'xs', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '35%3A0UNfy0QwpAuLmw%3A2%3A1727938422%3A-1%3A14476'}, {'domain': '.facebook.com', 'expiry': 1759474424, 'httpOnly': False, 'name': 'c_user', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '100007859116486'}, {'domain': '.facebook.com', 'expiry': 1728543205, 'httpOnly': False, 'name': 'locale', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'ru_RU'}, {'domain': '.facebook.com', 'httpOnly': False, 'name': 'presence', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1727938473890%2C%22v%22%3A1%7D'}, {'domain': '.facebook.com', 'expiry': 1728543273, 'httpOnly': False, 'name': 'wd', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '929x873'}, {'domain': '.facebook.com', 'expiry': 1762498397, 'httpOnly': True, 'name': 'datr', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'Wz_-ZubvX8PhEuJo2hFYXuKA'}, {'domain': '.facebook.com', 'expiry': 1762498424, 'httpOnly': True, 'name': 'sb', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'Wz_-ZluV4_krp6As8GZW3_l_'}]
                for cookie in cookies:
                    if cookie.get('expiry') and cookie['expiry'] < now_timestamp:
                        print("[-] Cookies expired")
                        return False
            except InvalidCookieDomainException:
                return False

            self.cookies = cookies
            print("[+] Stored session loaded !")
            return True
        else:
            return False


    def save_creds(self, silent=False):
        """Save cookies to the specified file."""
        pickle.dump(self.cookies, open(self.creds_path, 'wb'))
        if not silent:
            print(f"\n[+] Creds have been saved in {self.creds_path} !")



### Maps

class Position(SmartObj):
    def __init__(self):
        self.latitude: float = 0.0
        self.longitude: float = 0.0

class MapsLocation(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.address: str = ""
        self.position: Position = Position()
        self.tags: List[str] = []
        self.types: List[str] = []
        self.cost_level: int = 0 # 1-4

class MapsReview(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.comment: str = ""
        self.rating: int = 0
        self.location: MapsLocation = MapsLocation()
        self.date: datetime = None

class MapsPhoto(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.url: str = ""
        self.location: MapsLocation = MapsLocation()
        self.date: datetime = None

### Drive
class DriveExtractedUser(SmartObj):
    def __init__(self):
        self.gaia_id: str = ""
        self.name: str = ""
        self.email_address: str = ""
        self.role: str = ""
        self.is_last_modifying_user: bool = False