"""
Setup script for YouTube Enhancement Tools package

This script sets up the YouTube Enhancement Tools package for installation.
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read the requirements from requirements-enhanced.txt
with open('requirements-enhanced.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="youtube-enhancement-tools",
    version="1.0.0",
    author="YouTube Enhancement Tools Team",
    author_email="info@youtube-enhancement-tools.com",
    description="A comprehensive toolkit for YouTube content creators with automation, AI tools, and productivity enhancements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youtube-enhancement-tools/youtube-enhancement-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Content Creators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'youtube-enhancement-tools=youtube_enhancement_tools.main:main',
        ],
    },
    keywords=[
        'youtube', 'video', 'download', 'editor', 'automation', 
        'ai', 'content creator', 'productivity'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/youtube-enhancement-tools/youtube-enhancement-tools/issues',
        'Source': 'https://github.com/youtube-enhancement-tools/youtube-enhancement-tools',
        'Documentation': 'https://youtube-enhancement-tools.readthedocs.io/',
    },
)