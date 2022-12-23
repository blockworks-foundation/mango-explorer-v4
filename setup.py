from setuptools import setup, find_packages
from pathlib import Path


setup(
    name='mango_explorer_v4',
    version='0.1.4',
    description='Python client library for interacting with Mango Markets v4.',
    license='MIT',
    author="Mango Markets",
    author_email='support@mango.markets',
    packages=find_packages('mango_explorer_v4'),
    package_dir={'': 'mango_explorer_v4'},
    url='https://github.com/blockworks-foundation/mango-explorer-v4',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown'
)
