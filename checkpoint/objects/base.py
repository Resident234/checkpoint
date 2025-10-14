import pickle
from types import FrameType
from typing import *
from pathlib import Path
from datetime import datetime
import os
import threading
import inspect
from typing import TextIO

from threading import Thread
from typing import Any
from typing import Literal, LiteralString
from rich.console import Console

from selenium.common import InvalidCookieDomainException
from checkpoint.helpers.fs import get_temp_path



# class SmartObj(Slots): # Not Python 3.13 compatible so FUCK it fr fr
#     pass

class SmartObj():
    pass

class Inp:
    inp = None

    def __init__(self, hint=None):
        t = Thread(target=self.get_input, args=(hint,), name="UserInputThread")
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
        self.cookies: List[dict] = []

        if not creds_path:
            # Use temporary directory instead of home directory
            creds_path = get_temp_path("creds.pkl")
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


class DualConsole:
    """Console wrapper that outputs to both terminal and log file"""
    
    def __init__(self, highlight=True):
        # Основная консоль для терминала
        self.console: Any = Console(highlight=highlight)
        
        # Создаем директорию для логов в корне проекта (рядом с папкой checkpoint)
        current_file: Path = Path(__file__)
        project_root: Path = current_file.parent.parent.parent  # checkpoint/objects/base.py -> CheckPoint/
        self.log_dir: Path = project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Создаем файл лога с текущей датой и временем
        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path: Path = self.log_dir / f"checkpoint_{timestamp}.log"
        
        # Консоль для файла (без стилей для читаемости)
        self.log_file: TextIO = open(self.log_file_path, "w", encoding="utf-8")
        self.file_console: Any = Console(file=self.log_file, highlight=False, width=120)
        
        # Записываем заголовок в лог
        self._log_header()
    
    def _log_header(self):
        """Записывает заголовок в лог файл"""
        header: str = f"""
{'='*80}
CheckPoint Application Log
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Log file: {self.log_file_path}
{'='*80}
"""
        self.file_console.print(header)
    
    def _get_thread_module_prefix(self) -> LiteralString | Literal['']:
        """Получает префикс для потока и модуля"""
        # Получаем информацию о текущем потоке
        current_thread: Thread = threading.current_thread()
        thread_name: str = current_thread.name
        
        # Получаем имя модуля из глобальной переменной
        try:
            from checkpoint import globals as gb
            module_name = gb.current_module_name
        except:
            module_name = "Unknown"
        
        # Формируем префикс
        prefix_parts = []
        
        # Добавляем имя потока, если это не MainThread
        if thread_name != "MainThread":
            prefix_parts.append(f"T:{thread_name}")
        
        # Добавляем имя модуля
        if module_name != "Unknown":
            prefix_parts.append(f"M:{module_name}")
        
        if prefix_parts:
            return f"[{' | '.join(prefix_parts)}] "
        return ""
    
    def print(self, *args, **kwargs):
        """Выводит сообщение и в консоль, и в лог файл с префиксами потока и модуля"""
        # Получаем префикс для потока и модуля
        thread_module_prefix: LiteralString | Literal[''] = self._get_thread_module_prefix()
        
        # Подготавливаем аргументы с префиксом для терминала
        if args:
            prefixed_first_arg: str = f"{thread_module_prefix}{args[0]}"
            terminal_args: tuple[LiteralString | Literal['']] = (prefixed_first_arg,) + args[1:]
        else:
            terminal_args: tuple[LiteralString | Literal['']] = (thread_module_prefix,)
        
        # Вывод в терминал с префиксом
        self.console.print(*terminal_args, **kwargs)
        
        # Вывод в файл с временной меткой и префиксом
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        if args:
            # Добавляем временную метку и префикс к первому аргументу
            first_arg: str = f"[{timestamp}] {thread_module_prefix}{args[0]}"
            file_args: tuple[str, *tuple[Any, ...]] = (first_arg,) + args[1:]
            self.file_console.print(*file_args, **kwargs)
        else:
            self.file_console.print(f"[{timestamp}] {thread_module_prefix}", **kwargs)
    
    def close(self):
        """Закрывает лог файл"""
        if hasattr(self, 'log_file') and not self.log_file.closed:
            self.file_console.print(f"\nLog ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_file.close()
    
    def __del__(self):
        """Автоматически закрывает файл при удалении объекта"""
        self.close()
    
    def get_current_log_path(self):
        """Возвращает путь к текущему лог-файлу"""
        return getattr(self, 'log_file_path', None)
    
    @staticmethod
    def cleanup_old_logs(days_to_keep=70):
        """Удаляет старые лог-файлы
        
        Args:
            days_to_keep (int): Количество дней для хранения логов
        """
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # checkpoint/objects/base.py -> CheckPoint/
        log_dir = project_root / "logs"
        if not log_dir.exists():
            return
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in log_dir.glob("checkpoint_*.log"):
            try:
                # Получаем время создания файла
                file_time = datetime.fromtimestamp(log_file.stat().st_ctime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    print(f"Удален старый лог-файл: {log_file}")
            except Exception as e:
                print(f"Ошибка при удалении лог-файла {log_file}: {e}")