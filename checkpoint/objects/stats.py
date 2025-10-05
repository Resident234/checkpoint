import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from checkpoint import globals as gb
from checkpoint.knowledge import pauses
from checkpoint.helpers.utils import sleep


class PhotoStatsManager:
    """
    Класс для сбора статистики файлов в папке PHOTO
    
    Обеспечивает:
    - Мониторинг папки PHOTO каждый час
    - Анализ файлов по дате добавления
    - Разделение на новые файлы и дубли (с суффиксами _2, _3 и т.д.)
    - Запись статистики в ежедневные лог-файлы
    """
    
    def __init__(self, photo_path: Path, stats_logs_path: Path):
        """
        Инициализация менеджера статистики
        
        Args:
            photo_path: Путь к папке PHOTO
            stats_logs_path: Путь к папке для логов статистики
        """
        self.photo_path = photo_path
        self.stats_logs_path = stats_logs_path
        self.monitor_running = False
        self.monitor_thread = None
        
        # Создаем папку для логов статистики если не существует
        self.stats_logs_path.mkdir(exist_ok=True)
    
    def is_duplicate_file(self, filename: str) -> bool:
        """
        Проверяет, является ли файл дублем (имеет суффикс _2, _3 и т.д.)
        
        Args:
            filename: Имя файла для проверки
            
        Returns:
            bool: True если файл является дублем
        """
        # Паттерн для поиска суффикса дубля: _число перед расширением
        pattern = r'_\d+\.[^.]+$'
        return bool(re.search(pattern, filename))
    
    def get_files_added_today(self) -> Tuple[int, int]:
        """
        Подсчитывает файлы, добавленные сегодня в папку PHOTO
        
        Returns:
            Tuple[int, int]: (количество новых файлов, количество дублей)
        """
        if not self.photo_path.exists():
            gb.rc.print(f"⚠️ Папка {self.photo_path} не найдена", style="yellow")
            return 0, 0
        
        today = datetime.now().date()
        new_files_count = 0
        duplicate_files_count = 0
        
        try:
            # Рекурсивно проходим по всем файлам в папке PHOTO
            for root, dirs, files in os.walk(self.photo_path):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Получаем дату добавления файла (время создания или изменения)
                    try:
                        # Используем время создания файла
                        creation_time = os.path.getctime(file_path)
                        file_date = datetime.fromtimestamp(creation_time).date()
                        
                        # Проверяем, был ли файл добавлен сегодня
                        if file_date == today:
                            if self.is_duplicate_file(file):
                                duplicate_files_count += 1
                            else:
                                new_files_count += 1
                    
                    except (OSError, ValueError) as e:
                        gb.rc.print(f"⚠️ Ошибка при получении даты файла {file_path}: {e}", style="yellow")
                        continue
            
            return new_files_count, duplicate_files_count
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при сканировании папки {self.photo_path}: {e}", style="red")
            return 0, 0
    
    def write_daily_stats(self, new_files: int, duplicates: int) -> None:
        """
        Записывает статистику в ежедневный лог-файл
        
        Args:
            new_files: Количество новых файлов
            duplicates: Количество дублей
        """
        try:
            # Формируем имя файла в формате DD.MM.YYYY.log
            today = datetime.now()
            log_filename = today.strftime("%d.%m.%Y.log")
            log_file_path = self.stats_logs_path / log_filename
            
            # Формируем запись статистики
            stats_entry = f"{today.strftime('%d.%m.%Y')} новых файлов {new_files}, дублей {duplicates}\n"
            
            # Перезаписываем файл (каждый день новый файл, в течение дня перезаписываем)
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(stats_entry)
            
            gb.rc.print(f"📊 Статистика записана в {log_filename}: новых {new_files}, дублей {duplicates}", style="green")
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при записи статистики: {e}", style="red")
    
    def collect_and_log_stats(self) -> None:
        """
        Собирает статистику и записывает в лог
        """
        gb.rc.print(f"📊 Начинаем сбор статистики файлов {self.photo_path}...", style="blue")
        
        try:
            # Получаем количество новых файлов и дублей за сегодня
            new_files, duplicates = self.get_files_added_today()
            
            # Записываем статистику в лог
            self.write_daily_stats(new_files, duplicates)
            
            gb.rc.print(f"✅ Статистика собрана: новых файлов {new_files}, дублей {duplicates}", style="green")
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при сборе статистики: {e}", style="red")
    
    def monitor_photo_stats(self) -> None:
        """
        Мониторит статистику файлов каждый час
        """
        gb.rc.print(f"📊 Запущен мониторинг статистики в {self.photo_path}", style="blue")
        
        while self.monitor_running:
            try:
                # Собираем и записываем статистику
                self.collect_and_log_stats()
                
                # Ждем час до следующей проверки
                sleep(pauses.stats['hourly_check'], "Ожидание до следующего сбора статистики")
                
            except Exception as e:
                gb.rc.print(f"❌ Ошибка в мониторе статистики: {e}", style="red")
                sleep(pauses.stats['error_recovery'], "Восстановление после ошибки в мониторинге статистики")
        
        gb.rc.print("🛑 Мониторинг статистики остановлен", style="red")
    
    def start_monitor(self) -> None:
        """
        Запускает поток мониторинга статистики
        """
        if not self.monitor_running:
            self.monitor_running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_photo_stats,
                daemon=True,
                name="PhotoStatsThread"
            )
            self.monitor_thread.start()
            gb.rc.print("🚀 Поток мониторинга статистики запущен", style="green")
    
    def stop_monitor(self) -> None:
        """
        Останавливает поток мониторинга статистики
        """
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            gb.rc.print("🛑 Поток мониторинга статистики остановлен", style="red")
    
    def is_monitoring(self) -> bool:
        """
        Проверяет, активен ли мониторинг статистики
        
        Returns:
            bool: True если мониторинг активен
        """
        return self.monitor_running
