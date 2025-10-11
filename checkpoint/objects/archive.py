import os
import shutil
import threading
import zipfile
from pathlib import Path
from typing import Set

from checkpoint import globals as gb
from checkpoint.knowledge import pauses
from checkpoint.knowledge.fs import path as fs_path
from checkpoint.helpers.utils import sleep
from checkpoint.helpers.fs import get_unique_filename, merge_directories


class ArchiveManager:
    """
    Класс для управления архивами и мониторинга ZIP файлов
    
    Обеспечивает:
    - Автоматический мониторинг папки загрузок на наличие ZIP файлов
    - Извлечение архивов с разрешением конфликтов имен
    - Объединение директорий при конфликтах
    - Управление потоком мониторинга
    """
    
    def __init__(self, download_path: Path):
        """
        Инициализация менеджера архивов
        
        Args:
            download_path: Путь к папке загрузок для мониторинга
        """
        self.download_path = download_path
        self.to_delete_dir = download_path / fs_path['to_delete_dir']
        self.monitor_running = False
        self.monitor_thread = None
        self.processed_files: Set[str] = set()
    
    # get_unique_filename method moved to checkpoint.helpers.fs for centralized file utilities
    
    # merge_directories method moved to checkpoint.helpers.fs for centralized file utilities
    
    def extract_zip_archive(self, zip_path: Path) -> bool:
        """
        Извлекает ZIP архив и перемещает его в папку to_delete
        
        Args:
            zip_path: Путь к ZIP файлу
            
        Returns:
            bool: True если успешно, False при ошибке
        """
        try:
            gb.rc.print(f"📦 Начинаем извлечение: {zip_path.name}", style="cyan")
            
            # Создаем временную папку для извлечения
            temp_extract_dir = self.download_path / f"temp_extract_{zip_path.stem}"
            temp_extract_dir.mkdir(exist_ok=True)
            
            # Извлекаем архив во временную папку
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            # Перемещаем содержимое из временной папки в основную
            for item in temp_extract_dir.iterdir():
                target_item = self.download_path / item.name
                
                if item.is_file():
                    if target_item.exists():
                        unique_target = get_unique_filename(target_item)
                        shutil.move(str(item), str(unique_target))
                        gb.rc.print(f"📄 Файл переименован: {item.name} → {unique_target.name}", style="yellow")
                    else:
                        shutil.move(str(item), str(target_item))
                elif item.is_dir():
                    if target_item.exists():
                        gb.rc.print(f"📁 Объединение папок: {item.name}", style="cyan")
                        merge_directories(item, target_item)
                    else:
                        shutil.move(str(item), str(target_item))
            
            # Удаляем временную папку
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            
            # Перемещаем архив в папку to_delete
            self.to_delete_dir.mkdir(exist_ok=True)
            archive_target = self.to_delete_dir / zip_path.name
            
            # Если файл с таким именем уже существует в to_delete, создаем уникальное имя
            if archive_target.exists():
                archive_target = get_unique_filename(archive_target)
            
            shutil.move(str(zip_path), str(archive_target))
            gb.rc.print(f"✅ Архив обработан и перемещен: {zip_path.name} → {archive_target.name}", style="green")
            
            return True
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при извлечении {zip_path.name}: {e}", style="red")
            return False
    
    def monitor_zip_files(self) -> None:
        """
        Мониторит папку загрузок на наличие ZIP файлов и обрабатывает их
        """
        gb.rc.print(f"🔍 Запущен мониторинг ZIP файлов в: {self.download_path}", style="blue")
        
        while self.monitor_running:
            try:
                # Ищем все ZIP файлы в папке загрузок
                zip_files = list(self.download_path.glob("*.zip"))
                
                for zip_file in zip_files:
                    # Проверяем, не обрабатывали ли мы уже этот файл
                    if zip_file.name not in self.processed_files:
                        # Проверяем, что файл полностью загружен (не изменяется)
                        initial_size = zip_file.stat().st_size
                        sleep(pauses.archive['file_stability_check'], "Проверка стабильности размера ZIP файла")
                        
                        if zip_file.exists() and zip_file.stat().st_size == initial_size:
                            # Файл стабилен, можно обрабатывать
                            if self.extract_zip_archive(zip_file):
                                self.processed_files.add(zip_file.name)
                        else:
                            gb.rc.print(f"⏳ Файл {zip_file.name} еще загружается...", style="yellow")
                
                # Пауза между проверками
                sleep(pauses.archive['monitor_cycle'], "Пауза между циклами мониторинга ZIP файлов")
                
            except Exception as e:
                gb.rc.print(f"❌ Ошибка в мониторе ZIP файлов: {e}", style="red")
                sleep(pauses.archive['error_recovery'], "Восстановление после ошибки в мониторинге")  # Увеличенная пауза при ошибке
        
        gb.rc.print("🛑 Мониторинг ZIP файлов остановлен", style="red")
    
    def start_monitor(self) -> None:
        """
        Запускает поток мониторинга ZIP файлов
        """
        if not self.monitor_running:
            self.monitor_running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_zip_files,
                daemon=True,
                name="ArchiveMonitorThread"
            )
            self.monitor_thread.start()
            gb.rc.print("🚀 Поток мониторинга ZIP файлов запущен", style="green")
    
    def stop_monitor(self) -> None:
        """
        Останавливает поток мониторинга ZIP файлов
        """
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            gb.rc.print("🛑 Поток мониторинга ZIP файлов остановлен", style="red")
    
    def is_monitoring(self) -> bool:
        """
        Проверяет, активен ли мониторинг
        
        Returns:
            bool: True если мониторинг активен
        """
        return self.monitor_running
