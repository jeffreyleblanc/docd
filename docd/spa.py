# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

from pathlib import Path

# Load the spa page template
HERE = Path(__file__).parent
SPA_SRC_SPA_TEMPLATE_FILE = (HERE/"html-templates/spa.html").resolve()
assert(SPA_SRC_SPA_TEMPLATE_FILE.is_file())
SPA_TEMPLATE = SPA_SRC_SPA_TEMPLATE_FILE.read_text()

# The expected keys in the template
SPA_CONFIG_KEYS = (
    "__ROOT_URI__",
    "__TITLE__",
    "__AUTHOR__",
    "__NAME__",
    "__FOOTER__",
    "__HOME_URL__",
    "__CSS_FILE__",
    "__JS_FILE__"
)

# Our render method
def render_spa_html(config_dict, template_text=None):
    if template_text is None:
        template_text = SPA_TEMPLATE
    for k,v in config_dict.items():
        assert ( k in SPA_CONFIG_KEYS )
        template_text = template_text.replace(k,v)
    return template_text

