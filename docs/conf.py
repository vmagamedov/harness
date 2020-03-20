project = "Harness"
copyright = "2020, Vladimir Magamedov"
author = "Vladimir Magamedov"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_ext_protobuf",
    "sphinx_ext_test",
    "sphinx_ext_wire",
    "sphinx_ext_changelog",
]

autoclass_content = "both"
autodoc_mock_imports = [
    "aiohttp",
    "aiomonitor",
    "apscheduler",
    "asyncpg",
    "grpclib",
    "opentelemetry",
    "prometheus_client",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable", None),
}

exclude_patterns = ["_build"]
templates_path = ["_templates"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_additional_pages = {
    "bootstrap": "bootstrap.html",
}
html_theme_options = {
    "display_version": False,
}
html_context = {
    "display_github": True,
    "github_user": "vmagamedov",
    "github_repo": "harness",
    "github_version": "master",
    "conf_py_path": "/docs/",
}


def setup(app):
    app.add_stylesheet("style.css")
