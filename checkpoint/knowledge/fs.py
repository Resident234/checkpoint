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
    # Файлы для удаления в корне H:/ (например: H:/start_here.html)
    'file_patterns': [
        'start_here.html',
        'start_here_*.html',  # Паттерн для start_here_1.html, start_here_2.html и т.д.
    ],
    # Папки для удаления в корне H:/ (например: H:/files, H:/ads_information)
    'folder_patterns': [
        'ads_information',  # Папка с рекламной информацией
        'apps_and_websites_off_of_facebook',
        'security_and_login_information',
        'files',
        'logged_information',
        'preferences',
    ],
    # Папки для удаления по точному пути от корня H:/ (например: H:/connections/followers)
    'folder_path_patterns': [
        'connections/followers',
        'connections/supervision',
    ],
    # Правила для удаления подпапок с исключениями
    # Удаляет все подпапки в H:/personal_information/, кроме H:/personal_information/profile_information/
    'subfolder_cleanup_rules': [
        {
            'parent_folder': 'personal_information',
            'exclude_subfolders': ['profile_information'],  # Эти подпапки НЕ удалять
        }
    ],
    # Правила для удаления старых файлов по расширению и возрасту
    'old_file_cleanup': {
        'extensions': ['.crdownload'],  # Расширения файлов для удаления
        'max_age_days': 3,  # Удалять файлы старше N дней
    },
}