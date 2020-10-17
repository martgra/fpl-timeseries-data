"""The package install file."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fpl--martin-gran",  # Replace with your own username
    version="0.1.1",
    author="Martin Gran",
    author_email="martgra@gmail.com",
    description="A Fantasy premier league package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "azure-storage-blob",
        "azure-cosmos",
        "python-dotenv",
        "notebook",
        "jupytext",
        "pandas",
        "numpy",
        "requests",
        "tqdm",
        "seaborn",
        "click",
    ],
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        fantasy=fpl.__main__:main
        """,
)
