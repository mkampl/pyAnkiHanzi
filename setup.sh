#!/usr/bin/env python3
"""
Setup-Script für pyAnkiHanzi
"""

from setuptools import setup, find_packages
import os

# Lese README für long_description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Lese requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pyankihanzi",
    version="2.0.0",
    author="Ihr Name",
    author_email="ihre.email@example.com",
    description="Erstellt Anki-Karten für chinesische Zeichen mit interaktiven Strichfolgen",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/IhrUsername/pyAnkiHanzi",
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
        "Bug Reports": "https://github.com/IhrUsername/pyAnkiHanzi/issues",
        "Source": "https://github.com/IhrUsername/pyAnkiHanzi",
        "Documentation": "https://github.com/IhrUsername/pyAnkiHanzi/blob/main/README.md",
    },
)
