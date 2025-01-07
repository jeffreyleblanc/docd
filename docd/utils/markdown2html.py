# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import markdown


def make_html(str_src):
    return markdown.markdown(str_src, extensions=[
        "markdown.extensions.extra",
        "markdown.extensions.codehilite"
    ])
