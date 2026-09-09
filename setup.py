from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="farmsetu",
    version="1.0.0",
    author="Anand Wankhade",
    description="AI-powered agriculture and farmer market assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anandwankhade-afk/farmsetu",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.36.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
)
