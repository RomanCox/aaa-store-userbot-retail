import os
import hashlib

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def has_file_changed(new_file: str, old_file: str) -> bool:
    if not os.path.exists(old_file):
        return True
    return get_file_hash(new_file) != get_file_hash(old_file)