# Pramana Inline Algorithm Simulator

This document provides a guide on how to simulate the entire Inline Algorithm Pipeline that will run on the Pramana Scanner.


## Introduction
Pramana has a standardized API format for communicating between the Pramana scanning system and any image analysis algorithm module. For ease of deployment the algorithm module is recommended to be encapsulated and deployed as a Docker container. This API simulator includes the state changes of the scanning process from the start to the end and provides access to the image data inline during the scanning process.



## Folder Structure
    .
    ├── algorithm_api_service
    │   ├── algorithm_api_service.py
    │   ├── helpers.py
    │   └── models.py
    ├── data
    │   ├── M01JBC16P-1212.ome.tiff
    │   └── simulator_demo.dcm
    ├── mock_scanner_service
    │   ├── mock_scanner_service.py
    │   ├── models_scanner.py
    │   └── scanner_service_helpers.py
    ├── output/
    ├── pramana_inline_algorithm_simulator.py
    ├── algorithm_api_service_v1.tar
    ├── config.ini
    ├── requirements-for-simulator.txt
    └── README.md
## File Breakdown
 1. ```pramana_inline_algorithm_simulator.py```
  This is the  simulator script to make the needed API calls. This script reads the sample ```ome.tif``` or a ```.dcm``` file from the ```data/``` directory, breaks it down to ```.bmp``` files and saves it in a subdirectory inside the ```data/``` directory.   This file is supposed to mock the image acquisition process of the Pramana Scanner.

2. ```algorithm_api_service/algorithm_api_service.py```
This is a ```FastAPI``` backend server that runs on the ```PORT 8000```. This service receives all the API calls made by the ```pramana_inline_algorithm_simulator.py``` script. This service is supposed to be the Inline Algorithm Service. It uses the ```helpers.py``` and ```models.py``` files to run. 

3. ```mock_scanner_service/mock_scanner_service.py```
This is a ```FastAPI``` backend server that runs on the ```PORT 8001```. This service  is supposed to mock the Pramana Scanner and recieve the API calls made by the ```algorithm_api_service service```. It uses the ```models_scanner.py```  and     ```scanner_service_helpers.py``` files to run.

4. ```config.ini```
 This config file is where all the constant parameters are defined. 
- ```INPUT_FILE_NAME``` : This is the name for the input file (either ```ome.tif``` or ```dcm``` file).
- ```BASE_PATH``` : This is the absolute base path of the repository  (**you will need to replace this with the base path respective to your machine**).

- ```ALGORITHM_ID``` : This is the algorithm id.
- ```SLIDE_NAME``` : This is the slide name.
- ```STAIN_NAME``` : This is the stain name.
- ```ORGAN_NAME``` : This is the organ name.

 

## Prerequisite 
-  Needs Python3.11 or higher. Tested on Python 3.11.2

## Steps to install dependencies  
- Create a virtual environment using the command  : ```python3 -m venv venv```
- Activate the virtual environment using the command: ```source venv/bin/activate```
- Install the dependencies using the command: ```pip install -r requirements-for-simulator.txt```


## Run the Mock Scanner Service
Enter the command: ```python mock_scanner_service/mock_scanner_service.py```

## Run the Algorithm API Service
- If you want to run on localhost, enter the command: ```python algorithm_api_service/algorithm_api_service.py``` on another termninal.
- If you want to run it as a docker container. Make sure that you change the ```volumes``` in the ```docker-compose.yml``` file to the absolute path of your local machine upto the ```data``` directory like this: ```'<absolute path upto the data directory>:/data/acquired_data'```
    - Load the docker image: ```docker load < algorithm_api_service_v1.tar```
    - Turn on the container using the docker compose command: ```docker compose up```

## Run the simulator script to make the API calls
- One can either run the script in interactive mode which asks for the user to trigger the pipeline step by step or in non-interactive mode which will run the entire script end to end without any user interaction required. Note: With the interactive mode you can skip the function which extracts the tiles from the ome.tif you have already ran the script before to save time.
- To run the python script in interactive mode and if the algorithm api service is running on localhost:  ```python pramana_inline_algorithm_simulator.py -i```. If the algorithm api service is running inside a docker container run: ```python pramana_inline_algorithm_simulator.py -i -d```

- To run the python script in non-interactive mode if the algorithm api service is running on localhost: ```python pramana_inline_algorithm_simulator.py```. If the algorithm api service is running inside a docker container run: ```python pramana_inline_algorithm_simulator.py -d```

