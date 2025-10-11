import os
import re
import shutil
import threading
from pathlib import Path
from typing import Set

from checkpoint import globals as gb
from checkpoint.knowledge import pauses
from checkpoint.helpers.utils import sleep
from checkpoint.helpers.fs import get_unique_filename, merge_directories, clean_folder_name


class MediaManager:
    """
    Класс для обработки медиа папок Facebook
    
    Обеспечивает:
    - Мониторинг папки your_facebook_activity/posts/media
    - Очистка имен папок от случайных суффиксов
    - Объединение папок с одинаковыми именами
    - Перемещение папок в директорию PHOTO
    """
    
    def __init__(self, media_path: Path, photo_path: Path):
        """
        Инициализация менеджера медиа
        
        Args:
            media_path: Путь к папке your_facebook_activity/posts/media
            photo_path: Путь к папке PHOTO (по умолчанию: на том же уровне что и your_facebook_activity)
        """
        self.media_path = media_path
        self.photo_path = photo_path
        self.monitor_running = False
        self.monitor_thread = None
        self.processed_folders: Set[str] = set()
    
    def process_folder(self, folder_path: Path) -> bool:
        """
        Обрабатывает отдельную папку: переименовывает и перемещает в PHOTO
        
        Args:
            folder_path: Путь к папке для обработки
            
        Returns:
            bool: True если успешно, False при ошибке
        """
        try:
            original_name = folder_path.name
            cleaned_name = clean_folder_name(original_name)
            
            # Если имя не изменилось, значит суффикса не было
            if original_name == cleaned_name:
                gb.rc.print(f"📁 Папка уже имеет чистое имя: {original_name}", style="blue")
            else:
                gb.rc.print(f"🔧 Очистка имени папки: {original_name} → {cleaned_name}", style="cyan")
                
                # Переименовываем папку в той же директории
                new_folder_path = folder_path.parent / cleaned_name
                
                if new_folder_path.exists():
                    # Папка с таким именем уже существует, объединяем
                    gb.rc.print(f"📁 Объединение с существующей папкой: {cleaned_name}", style="yellow")
                    merge_directories(folder_path, new_folder_path)
                    if folder_path.exists():
                        shutil.rmtree(str(folder_path))
                        gb.rc.print(f"🗑️ Исходная папка удалена: {folder_path.name}", style="cyan")
                else:
                    # Просто переименовываем
                    folder_path.rename(new_folder_path)
                
                folder_path = new_folder_path
            
            # Создаем папку PHOTO если не существует
            self.photo_path.mkdir(exist_ok=True)
            
            # Перемещаем папку в PHOTO
            photo_target = self.photo_path / folder_path.name
            
            if photo_target.exists():
                # Папка уже существует в PHOTO, объединяем
                gb.rc.print(f"📁 Объединение с папкой в {self.photo_path}: {folder_path.name}", style="yellow")
                merge_directories(folder_path, photo_target)
                # Удаляем исходную папку после объединения
                if folder_path.exists():
                    shutil.rmtree(str(folder_path))
                    gb.rc.print(f"🗑️ Исходная папка удалена: {folder_path.name}", style="cyan")
            else:
                # Перемещаем папку в PHOTO
                shutil.move(str(folder_path), str(photo_target))
                gb.rc.print(f"📦 Папка перемещена в {self.photo_path}: {folder_path.name}", style="green")
                # Проверяем и удаляем исходную папку, если она осталась
                if folder_path.exists():
                    shutil.rmtree(str(folder_path))
                    gb.rc.print(f"🗑️ Исходная папка удалена: {folder_path.name}", style="cyan")
            
            return True
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при обработке папки {folder_path.name}: {e}", style="red")
            return False
    
    def monitor_media_folders(self) -> None:
        """
        Мониторит папку медиа и обрабатывает новые папки
        """
        gb.rc.print(f"🔍 Запущен мониторинг медиа папок в: {self.media_path}", style="blue")
        
        while self.monitor_running:
            try:
                if not self.media_path.exists():
                    gb.rc.print(f"⚠️ Папка медиа не найдена: {self.media_path}", style="yellow")
                    sleep(pauses.media['folder_scan'], "Ожидание появления папки медиа")
                    continue
                
                # Ищем все папки в директории медиа
                media_folders = [item for item in self.media_path.iterdir() if item.is_dir()]
                
                for folder in media_folders:
                    # Проверяем, не обрабатывали ли мы уже эту папку
                    if folder.name not in self.processed_folders:
                        gb.rc.print(f"🆕 Найдена новая папка для обработки: {folder.name}", style="cyan")
                        
                        if self.process_folder(folder):
                            self.processed_folders.add(folder.name)
                        
                        # Пауза между обработкой папок
                        sleep(pauses.media['processing_cycle'], "Пауза между обработкой папок медиа")
                
                # Пауза между сканированием
                sleep(pauses.media['folder_scan'], "Пауза между сканированием папок медиа")
                
            except Exception as e:
                gb.rc.print(f"❌ Ошибка в мониторе медиа папок: {e}", style="red")
                sleep(pauses.media['error_recovery'], "Восстановление после ошибки в мониторинге медиа")
        
        gb.rc.print("🛑 Мониторинг медиа папок остановлен", style="red")
    
    def start_monitor(self) -> None:
        """
        Запускает поток мониторинга медиа папок
        """
        if not self.monitor_running:
            self.monitor_running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_media_folders,
                daemon=True,
                name="MediaProcessorThread"
            )
            self.monitor_thread.start()
            gb.rc.print("🚀 Поток мониторинга медиа папок запущен", style="green")
    
    def stop_monitor(self) -> None:
        """
        Останавливает поток мониторинга медиа папок
        """
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            gb.rc.print("🛑 Поток мониторинга медиа папок остановлен", style="red")
    
    def is_monitoring(self) -> bool:
        """
        Проверяет, активен ли мониторинг
        
        Returns:
            bool: True если мониторинг активен
        """
        return self.monitor_running
