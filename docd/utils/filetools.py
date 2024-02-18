# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

from pathlib import Path
import shutil
import hashlib

def clear_directory(dir_path):
    # Note not 'safety' tested
    dir_path = Path(dir_path)
    for child in dir_path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        elif child.is_file():
            child.unlink()

def file_md5(filepath):
    hasher = hashlib.md5()
    with Path(filepath).open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def file_sha256(filepath):
    hasher = hashlib.sha256()
    with Path(filepath).open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
