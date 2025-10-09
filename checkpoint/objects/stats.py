import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, List, Optional

from checkpoint import globals as gb
from checkpoint.knowledge import pauses
from checkpoint.helpers.utils import sleep
from checkpoint.helpers.email import send_notification_email
from checkpoint import config


class PhotoStatsManager:
    """
    Класс для сбора статистики файлов в папке PHOTO
    
    Обеспечивает:
    - Мониторинг папки PHOTO каждый час
    - Анализ файлов по дате добавления
    - Разделение на новые файлы и дубли (с суффиксами _2, _3 и т.д.)
    - Запись статистики в ежедневные лог-файлы
    """
    
    def __init__(self, photo_path: Path, stats_logs_path: Path, send_email: bool = False, email_to: Optional[str] = None):
        """
        Инициализация менеджера статистики
        
        Args:
            photo_path: Путь к папке PHOTO
            stats_logs_path: Путь к папке для логов статистики
            send_email: Отправлять ли статистику на email автоматически
            email_to: Email получателя (по умолчанию из config.NOTIFY_EMAIL)
        """
        self.photo_path = photo_path
        self.stats_logs_path = stats_logs_path
        self.send_email = send_email
        self.email_to = email_to
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
    
    def get_files_added_today(self) -> Tuple[int, int, List[str], List[str]]:
        """
        Подсчитывает файлы, добавленные сегодня в папку PHOTO
        
        Returns:
            Tuple[int, int, List[str], List[str]]: (
                количество новых файлов, количество дублей,
                список имен новых файлов, список имен дублей
            )
        """
        if not self.photo_path.exists():
            gb.rc.print(f"⚠️ Папка {self.photo_path} не найдена", style="yellow")
            return 0, 0, [], []
        
        today = datetime.now().date()
        new_files_count = 0
        duplicate_files_count = 0
        new_file_names: List[str] = []
        duplicate_file_names: List[str] = []
        
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
                                duplicate_file_names.append(str(file_path))
                            else:
                                new_files_count += 1
                                new_file_names.append(str(file_path))
                    
                    except (OSError, ValueError) as e:
                        gb.rc.print(f"⚠️ Ошибка при получении даты файла {file_path}: {e}", style="yellow")
                        continue
            
            return new_files_count, duplicate_files_count, new_file_names, duplicate_file_names
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при сканировании папки {self.photo_path}: {e}", style="red")
            return 0, 0, [], []
    
    def write_daily_stats(
        self, 
        new_files: int, 
        duplicates: int, 
        new_names: Optional[List[str]] = None, 
        dup_names: Optional[List[str]] = None
    ) -> None:
        """
        Записывает статистику в ежедневный лог-файл
        
        Args:
            new_files: Количество новых файлов
            duplicates: Количество дублей
            new_names: Список имен новых файлов
            dup_names: Список имен дублированных файлов
        """
        try:
            # Формируем имя файла в формате DD.MM.YYYY.log
            today = datetime.now()
            log_filename = today.strftime("%d.%m.%Y.log")
            log_file_path = self.stats_logs_path / log_filename
            
            # Формируем запись статистики (шапка)
            stats_lines = [f"{today.strftime('%d.%m.%Y')} новых файлов {new_files}, дублей {duplicates}"]
            
            # Добавляем поименные списки, если переданы
            if new_names:
                stats_lines.append("Новые файлы:")
                stats_lines.extend([f"  - {name}" for name in new_names])
            if dup_names:
                stats_lines.append("Дубли:")
                stats_lines.extend([f"  - {name}" for name in dup_names])
            
            stats_entry = "\n".join(stats_lines) + "\n"
            
            # Перезаписываем файл (каждый день новый файл, в течение дня перезаписываем)
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(stats_entry)
            
            gb.rc.print(f"📊 Статистика записана в {log_filename}: новых файлов {new_files}, дублей {duplicates}", style="green")
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при записи статистики: {e}", style="red")
    
    def print_daily_stats(
        self, 
        new_files: int, 
        duplicates: int, 
        new_names: Optional[List[str]] = None, 
        dup_names: Optional[List[str]] = None
    ) -> None:
        """
        Выводит поименные списки новых файлов и дублей
        
        Args:
            new_files: Количество новых файлов
            duplicates: Количество дублей
            new_names: Список имен новых файлов
            dup_names: Список имен дублированных файлов
        """
        try:
            # Поименно выводим списки файлов, если они есть
            if new_names:
                gb.rc.print("🆕 Новые файлы:", style="blue")
                for name in new_names:
                    gb.rc.print(f"  - {name}", style="blue")
            if dup_names:
                gb.rc.print("♻️ Дубли:", style="yellow")
                for name in dup_names:
                    gb.rc.print(f"  - {name}", style="yellow")
                
            
            gb.rc.print(f"✅ Статистика собрана: новых файлов {new_files}, дублей {duplicates}", style="green")

        except Exception as e:
            gb.rc.print(f"❌ Ошибка при выводе списков файлов: {e}", style="red")
    
    def send_stats_email(
        self, 
        to_email: str,
        new_files: int, 
        duplicates: int, 
        new_names: Optional[List[str]] = None, 
        dup_names: Optional[List[str]] = None
    ) -> bool:
        """
        Отправляет статистику на email
        
        Args:
            to_email: Email получателя
            new_files: Количество новых файлов
            duplicates: Количество дублей
            new_names: Список имен новых файлов
            dup_names: Список имен дублированных файлов
            
        Returns:
            bool: True если email успешно отправлен
        """
        try:
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            today_date = datetime.now().strftime("%d.%m.%Y")
            
            subject = f"CheckPoint: Статистика файлов за {today_date}"
            
            # Формируем основную статистику
            message_lines = [
                "Ежедневная статистика файлов CheckPoint",
                "",
                f"Дата: {today_date}",
                f"Время отчета: {current_time}",
                f"Папка мониторинга: {self.photo_path}",
                "",
                "📊 СТАТИСТИКА:",
                f"🆕 Новых файлов: {new_files}",
                f"♻️ Дублированных файлов: {duplicates}",
                f"📁 Всего обработано: {new_files + duplicates}",
                ""
            ]
            
            # Добавляем списки файлов, если они есть
            if new_names and len(new_names) > 0:
                message_lines.extend([
                    "🆕 НОВЫЕ ФАЙЛЫ:",
                    ""
                ])
                for i, name in enumerate(new_names, 1):
                    message_lines.append(f"{i:3d}. {name}")
                message_lines.append("")
            
            if dup_names and len(dup_names) > 0:
                message_lines.extend([
                    "♻️ ДУБЛИРОВАННЫЕ ФАЙЛЫ:",
                    ""
                ])
                for i, name in enumerate(dup_names, 1):
                    message_lines.append(f"{i:3d}. {name}")
                message_lines.append("")
            
            # Завершаем сообщение
            message_lines.extend([
                "---",
                "Это автоматический отчет от CheckPoint",
                f"Логи сохранены в: {self.stats_logs_path}"
            ])
            
            message = "\n".join(message_lines)
            
            # Отправляем email
            success = send_notification_email(to_email, subject, message)
            
            if success:
                gb.rc.print(f"📧 Статистика отправлена на email {to_email}", style="green")
            else:
                gb.rc.print(f"❌ Ошибка отправки статистики на email {to_email}", style="red")
                
            return success
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при отправке статистики на email: {e}", style="red")
            return False
    
    def collect_and_log_stats(self) -> None:
        """
        Собирает статистику и записывает в лог
        Отправка email определяется настройками конструктора
        """
        gb.rc.print(f"📊 Начинаем сбор статистики файлов {self.photo_path}...", style="blue")
        
        try:
            # Получаем количество новых файлов и дублей за сегодня
            new_files, duplicates, new_names, dup_names = self.get_files_added_today()
            
            # Записываем статистику в лог (включая списки файлов)
            self.write_daily_stats(new_files, duplicates, new_names, dup_names)

            # Выводим статистику в консоль
            self.print_daily_stats(new_files, duplicates, new_names, dup_names)
            
            # Отправляем по email, если требуется
            if self.send_email:
                # Определяем email получателя
                recipient_email = self.email_to or config.NOTIFY_EMAIL
                if recipient_email:
                    self.send_stats_email(recipient_email, new_files, duplicates, new_names, dup_names)
                else:
                    gb.rc.print("⚠️ Email получатель не указан. Проверьте config.NOTIFY_EMAIL", style="yellow")
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при сборе статистики: {e}", style="red")
    
    def send_current_stats_email(self, email_to: Optional[str] = None) -> bool:
        """
        Отправляет текущую статистику на email
        
        Args:
            email_to: Email получателя (по умолчанию из config.NOTIFY_EMAIL)
            
        Returns:
            bool: True если email успешно отправлен
        """
        try:
            gb.rc.print("📧 Подготовка статистики для отправки на email...", style="blue")
            
            # Получаем статистику
            new_files, duplicates, new_names, dup_names = self.get_files_added_today()
            
            # Определяем email получателя
            recipient_email = email_to or config.NOTIFY_EMAIL
            if not recipient_email:
                gb.rc.print("❌ Email получатель не указан. Проверьте config.NOTIFY_EMAIL", style="red")
                return False
            
            # Отправляем email
            return self.send_stats_email(recipient_email, new_files, duplicates, new_names, dup_names)
            
        except Exception as e:
            gb.rc.print(f"❌ Ошибка при отправке статистики на email: {e}", style="red")
            return False
    
    def collect_and_email_stats(self) -> None:
        """
        Собирает статистику, записывает в лог и отправляет на email
        Примечание: Настройки email берутся из конструктора
        """
        # Временно включаем email для этого вызова
        original_send_email = self.send_email
        self.send_email = True
        try:
            self.collect_and_log_stats()
        finally:
            self.send_email = original_send_email
    
    def monitor_photo_stats(self) -> None:
        """
        Мониторит статистику файлов каждый час
        Настройки email берутся из конструктора
        """
        gb.rc.print(f"📊 Запущен мониторинг статистики в {self.photo_path}", style="blue")
        if self.send_email:
            recipient = self.email_to or config.NOTIFY_EMAIL
            gb.rc.print(f"📧 Email уведомления: включены на {recipient}", style="blue")
        
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
        Настройки email берутся из конструктора
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
