import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import requests

from checkpoint import config
from checkpoint import globals as gb


def send_notification_email(to_email: str, subject: str, message: str, 
                          smtp_server: str = "smtp.mail.ru",
                          smtp_port: int = 465):
    """
    Отправляет уведомление на email
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        message: Текст сообщения
        smtp_server: SMTP сервер (по умолчанию mail.ru)
        smtp_port: Порт SMTP сервера
    """
    try:
        api_key = config.MAILGUN_API_KEY

        resp = requests.post(
            config.MAILGUN_API_URL,
            auth=("api", api_key),
            data={"from": config.FROM_EMAIL_ADDRESS, "to": to_email, "subject": subject, "text": message}
        )
        if resp.status_code == 200:
            gb.rc.print(f"Successfully sent an email to '{to_email}' via Mailgun API.")
        else:  # error
            gb.rc.print(f"Could not send the email, reason: {resp.text}")

    except Exception as ex:
        gb.rc.print(f"Mailgun error: {ex}")


    try:
            
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Добавляем текст сообщения
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Подключаемся к SMTP серверу
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Включаем шифрование
        
        # Если указан пароль, авторизуемся
        if from_password:
            server.login(from_email, from_password)
        
        # Отправляем сообщение
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
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
