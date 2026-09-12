import os
import re
import hashlib
from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
_TIMESTAMP_RE = re.compile(r"_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})(?=\.[^.]*$)")

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def has_file_changed(new_file: str, old_file: str) -> bool:
    if not old_file or not os.path.exists(old_file):
        return True
    return get_file_hash(new_file) != get_file_hash(old_file)

def add_timestamp_to_filename(file_name: str, when: datetime = None) -> str:
    """
    Добавляет к имени файла (перед расширением) метку даты и времени, например:
    'Все товары.xlsx' -> 'Все товары_2026-09-11_00-03-31.xlsx'
    """
    when = when or datetime.now()
    name, ext = os.path.splitext(file_name)
    return f"{name}_{when.strftime(TIMESTAMP_FORMAT)}{ext}"

def extract_timestamp_from_filename(file_name: str):
    """Извлекает дату/время из имени файла, если она туда была добавлена. Иначе None."""
    match = _TIMESTAMP_RE.search(file_name)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), TIMESTAMP_FORMAT)
    except ValueError:
        return None

def find_latest_versioned_file(directory: str, prefix: str, skip_prefix: str = "new_"):
    """
    Находит в directory самую свежую (по метке даты/времени в имени) версию файла,
    имя которого начинается на prefix (и пропускает временные файлы skip_prefix).
    """
    if not os.path.isdir(directory):
        return None
    latest_path = None
    latest_ts = None
    for file_name in os.listdir(directory):
        if skip_prefix and file_name.startswith(skip_prefix):
            continue
        if not file_name.startswith(prefix):
            continue
        ts = extract_timestamp_from_filename(file_name)
        if ts is None:
            continue
        if latest_ts is None or ts > latest_ts:
            latest_ts = ts
            latest_path = os.path.join(directory, file_name)
    return latest_path

def cleanup_old_versioned_files(directory: str, prefix: str, max_age_days: float, skip_prefix: str = "new_"):
    """
    Удаляет в directory версии файла (имя начинается на prefix и содержит метку
    даты/времени), которым уже больше max_age_days суток.
    """
    removed = []
    if not os.path.isdir(directory):
        return removed
    now = datetime.now()
    for file_name in os.listdir(directory):
        if skip_prefix and file_name.startswith(skip_prefix):
            continue
        if not file_name.startswith(prefix):
            continue
        ts = extract_timestamp_from_filename(file_name)
        if ts is None:
            continue
        age_days = (now - ts).total_seconds() / 86400
        if age_days > max_age_days:
            full_path = os.path.join(directory, file_name)
            try:
                os.remove(full_path)
                removed.append(full_path)
                print(f"🗑️ Удалена устаревшая (>{max_age_days} сут.) версия прайса: {full_path}")
            except OSError as e:
                print(f"⚠️ Не удалось удалить устаревшую версию прайса {full_path}: {e}")
    return removed
