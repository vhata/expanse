from setuptools import setup, find_packages

setup(
    name="expanse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "pynput",
    ],
    entry_points={
        "console_scripts": [
            "expanse=expanse.cli:main",
            "expanse-gui=expanse.daemon:main",
        ],
    },
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A text snippet manager with global keyboard shortcuts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/expanse",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
