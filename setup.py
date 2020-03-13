import os.path

from setuptools import setup, find_packages

with open(
    os.path.join(os.path.dirname(__file__), 'README.rst')
) as f:
    DESCRIPTION = f.read()

setup(
    name='harness',
    version='0.1.0rc3',
    description='Language-neutral microservices boilerplate as a code',
    long_description=DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='Vladimir Magamedov',
    author_email='vladimir@magamedov.com',
    url='https://github.com/vmagamedov/harness',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD-3-Clause',
    python_requires='>=3.7',
    install_requires=[
        'protobuf',
        'json-merge-patch',
        'jsonpatch',
        'opentelemetry-sdk==0.4a1',
    ],
    entry_points={
        'console_scripts': [
            'protoc-gen-harness=harness.plugin.main:main',
            'harness=harness.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
