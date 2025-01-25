# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import markdown

def make_html(str_src):
    config = {
        "output_format": "html5",
        "extensions": [
            "markdown.extensions.extra",
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite"
        ],
        "extension_configs": {
            "markdown.extensions.codehilite": {
                "guess_lang": False
            }
        }
    }
    return markdown.markdown(str_src,**config)
