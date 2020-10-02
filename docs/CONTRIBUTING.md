# How to contribute to FPL2021 prosject?


## Table of Contents
1. [Where to contribute](#)
   1. [Understanding the data](#understanding-the-data)
   2. [Making data available](#making-data-available)
   3. [Integrating more data sources](#integrating-more-data-sources)
2. [Setting up development environment](#setting-up-development-environment)
    1. [Python environment](#python-environment)
    2. [VSCode](#visual-studio-code)
    3. [Connecting to data sources](#connecting-to-data-sources)
    4. [Jupyter Notebooks](#jupyter-notebooks)
3. [Workflow](#workflow)
4. [Never mind, I just want the data](#never-mind,-i-just-want-the-data)

## Where to contribute
### Understanding the data
* #### Describing the data
* #### Visualizing the data
* #### Predicting with the data
### Making data available
* #### API for grabbing data set and slices
* #### Frontend for searching in the data
* #### Publishing useful models/visualiztions
### Integrating more data sources
* #### Finding useful data sources
* #### Making scraping routines
* #### Integrating scraped data with existing dataset
## Setting up development environment
This project is developed with VSCode, Jupyter Notebooks and Azure. Below are instructions on how to replicate the development environment.
### Python environment
The project is based on **[Python 3.8](https://www.python.org/downloads/release/python-380/)**. It is strongly recommended that python inside a virtual environment. After installing python run the following to setup python interpeter, required packages and project files
```bash
# Linux/Debian
git clone https://github.com/martgra/fpl2021.git
cd fpl2021
python3 -m venv venv
source venv/bin/activate
# on Window: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Visual Studio Code
https://code.visualstudio.com/

#### **SSH remote development**
If developing on a Windows workstation an option to explore to develop in a [VS Code remote development](https://code.visualstudio.com/docs/remote/ssh)

#### **Extensions:**
* [Python-extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
* [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

#### **Workspace settings**
For better workflow the current settings have been used with VSCode to hightlight flake8, pylint and pydocstyles errors and warnings.<br>

Inside ```.vscode/settings.json```

```json
{
    "python.sortImports.args": [
        "-rc",
        "-sp isort.cfg"
    ],
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.pydocstyleEnabled": true,
    "files.trimTrailingWhitespace": true,
    "python.linting.pylintUseMinimalCheckers": false,
    "editor.formatOnSave": true,
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length",
        "100"
    ],
    "editor.rulers": [
        100
    ]
}
```
### Connecting to data sources
The repo utilze Azure Cloud for storage.
- [Azure Storage Blobs](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) holds raw scraped .json files downloaded every 6th hour from /api/bootstrap-static
- [Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction) hokds transformed data
Conributors can ask permission to get access to Cosmos DB and Azure Storage.

To get access add the following to a file named ```.env``` to the project root directory.
```bash
# .env
AZURE_STORAGE_CONNECTION_STRING="<connection string>"
AZURE_COSMOS_URI="<uri>"
AZURE_COSMOS_TOKEN="<key>"

```

### Jupyter Notebooks
Jupyter notebooks should be used for data exploration and visualization. However resuable functions should be written in python modules inside approporiate package inside ```fpl```.

Notebooks should be placed in the directory <b>notebooks</b> and is started by running the following commands:
```bash
source venv/bin/activate
jupyter notebook
```

#### **Notebook convention**
Further notebooks should have a clear purpose and which is reflected in:
* Notebook name
* A short markdown explaining the purpose of the notebook
* Some minimal documentation between sections ofthe notebook

#### **Version Control**
For version control the project utilize ```jupytext``` which splits the notebook source from output. Only the code in format of ```.rmd```  files is checked into version control.

To start juptyter notebooks

## Workflow
TODO: Fill inn


## Never mind, I just want the data
- Look in [README](https://github.com/martgra/fpl2021/blob/dev/README.md)
