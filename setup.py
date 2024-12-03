from setuptools import setup, find_packages

# Lendo as dependências do requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Lendo o README.md para a descrição longa (se existir)
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="pagseguro",
    version="0.1.0",
    author="Miguel Ilha",
    author_email="miguel@isla.software",
    description="Framework for integration with payment gateways, with initial support for PagSeguro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"pagseguro": "payments"},
    packages=["pagseguro"],
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    project_urls={
        "Source Code": "https://github.com/Migguell/PagBank.git"
    }
)
