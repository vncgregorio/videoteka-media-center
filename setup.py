from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="videoteka-media-center",
    version="0.1.0",
    author="Videoteka Team",
    description="A desktop media center application for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/videoteka/media-center",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.6.0",
        "Pillow>=10.0.0",
        "mutagen>=1.47.0",
        "PyMuPDF>=1.23.0",
        "opencv-python-headless>=4.8.0",
    ],
    entry_points={
        "console_scripts": [
            "videoteka=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["resources/**/*"],
    },
)


