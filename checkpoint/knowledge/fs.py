"""
File system configuration and constants
"""

path = {
    'download_path': "H:/",
    'root_folder': "H:/PHOTO/",
    'to_delete_dir': "to_delete",
    'facebook_media_subpath': "your_facebook_activity/posts/media",
    'stats_logs_dir': "stats_logs",
}

files = {
    'verification_code_file': "verification_code.json",
    'allowed_pages_file': "allowed_pages.json",
}

# Конфигурация для CleanupManager
cleanup = {
    'file_patterns': [
        'start_here.html',
        'start_here_*.html',  # Паттерн для start_here_1.html, start_here_2.html и т.д.
    ],
    'folder_patterns': [],  # Можно добавить паттерны папок для удаления
}