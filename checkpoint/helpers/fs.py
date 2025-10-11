"""
File system utilities and duplicate handling
"""
import os
import re
import shutil
import hashlib
from pathlib import Path
from typing import Set, List, Tuple, Optional
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


# =============================================================================
# DUPLICATE FILE HANDLING METHODS
# =============================================================================

def calculate_file_hash(file_path: Path, algorithm: str = 'md5') -> str:
    """
    Вычисляет хеш файла для определения дубликатов
    
    Args:
        file_path: Путь к файлу
        algorithm: Алгоритм хеширования ('md5', 'sha1', 'sha256')
        
    Returns:
        str: Хеш файла в виде строки
        
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если алгоритм не поддерживается
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    # Размер буфера для чтения файла (64KB)
    BUF_SIZE = 65536
    
    # Выбираем алгоритм хеширования
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }
    
    if algorithm not in hash_algorithms:
        raise ValueError(f"Неподдерживаемый алгоритм: {algorithm}. Доступны: {list(hash_algorithms.keys())}")
    
    hash_obj = hash_algorithms[algorithm]()
    
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                hash_obj.update(data)
        
        return hash_obj.hexdigest()
    
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при вычислении хеша файла {file_path}: {e}", style="red")
        raise


def is_duplicate_by_filename(filename: str) -> bool:
    """
    Проверяет, является ли файл дублем по имени (имеет суффикс _2, _3 и т.д.)
    
    Args:
        filename: Имя файла для проверки
        
    Returns:
        bool: True если файл является дублем
    """
    # Паттерн для поиска суффикса дубля: _число перед расширением
    pattern = r'_\d+\.[^.]+$'
    return bool(re.search(pattern, filename))


def find_duplicates_by_hash(
    directory: Path, 
    extensions: Optional[List[str]] = None,
    algorithm: str = 'md5',
    recursive: bool = True
) -> Tuple[List[Tuple[str, List[Path]]], int]:
    """
    Находит дубликаты файлов в директории по хешу
    
    Args:
        directory: Путь к директории для поиска
        extensions: Список расширений файлов для проверки (например, ['.jpg', '.png'])
        algorithm: Алгоритм хеширования
        recursive: Рекурсивный поиск по поддиректориям
        
    Returns:
        Tuple[List[Tuple[str, List[Path]]], int]: 
            (список групп дубликатов (хеш, список путей), общее количество дубликатов)
    """
    if not directory.exists():
        gb.rc.print(f"⚠️ Директория не найдена: {directory}", style="yellow")
        return [], 0
    
    file_hashes = {}
    total_duplicates = 0
    
    try:
        # Определяем метод обхода директории
        if recursive:
            file_paths = directory.rglob('*')
        else:
            file_paths = directory.glob('*')
        
        # Фильтруем только файлы
        for file_path in file_paths:
            if not file_path.is_file():
                continue
                
            # Проверяем расширение файла, если задан фильтр
            if extensions and file_path.suffix.lower() not in [ext.lower() for ext in extensions]:
                continue
            
            try:
                file_hash = calculate_file_hash(file_path, algorithm)
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(file_path)
                else:
                    file_hashes[file_hash] = [file_path]
                    
            except Exception as e:
                gb.rc.print(f"⚠️ Ошибка при обработке файла {file_path}: {e}", style="yellow")
                continue
        
        # Выбираем только группы с дубликатами (больше одного файла)
        duplicate_groups = [(hash_val, paths) for hash_val, paths in file_hashes.items() if len(paths) > 1]
        
        # Подсчитываем общее количество дубликатов (исключая оригиналы)
        for _, paths in duplicate_groups:
            total_duplicates += len(paths) - 1  # -1 потому что один файл - оригинал
        
        gb.rc.print(f"🔍 Найдено {len(duplicate_groups)} групп дубликатов, всего дубликатов: {total_duplicates}", style="blue")
        
        return duplicate_groups, total_duplicates
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при поиске дубликатов в {directory}: {e}", style="red")
        return [], 0


def find_duplicates_by_filename(
    directory: Path,
    recursive: bool = True
) -> Tuple[List[Path], int]:
    """
    Находит дубликаты файлов в директории по имени (с суффиксами _2, _3 и т.д.)
    
    Args:
        directory: Путь к директории для поиска
        recursive: Рекурсивный поиск по поддиректориям
        
    Returns:
        Tuple[List[Path], int]: (список путей к дубликатам, количество дубликатов)
    """
    if not directory.exists():
        gb.rc.print(f"⚠️ Директория не найдена: {directory}", style="yellow")
        return [], 0
    
    duplicate_files = []
    
    try:
        # Определяем метод обхода директории
        if recursive:
            file_paths = directory.rglob('*')
        else:
            file_paths = directory.glob('*')
        
        # Фильтруем только файлы и проверяем на дубликаты
        for file_path in file_paths:
            if file_path.is_file() and is_duplicate_by_filename(file_path.name):
                duplicate_files.append(file_path)
        
        gb.rc.print(f"🔍 Найдено {len(duplicate_files)} дубликатов по имени файла", style="blue")
        
        return duplicate_files, len(duplicate_files)
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при поиске дубликатов по имени в {directory}: {e}", style="red")
        return [], 0


def get_unique_filename(target_path: Path) -> Path:
    """
    Генерирует уникальное имя файла, добавляя число к имени при конфликте
    Если исходный файл уже является дублем (имеет номер в конце),
    счетчик начинается с этого номера + 1
    
    Args:
        target_path: Путь к целевому файлу
        
    Returns:
        Path: Уникальный путь к файлу
    """
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    
    # Проверяем, является ли исходный файл уже дублем (имеет суффикс _число)
    duplicate_pattern = r'_(\d+)$'
    match = re.search(duplicate_pattern, stem)
    
    if match:
        # Исходный файл уже дубль, извлекаем базовое имя и номер
        existing_number = int(match.group(1))
        base_stem = stem[:match.start()]  # Имя без суффикса _число
        counter = existing_number + 1
    else:
        # Исходный файл не дубль, используем полное имя как базу
        base_stem = stem
        counter = 1
    
    while True:
        new_name = f"{base_stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def merge_directories(src_dir: Path, dst_dir: Path, conflict_resolution: str = 'rename') -> bool:
    """
    Объединяет содержимое двух директорий, разрешая конфликты имен
    
    Args:
        src_dir: Исходная директория
        dst_dir: Целевая директория
        conflict_resolution: Способ разрешения конфликтов:
            - 'rename': переименовывает конфликтующие файлы
            - 'skip': пропускает конфликтующие файлы
            - 'overwrite': перезаписывает существующие файлы
            
    Returns:
        bool: True если операция прошла успешно
    """
    if not src_dir.exists():
        gb.rc.print(f"⚠️ Исходная директория не найдена: {src_dir}", style="yellow")
        return False
    
    if not src_dir.is_dir():
        gb.rc.print(f"⚠️ Путь не является директорией: {src_dir}", style="yellow")
        return False
    
    # Создаем целевую директорию если не существует
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        for item in src_dir.iterdir():
            target_item = dst_dir / item.name
            
            if item.is_file():
                if target_item.exists():
                    if conflict_resolution == 'rename':
                        # Создаем уникальное имя
                        unique_target = get_unique_filename(target_item)
                        shutil.move(str(item), str(unique_target))
                        gb.rc.print(f"📄 Файл переименован: {item.name} → {unique_target.name}", style="yellow")
                    elif conflict_resolution == 'skip':
                        gb.rc.print(f"⏭️ Файл пропущен (уже существует): {item.name}", style="cyan")
                        continue
                    elif conflict_resolution == 'overwrite':
                        shutil.move(str(item), str(target_item))
                        gb.rc.print(f"🔄 Файл перезаписан: {item.name}", style="orange")
                else:
                    shutil.move(str(item), str(target_item))
                    
            elif item.is_dir():
                if target_item.exists():
                    # Директория существует, объединяем содержимое рекурсивно
                    gb.rc.print(f"📁 Объединение папок: {item.name}", style="cyan")
                    merge_directories(item, target_item, conflict_resolution)
                    # Удаляем исходную директорию после слияния
                    if item.exists():
                        shutil.rmtree(str(item))
                else:
                    shutil.move(str(item), str(target_item))
        
        return True
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при объединении директорий: {e}", style="red")
        return False


def remove_duplicates(
    directory: Path,
    method: str = 'hash',
    extensions: Optional[List[str]] = None,
    dry_run: bool = True,
    keep_newest: bool = True
) -> Tuple[int, List[Path]]:
    """
    Удаляет дубликаты файлов в директории
    
    Args:
        directory: Путь к директории
        method: Метод поиска дубликатов ('hash' или 'filename')
        extensions: Список расширений файлов для проверки
        dry_run: Если True, только показывает что будет удалено без реального удаления
        keep_newest: Если True, сохраняет самый новый файл из группы дубликатов
        
    Returns:
        Tuple[int, List[Path]]: (количество удаленных файлов, список удаленных путей)
    """
    if not directory.exists():
        gb.rc.print(f"⚠️ Директория не найдена: {directory}", style="yellow")
        return 0, []
    
    removed_count = 0
    removed_files = []
    
    try:
        if method == 'hash':
            duplicate_groups, _ = find_duplicates_by_hash(directory, extensions)
            
            for hash_val, file_paths in duplicate_groups:
                # Сортируем файлы по времени модификации
                sorted_files = sorted(file_paths, key=lambda x: x.stat().st_mtime, reverse=keep_newest)
                
                # Удаляем все файлы кроме первого (самого нового или старого)
                files_to_remove = sorted_files[1:]
                
                for file_path in files_to_remove:
                    if dry_run:
                        gb.rc.print(f"🗑️ [DRY RUN] Будет удален: {file_path}", style="yellow")
                    else:
                        try:
                            file_path.unlink()
                            gb.rc.print(f"🗑️ Удален дубликат: {file_path}", style="green")
                            removed_count += 1
                            removed_files.append(file_path)
                        except Exception as e:
                            gb.rc.print(f"❌ Ошибка при удалении {file_path}: {e}", style="red")
        
        elif method == 'filename':
            duplicate_files, _ = find_duplicates_by_filename(directory)
            
            for file_path in duplicate_files:
                if dry_run:
                    gb.rc.print(f"🗑️ [DRY RUN] Будет удален: {file_path}", style="yellow")
                else:
                    try:
                        file_path.unlink()
                        gb.rc.print(f"🗑️ Удален дубликат: {file_path}", style="green")
                        removed_count += 1
                        removed_files.append(file_path)
                    except Exception as e:
                        gb.rc.print(f"❌ Ошибка при удалении {file_path}: {e}", style="red")
        
        else:
            raise ValueError(f"Неподдерживаемый метод: {method}. Доступны: 'hash', 'filename'")
        
        if dry_run:
            gb.rc.print(f"📊 [DRY RUN] Найдено {len(removed_files)} файлов для удаления", style="blue")
        else:
            gb.rc.print(f"✅ Удалено {removed_count} дубликатов", style="green")
        
        return removed_count, removed_files
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при удалении дубликатов: {e}", style="red")
        return 0, []


def get_duplicate_statistics(
    directory: Path,
    extensions: Optional[List[str]] = None,
    include_hash_duplicates: bool = True,
    include_filename_duplicates: bool = True
) -> dict:
    """
    Получает статистику по дубликатам в директории
    
    Args:
        directory: Путь к директории
        extensions: Список расширений файлов для проверки
        include_hash_duplicates: Включать ли поиск дубликатов по хешу
        include_filename_duplicates: Включать ли поиск дубликатов по имени
        
    Returns:
        dict: Словарь со статистикой дубликатов
    """
    stats = {
        'directory': str(directory),
        'hash_duplicates': {'groups': 0, 'files': 0, 'details': []},
        'filename_duplicates': {'files': 0, 'details': []},
        'total_duplicates': 0
    }
    
    if not directory.exists():
        gb.rc.print(f"⚠️ Директория не найдена: {directory}", style="yellow")
        return stats
    
    try:
        if include_hash_duplicates:
            duplicate_groups, hash_duplicates_count = find_duplicates_by_hash(directory, extensions)
            stats['hash_duplicates']['groups'] = len(duplicate_groups)
            stats['hash_duplicates']['files'] = hash_duplicates_count
            stats['hash_duplicates']['details'] = [(hash_val, [str(p) for p in paths]) for hash_val, paths in duplicate_groups]
        
        if include_filename_duplicates:
            filename_duplicates, filename_duplicates_count = find_duplicates_by_filename(directory)
            stats['filename_duplicates']['files'] = filename_duplicates_count
            stats['filename_duplicates']['details'] = [str(p) for p in filename_duplicates]
        
        stats['total_duplicates'] = stats['hash_duplicates']['files'] + stats['filename_duplicates']['files']
        
        gb.rc.print(f"📊 Статистика дубликатов для {directory}:", style="blue")
        gb.rc.print(f"   🔗 Дубликаты по хешу: {stats['hash_duplicates']['files']} файлов в {stats['hash_duplicates']['groups']} группах", style="cyan")
        gb.rc.print(f"   📝 Дубликаты по имени: {stats['filename_duplicates']['files']} файлов", style="cyan")
        gb.rc.print(f"   📁 Всего дубликатов: {stats['total_duplicates']}", style="green")
        
        return stats
        
    except Exception as e:
        gb.rc.print(f"❌ Ошибка при получении статистики дубликатов: {e}", style="red")
        return stats


def clean_folder_name(folder_name: str) -> str:
    """
    Очищает имя папки от случайного суффикса
    
    Args:
        folder_name: Исходное имя папки (например, "2016Novorossijsk_1GrOsmhKAQ")
        
    Returns:
        str: Очищенное имя папки (например, "2016Novorossijsk")
    """
    # Паттерн для поиска случайного суффикса: подчеркивание + случайные символы в конце
    pattern = r'_[A-Za-z0-9]+$'
    cleaned_name = re.sub(pattern, '', folder_name)
    return cleaned_name
