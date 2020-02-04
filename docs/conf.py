project = 'Harness'
copyright = '2020, Vladimir Magamedov'
author = 'Vladimir Magamedov'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

autoclass_content = 'both'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.7', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable', None),
}

exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'display_version': False,
}

def setup(app):
    app.add_stylesheet('style.css?r=1')
    app.add_stylesheet('fixes.css?r=1')
