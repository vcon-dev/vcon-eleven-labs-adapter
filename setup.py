from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vcon-elevenlabs-adapter",
    version="1.0.0",
    author="Thomas Howe",
    description="Convert ElevenLabs agent interactions to vCon format and export to multiple backends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vcon-eleven-labs-adapter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "vcon>=1.0.3,<2",
        "elevenlabs>=0.3.0",
        "boto3>=1.28.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vcon-elevenlabs=src.cli:main",
        ],
    },
)
