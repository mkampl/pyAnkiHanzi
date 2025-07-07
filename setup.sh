#!/usr/bin/env python3
"""
Setup script for pyAnkiHanzi
"""

from setuptools import setup, find_packages
import os

# Read README for long_description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pyankihanzi",
    version="2.0.0",
    author="Markus Kampl",
    author_email="markus.kampl@gmail.com",
    description="Creates Anki cards for Chinese characters with interactive stroke order",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mkampl/pyAnkiHanzi",
    py_modules=["pyAnkiHanzi", "config"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ]
    },
    entry_points={
        "console_scripts": [
            "pyankihanzi=pyAnkiHanzi:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.cfg"],
    },
    keywords="anki chinese hanzi flashcards education language-learning",
    project_urls={
        "Bug Reports": "https://github.com/mkampl/pyAnkiHanzi/issues",
        "Source": "https://github.com/mkampl/pyAnkiHanzi",
        "Documentation": "https://github.com/mkampl/pyAnkiHanzi/blob/main/README.md",
    },
)
