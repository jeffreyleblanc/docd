# To use 'Markdown' library

While we use `mistune` in `docd`, if you want to switch to `markdown`,
the rough implementation looks like:

```python
from markdown import markdown
def make_html(text):
    config = {
        'output_format': 'html5',
        'extensions': ['fenced_code','codehilite'],
        'extension_configs': {
            'codehilite': { 'guess_lang': False, 'css_class': 'highlighted-syntax' }
        }}
    return markdown(text,**config)
```

