from setuptools import setup, find_packages
from pathlib import Path

# Read long description
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

# Read version
version = {}
exec((Path(__file__).parent / "src" / "version.py").read_text(), version)

setup(
    name="security-breach-simulator",
    version=version.get("__version__", "1.0.0"),
    author="Security Team",
    author_email="security@example.com",
    description="Security Breach Simulator - Practice handling cyber attacks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taher53-s/security-breach-simulator",
    packages=find_packages(exclude=["tests", "docs", "backend"]),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "breach=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="security training simulator cyberattack breach incident-response",
    project_urls={
        "Bug Reports": "https://github.com/taher53-s/security-breach-simulator/issues",
        "Source": "https://github.com/taher53-s/security-breach-simulator",
    },
)
