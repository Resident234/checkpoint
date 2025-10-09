import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from datetime import datetime

import requests

from checkpoint import config
from checkpoint.knowledge import external
from checkpoint import globals as gb


def send_notification_email(to_email: str, subject: str, message: str):
    """
    Отправляет уведомление на email
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        message: Текст сообщения
    
    Инструкция по получению App Password для Gmail:
    1. Перейдите на https://myaccount.google.com/security
    2. Включите двухфакторную аутентификацию
    3. Перейдите в "App passwords" (Пароли приложений)
    4. Создайте новый пароль для "Mail"
    5. Используйте полученный 16-значный пароль
    """

    try:
        # Конфигурация берется из настроек приложения
        smtp_server = external.email['smtp_host']
        smtp_port = external.email['smtp_port']
        from_email = config.EMAIL_FROM
        from_password = config.EMAIL_APP_PASSWORD

        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-Id'] = make_msgid()
        
        # Добавляем текст сообщения
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Подключаемся к SMTP серверу (автовыбор SSL/STARTTLS по порту)
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.ehlo()
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        
        # Если указан пароль, авторизуемся
        if from_password:
            # Важно: адрес отправителя должен соответствовать аккаунту аутентификации
            server.login(from_email, from_password)
        
        # Отправляем сообщение
        text = msg.as_string()
        rejected = server.sendmail(from_email, [to_email], text)
        server.quit()
        
        if rejected:
            # sendmail возвращает словарь непринятых адресов
            gb.rc.print(f"❌ Почтовый сервер отклонил адреса: {rejected}", style="red")
            return False
        
        gb.rc.print(f"📧 Email успешно отправлен на {to_email}", style="green")
        return True
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при отправке email: {e}", style="red")
        return False


def send_download_completion_notification(to_email: str, files_count: int):
    """
    Отправляет уведомление о завершении скачивания файлов
    
    Args:
        to_email: Email получателя
        files_count: Количество скачанных файлов
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = "CheckPoint: Скачивание файлов завершено"
    
    message = f"""
Уведомление от CheckPoint

Скачивание файлов Facebook завершено!

Детали:
- Количество файлов: {files_count}
- Время завершения: {current_time}
- Статус: Успешно завершено

Все файлы были успешно отправлены на скачивание.
Проверьте папку загрузок для получения файлов.

---
Это автоматическое уведомление от CheckPoint
"""
    
    return send_notification_email(to_email, subject, message)


def send_module_start_notification(to_email: str, module_name: str):
    """
    Отправляет уведомление о начале выполнения модуля
    
    Args:
        to_email: Email получателя
        module_name: Название модуля
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = f"CheckPoint: Запуск модуля {module_name}"
    
    message = f"""
Уведомление от CheckPoint

Начато выполнение модуля: {module_name}

Детали:
- Модуль: {module_name}
- Время запуска: {current_time}
- Статус: Модуль запущен и выполняется

Модуль начал свою работу и будет выполнять назначенные задачи.

---
Это автоматическое уведомление от CheckPoint
"""
    
    return send_notification_email(to_email, subject, message)


def send_stats_notification(to_email: str, new_files: int, duplicates: int, photo_path: str, stats_logs_path: str):
    """
    Отправляет уведомление о статистике файлов
    
    Args:
        to_email: Email получателя
        new_files: Количество новых файлов
        duplicates: Количество дублей
        photo_path: Путь к папке PHOTO
        stats_logs_path: Путь к папке логов статистики
    """
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    today_date = datetime.now().strftime("%d.%m.%Y")
    
    subject = f"CheckPoint: Статистика файлов за {today_date}"
    
    message = f"""
Ежедневная статистика файлов CheckPoint

Дата: {today_date}
Время отчета: {current_time}
Папка мониторинга: {photo_path}

📊 СТАТИСТИКА:
🆕 Новых файлов: {new_files}
♻️ Дублированных файлов: {duplicates}
📁 Всего обработано: {new_files + duplicates}

Подробная статистика сохранена в лог-файле:
{stats_logs_path}/{today_date}.log

---
Это автоматический отчет от CheckPoint
"""
    
    return send_notification_email(to_email, subject, message)
