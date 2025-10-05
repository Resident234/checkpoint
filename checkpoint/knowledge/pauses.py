"""
Pause durations configuration and constants
All sleep() durations used throughout the application
"""

# General pauses (in seconds)
general = {
    'short_wait': 1,           # Короткая пауза для UI операций
    'medium_wait': 2,          # Средняя пауза для загрузки элементов
    'audio_load_wait': 10,     # Ожидание загрузки аудио
    'final_cleanup': 20,       # Финальная пауза перед закрытием
}

# Authentication and verification pauses
auth = {
    'verification_input': 3,   # Пауза после ввода кода верификации
    'thread_check': 0.2,       # Проверка состояния потоков
    'thread_wait': 10,         # Ожидание остановки потоков
}

# Download and backup pauses
download = {
    'button_click': 5,         # Пауза после клика по кнопке
    'download_start': 2,       # Ожидание начала скачивания
    'backup_processing': 36000,  # Ожидание обработки бэкапа (10 часов)
    'post_download': 93600,    # 26 часов после завершения скачиваний (93600 секунд)
}

# Archive monitoring pauses
archive = {
    'file_stability_check': 2,  # Проверка стабильности размера файла
    'monitor_cycle': 50,        # Пауза между циклами мониторинга ZIP файлов
    'error_recovery': 100,      # Увеличенная пауза при ошибке в мониторинге
}

# Media processing pauses
media = {
    'folder_scan': 300,          # Пауза между сканированием папок медиа
    'processing_cycle': 50,      # Пауза между обработкой отдельных папок
    'error_recovery': 100,       # Пауза при ошибке в обработке медиа
}

# Upload and connection pauses
upload = {
    'connection_check': 1,     # Проверка соединения
}

# Photo statistics monitoring pauses
stats = {
    'hourly_check': 3600,      # Проверка статистики каждый час (3600 секунд)
    'error_recovery': 300,     # Пауза при ошибке в сборе статистики (5 минут)
}

# Throttling function delays (used in sleep_throttling)
throttling = {
    'base_delay': 1,           # Базовая задержка в функции sleep_throttling
}

# WebDriverWait timeout values (in seconds)
webdriver_wait = {
    'short_wait': 1,           # Короткое ожидание элементов
    'quick_check': 3,          # Быстрая проверка наличия элементов
    'medium_wait': 30,         # Среднее ожидание загрузки
    'standard_wait': 100,      # Стандартное ожидание операций
    'form_wait': 300,          # Ожидание форм и диалогов
    'upload_wait': 500,        # Ожидание загрузки файлов
    'long_wait': 1000,         # Длительное ожидание (капча, верификация)
    'verification_wait': 36000, # Ожидание верификации (10 часов)
}
