# Overview
This project has been implemented based on a research that was carried out by INRS, Quebec City, Quebec, Canada. The main objective of this project is 
predicting the flood zones using remote sensing analysis and artificial intelligence.

**under development**

# Instruction
This project is based on `python 3.7.4` and applies different python libraries. So that you need to install all the requirements on your machine.

# Libraries
- gdal : [official website](https://gdal.org/)
- numppy.py : [official website](https://numpy.org/)
- scipy : [official website](https://scipy.org/)
- rasterio : [official website](https://rasterio.readthedocs.io/en/latest/)
- fcmeans : [github project](https://github.com/omadson/fuzzy-c-means)

# Install project
First of all you need to install all mentioned dependencies.
Rasterio is a  powerful library that provide us with handy functions to manipulate satellite images. This library needs GDAL as mentioned in it's [github project](https://github.com/mapbox/rasterio).
Because installing GDAL could be sometimes a tough work, I've answered to a similar question on [gis.stackchange](https://gis.stackexchange.com/questions/343835/installing-rasterio-and-gdal-api-in-a-virtuallenv-in-windows-10/371720#371720).

**under development**

# Launch project
## Create an environment
By developing different python virtual environments, you will be able to have different versions of python on your machine. Taking advantages of differrnt python make you to have several compatible dependencies on each environment. To achive this, after installing python follow these steps.

1. DONT add python to PATH environment variable
2. Open terminal and run following code to create an environment for version of python in which you are insterested.
```
> ~\python.exe -m pip install virtualenv
> virtalenv <path-to-env>\<env_name> -p <path-to-python.exe>
```
## Run project
**IMPORTANT**

Each time, you need to `activate` local environment of python before starting project or installing any dependency.

Open terminal, `cd` to project and then activate the environment.
```
> <path-to-env>\<env_name>\Scripts\activate
```
When local environment is active, use `pip` package manager to installed neccessary dependencies on project.
```
pip install <package_name>
```
**under development**
