# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import subprocess
import shlex
from pathlib import Path

def proc(cmd, cwd=None):
    if isinstance(cmd,str):
        cmd = shlex.split(cmd)
    r = subprocess.run(cmd,capture_output=True,cwd=cwd)
    return (
        r.returncode,
        r.stdout.decode('utf-8'),
        r.stderr.decode('utf-8')
    )

# We can improve this in future
def rsync(src_dir, dst_dir, delete=False, exclude=[], follow_symlinks=False):
    src = f"{Path(src_dir)}/."
    dst = f"{Path(dst_dir)}/."
    assert src.endswith("/.") and not src.endswith("//.")
    assert dst.endswith("/.") and not dst.endswith("//.")

    delete_opt = "--delete" if delete else ""
    symlink_opt = "--copy-links" if follow_symlinks else ""
    exclude_opt = ""
    if len(exclude)>0:
        for e in exclude:
            exclude_opt += f"--exclude '{e}' "
    cmd = f"rsync -av {delete_opt} {exclude_opt} {symlink_opt} {src} {dst}"
    c,o,e = proc(cmd)
    return c,o,e
