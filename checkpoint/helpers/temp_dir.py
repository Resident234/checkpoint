"""
Temporary directory management utilities
"""
from pathlib import Path
from checkpoint import globals as gb


def ensure_temp_directory() -> Path:
    """
    Создает временную директорию в корневой папке проекта, если она не существует
    
    Returns:
        Path: Путь к временной директории
    """
    # Определяем корневую папку проекта (где находится pyproject.toml)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # checkpoint/helpers/temp_dir.py -> CheckPoint/
    
    # Создаем временную директорию
    temp_dir = project_root / "temp"
    
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)
        gb.rc.print(f"📁 Создана временная директория: {temp_dir}", style="blue")
    
    return temp_dir


def get_temp_path(filename: str) -> Path:
    """
    Возвращает путь к файлу во временной директории проекта
    
    Args:
        filename: Имя файла
        
    Returns:
        Path: Полный путь к файлу во временной директории
    """
    temp_dir = ensure_temp_directory()
    return temp_dir / filename
