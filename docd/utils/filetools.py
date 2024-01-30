# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

from pathlib import Path
import shutil

def clear_directory(dir_path):
    # Note not 'safety' tested
    dir_path = Path(dir_path)
    for child in dir_path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        elif child.is_file():
            child.unlink()
