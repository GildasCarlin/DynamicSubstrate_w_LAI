Required python packages:
-------------------------------------------------------

-- numpy

-- pandas 


-- fluigent Software Development Kit (SDK) https://github.com/Fluigent/fgt-SDK


-- setuptools
 (not required in python 3.8)
   Note: recent versions, pkg_resources must be replaced by setuptools. It is adviced to use the low_level.py version without pkg_resources.




to create a virtual environment (.venv) from Visual Studio Code:
-------------------------------------------------------

https://code.visualstudio.com/docs/python/environments




to activate the .venv:
-------------------------------------------------------

open the folder in the VS code terminal and type .\venv\Scripts\activate

IF error: Impossible de charger le fichier ~\.venv\Scripts\Activate.ps1, car l'exécution de scripts est désactivée sur ce système.

THEN type Set-ExecutionPolicy Unrestricted -Scope Process

THEN redo .\venv\Scripts\activate

sources:

https://stackoverflow.com/questions/54106071/how-can-i-set-up-a-virtual-environment-for-python-in-visual-studio-
code

https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows/18713789#18713789
