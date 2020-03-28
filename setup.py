import re
import os.path

from setuptools import setup, find_packages

with open(
    os.path.join(os.path.dirname(__file__), "src", "harness", "__init__.py")
) as f:
    VERSION = re.match(r".*__version__ = \"(.*?)\"", f.read(), re.S).group(1)

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as f:
    DESCRIPTION = f.read()

setup(
    name="harness",
    version=VERSION,
    description="Language-neutral meta-framework for server-less style services",
    long_description=DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Vladimir Magamedov",
    author_email="vladimir@magamedov.com",
    url="https://github.com/vmagamedov/harness",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="BSD-3-Clause",
    python_requires=">=3.7",
    install_requires=[
        "protobuf",
        "pyyaml",
        "json-merge-patch",
        "jsonpatch",
        "opentelemetry-sdk==0.5b0",
    ],
    extras_require={"sdk": ["grpcio-tools"]},
    entry_points={
        "console_scripts": [
            "protoc-gen-harness=harness.plugin.main:main",
            "harness=harness.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
