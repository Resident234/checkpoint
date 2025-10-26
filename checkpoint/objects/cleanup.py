import threading
from pathlib import Path
from typing import List, Set

from checkpoint import globals as gb
from checkpoint.knowledge import pauses
from checkpoint.knowledge.fs import path as fs_path, cleanup as cleanup_config
from checkpoint.helpers.utils import sleep


class CleanupManager:
    """
    Класс для управления очисткой файлов и папок
    
    Обеспечивает:
    - Автоматический мониторинг указанной директории
    - Удаление файлов по заданным паттернам
    - Удаление папок по заданным паттернам
    - Управление потоком мониторинга
    """
    
    def __init__(self, target_path: Path, file_patterns: List[str] = None, folder_patterns: List[str] = None):
        """
        Инициализация менеджера очистки
        
        Args:
            target_path: Путь к директории для мониторинга
            file_patterns: Список паттернов файлов для удаления (например, ['start_here.html', 'start_here_*.html'])
            folder_patterns: Список паттернов папок для удаления (только в корне)
        """
        self.target_path = target_path
        self.file_patterns = file_patterns or cleanup_config['file_patterns']
        self.folder_patterns = folder_patterns or cleanup_config['folder_patterns']
        self.folder_path_patterns = cleanup_config.get('folder_path_patterns', [])
        self.subfolder_cleanup_rules = cleanup_config.get('subfolder_cleanup_rules', [])
        self.monitor_running = False
        self.monitor_thread = None
        self.deleted_files: Set[str] = set()
        
    def matches_pattern(self, name: str, pattern: str) -> bool:
        """
        Проверяет, соответствует ли имя файла/папки паттерну
        
        Args:
            name: Имя файла или папки
            pattern: Паттерн для проверки (поддерживает * как wildcard)
            
        Returns:
            bool: True если имя соответствует паттерну
        """
        if '*' not in pattern:
            return name == pattern
        
        # Простая реализация wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            prefix, suffix = parts
            return name.startswith(prefix) and name.endswith(suffix)
        
        return False
    
    def should_delete_file(self, file_path: Path) -> bool:
        """
        Проверяет, нужно ли удалить файл
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True если файл нужно удалить
        """
        filename = file_path.name
        
        for pattern in self.file_patterns:
            if self.matches_pattern(filename, pattern):
                return True
        
        return False
    
    def should_delete_folder_root(self, folder_path: Path) -> bool:
        """
        Проверяет, нужно ли удалить папку в корне (только по имени)
        
        Args:
            folder_path: Путь к папке
            
        Returns:
            bool: True если папку нужно удалить
        """
        foldername = folder_path.name
        
        for pattern in self.folder_patterns:
            if self.matches_pattern(foldername, pattern):
                return True
        
        return False
    

    def cleanup_files(self) -> int:
        """
        Удаляет файлы, соответствующие паттернам
        
        Returns:
            int: Количество удаленных файлов
        """
        deleted_count = 0
        
        try:
            if not self.target_path.exists():
                gb.rc.print(f"⚠️ Директория не найдена: {self.target_path}", style="yellow")
                return 0
            
            # Ищем файлы в директории
            for item in self.target_path.iterdir():
                if item.is_file() and self.should_delete_file(item):
                    try:
                        item.unlink()
                        gb.rc.print(f"🗑️ Удален файл: {item.name}", style="green")
                        deleted_count += 1
                        self.deleted_files.add(item.name)
                    except Exception as e:
                        gb.rc.print(f"❌ Ошибка при удалении файла {item.name}: {e}", style="red")
            
            return deleted_count
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при очистке файлов: {e}", style="red")
            return deleted_count
    
    def cleanup_subfolders_with_exclusions(self) -> int:
        """
        Удаляет подпапки согласно специальным правилам с исключениями
        Работает только с папками в корне target_path
        
        Returns:
            int: Количество удаленных подпапок
        """
        deleted_count = 0
        
        try:
            if not self.target_path.exists():
                return 0
            
            for rule in self.subfolder_cleanup_rules:
                parent_folder_name = rule['parent_folder']
                exclude_subfolders = rule.get('exclude_subfolders', [])
                
                # Родительская папка должна быть в корне target_path
                parent_folder_path = self.target_path / parent_folder_name
                
                if not parent_folder_path.exists() or not parent_folder_path.is_dir():
                    continue
                
                # Перебираем только прямые подпапки (без рекурсии)
                for subfolder in parent_folder_path.iterdir():
                    if subfolder.is_dir() and subfolder.name not in exclude_subfolders:
                        try:
                            import shutil
                            shutil.rmtree(subfolder)
                            gb.rc.print(f"🗑️ Удалена подпапка: {parent_folder_name}/{subfolder.name}", style="green")
                            deleted_count += 1
                            self.deleted_files.add(f"{parent_folder_name}/{subfolder.name}")
                        except Exception as e:
                            gb.rc.print(f"❌ Ошибка при удалении подпапки {parent_folder_name}/{subfolder.name}: {e}", style="red")
            
            return deleted_count
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при очистке подпапок с исключениями: {e}", style="red")
            return deleted_count
    
    def cleanup_folders_root(self) -> int:
        """
        Удаляет папки в корне target_path, соответствующие паттернам
        
        Returns:
            int: Количество удаленных папок
        """
        deleted_count = 0
        
        try:
            if not self.target_path.exists():
                gb.rc.print(f"⚠️ Директория не найдена: {self.target_path}", style="yellow")
                return 0
            
            # Ищем папки только в корне директории
            for item in self.target_path.iterdir():
                if item.is_dir() and self.should_delete_folder_root(item):
                    try:
                        import shutil
                        shutil.rmtree(item)
                        gb.rc.print(f"🗑️ Удалена папка (корень): {item.name}", style="green")
                        deleted_count += 1
                        self.deleted_files.add(item.name)
                    except Exception as e:
                        gb.rc.print(f"❌ Ошибка при удалении папки {item.name}: {e}", style="red")
            
            return deleted_count
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при очистке папок в корне: {e}", style="red")
            return deleted_count
    
    def cleanup_folders_by_path(self) -> int:
        """
        Удаляет папки по полному пути (только на уровне 1-2 от корня)
        Например: connections/followers - проверяет только H:/connections/followers
        
        Returns:
            int: Количество удаленных папок
        """
        deleted_count = 0
        
        try:
            if not self.target_path.exists():
                return 0
            
            # Проходим по каждому паттерну пути
            for pattern in self.folder_path_patterns:
                # Разбиваем путь на части (например, "connections/followers" -> ["connections", "followers"])
                parts = pattern.split('/')
                
                # Строим полный путь от target_path
                folder_path = self.target_path
                for part in parts:
                    folder_path = folder_path / part
                
                # Проверяем, существует ли эта папка, и удаляем её
                if folder_path.exists() and folder_path.is_dir():
                    try:
                        import shutil
                        relative_path = folder_path.relative_to(self.target_path)
                        shutil.rmtree(folder_path)
                        gb.rc.print(f"🗑️ Удалена папка (по пути): {relative_path}", style="green")
                        deleted_count += 1
                        self.deleted_files.add(str(relative_path))
                    except Exception as e:
                        gb.rc.print(f"❌ Ошибка при удалении папки {pattern}: {e}", style="red")
            
            return deleted_count
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при очистке папок по пути: {e}", style="red")
            return deleted_count
    
    def monitor_cleanup(self) -> None:
        """
        Мониторит директорию и периодически выполняет очистку
        """
        gb.rc.print(f"🔍 Запущен мониторинг очистки в: {self.target_path}", style="blue")
        gb.rc.print(f"📋 Паттерны файлов (корень): {self.file_patterns}", style="cyan")
        gb.rc.print(f"📋 Паттерны папок (корень): {self.folder_patterns}", style="cyan")
        if self.folder_path_patterns:
            gb.rc.print(f"📋 Паттерны папок (по пути): {self.folder_path_patterns}", style="cyan")
        if self.subfolder_cleanup_rules:
            gb.rc.print(f"📋 Правила очистки подпапок: {self.subfolder_cleanup_rules}", style="cyan")
        task_name = "CleanupManager"
        
        while self.monitor_running:
            try:
                # Проверяем глобальную переменную синхронизации перед началом работы
                if not gb.task_sync.can_run_task(task_name):
                    gb.rc.print(f"⏸️ CleanupManager: ожидание завершения {gb.task_sync.get_current_running_task()}", style="yellow")
                    sleep(pauses.cleanup['monitor_cycle'], "Пауза - ожидание освобождения таска")
                    continue
                
                # Устанавливаем себя как активный таск
                if not gb.task_sync.is_task_running():
                    gb.task_sync.set_current_running_task(task_name)
                    gb.rc.print(f"▶️ CleanupManager: начало выполнения", style="green")
                
                # Выполняем очистку файлов (только в корне)
                files_deleted = self.cleanup_files()
                
                # Выполняем очистку папок в корне
                folders_deleted_root = self.cleanup_folders_root()
                
                # Выполняем очистку папок по полному пути (рекурсивно)
                folders_deleted_path = self.cleanup_folders_by_path()
                
                # Выполняем очистку подпапок с исключениями
                subfolders_deleted = self.cleanup_subfolders_with_exclusions()
                
                total_folders = folders_deleted_root + folders_deleted_path + subfolders_deleted
                if files_deleted > 0 or total_folders > 0:
                    gb.rc.print(f"✅ Очистка завершена: удалено {files_deleted} файлов и {total_folders} папок", style="green")
                
                # Освобождаем глобальную переменную перед паузой
                if gb.task_sync.is_task_running(task_name):
                    gb.task_sync.set_current_running_task(None)
                    gb.rc.print(f"⏸️ CleanupManager: переход в паузу", style="cyan")
                
                # Пауза между проверками
                sleep(pauses.cleanup['monitor_cycle'], "Пауза между циклами очистки")
                
            except Exception as e:
                gb.rc.print(f"❌ Ошибка в мониторе очистки: {e}", style="red")
                # Освобождаем глобальную переменную при ошибке
                if gb.task_sync.is_task_running(task_name):
                    gb.task_sync.set_current_running_task(None)
                sleep(pauses.cleanup['error_recovery'], "Восстановление после ошибки в очистке")
        
        # Освобождаем глобальную переменную при завершении работы
        if gb.task_sync.is_task_running(task_name):
            gb.task_sync.set_current_running_task(None)
        
        gb.rc.print("🛑 Мониторинг очистки остановлен", style="red")
    
    def start_monitor(self) -> None:
        """
        Запускает поток мониторинга очистки
        """
        if not self.monitor_running:
            self.monitor_running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_cleanup,
                daemon=True,
                name="CleanupMonitorThread"
            )
            self.monitor_thread.start()
            gb.rc.print("🚀 Поток мониторинга очистки запущен", style="green")
    
    def stop_monitor(self) -> None:
        """
        Останавливает поток мониторинга очистки
        """
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            gb.rc.print("🛑 Поток мониторинга очистки остановлен", style="red")
    
    def is_monitoring(self) -> bool:
        """
        Проверяет, активен ли мониторинг
        
        Returns:
            bool: True если мониторинг активен
        """
        return self.monitor_running
