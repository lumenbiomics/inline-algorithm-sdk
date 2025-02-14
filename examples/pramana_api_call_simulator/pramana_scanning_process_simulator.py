'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''
##### Import Libraries #####
import time
import json
import os
import math
import random
import configparser
import argparse
import requests
import tifffile
import pydicom
import numpy as np
from PIL import Image
from pydicom.pixel_data_handlers import convert_color_space
from tqdm import tqdm

####### Helper function to patch images from dicom pixel data #######
def get_patched_image(data, total_pixel_matrix_rows, total_pixel_matrix_cols):
    '''
    Will patch the smaller images together to form the complete pixel data image.
    
    :param data : dicom data.
    :param total_pixel_matrix_rows : the total rows of dicom pixel image.
    :param total_pixel_matrix_cols : the total columns of dicom pixel image.
    '''
    try:
        if len(data.shape) == 3:
            return data

        base_tile_rows = data.shape[1]
        base_tile_cols = data.shape[2]

        row_ceil = math.ceil(total_pixel_matrix_rows / base_tile_rows)
        col_ceil = math.ceil(total_pixel_matrix_cols / base_tile_cols)
        data = convert_color_space(data, "YBR_FULL", "RGB")
        patched_image = None
        for row in range(0,row_ceil):
            horz_array = None
            for col in range(0,col_ceil):
                index = row*(col_ceil) + col
                if horz_array is None:
                    horz_array = data[index]
                else:
                    horz_array = np.hstack((horz_array,data[index]))
            if patched_image is None:
                patched_image = horz_array
            else:
                patched_image = np.vstack((patched_image, horz_array))

        # Chop off the excess unnecessary parts of the image.
        patched_image = patched_image[:total_pixel_matrix_rows, :total_pixel_matrix_cols]

        return patched_image
    except Exception as e:
        print("Caught an error in get_patched_image function : ", e)

####### Helper function to extract patched data from dcm file #######
def extract_pixel_data(file_name):
    '''
    The main function that will extract the pixel data from a dicom file. 
    
    :param file_name: path of the dicom file saved.
    '''
    try:
        dicom = pydicom.dcmread(file_name)
        data = dicom.pixel_array
        if len(data.shape) == 2 or len(data.shape) == 3: # checks if it is just 1 image
            data = data - np.min(data)
            data = data / np.max(data)
            data = (data * 255).astype(np.uint8)
            data = convert_color_space(data, "YBR_FULL", "RGB")
            return data
        total_pixel_matrix_rows = dicom.TotalPixelMatrixRows
        total_pixel_matrix_cols = dicom.TotalPixelMatrixColumns
        image = get_patched_image(data,total_pixel_matrix_rows, total_pixel_matrix_cols)
        return image
    except Exception as e:
        print("Caught an error in extract_pixel_data function : ", e)

####### Helper function to test the PUT /v1/scan/start API #######
def start_scan(algorithm_id, slide_name, stain_name, organ_name, api_port, path_to_output):
    """
    Start a scan with the specified parameters.
    Will call PUT /v1/scan/start and will return a 200 response code.

    :param algorithm_id: The ID of the algorithm used for scanning.
    :param slide_name: The name of the slide.
    :param stain_name: The name of the stain.
    :param organ_name: The name of the organ.
    :param api_url: The URL of the API.
    :param path_to_output: The path to the output file.
    """
    try:
        start_scan_payload = {
            "algorithm_id": algorithm_id,
            "slide_name": slide_name,
            "stain_name": stain_name,
            "organ_name": organ_name,
            "tile_width": 1912,
            "tile_height": 1192,
            "path_to_output": path_to_output,
        }
        print("Testing the PUT /v1/scan/start API")
        print(f"Sending payload : {start_scan_payload}")
        api_url = f"http://localhost:{api_port}"
        res = requests.put(api_url + "/v1/scan/start", json=start_scan_payload)
        if res.status_code == 200:
            print("Scan Started. Status code received  : ", res.status_code)
        else:
            print("Status code received : ", res.status_code)
    except Exception as e:
        print("Caught an error in start_scan function : ", e)

####### Helper function to test the POST /v1/scan/image-tile API #######
def process_tiles(
    api_port,
    slide_name,
    input_file_path,
    file_path_to_docker,
    abort_scan=False,
    is_docker_running=False
):
    """
    Access the tiles in the specified directory and submit them to the API as
    image tiles for scanning.
    
    Will call POST /v1/scan/image-tile API and will return a 202 response code.

    :param api_url: The URL of the API.
    :param slide_name: The name of the slide.
    :param TILES_DIR_PATH: The path to the directory containing the tiles.
                           Defaults to './data/DEID-ID-2_H01EBB55P-86.ome_tiles_input/'.
    """
    try:
        print("Testing the POST /v1/scan/image-tile API")
        tiles_dir_path = os.path.splitext(input_file_path)[0] + "_tiles_input"
        docker_base_dir = os.path.splitext(file_path_to_docker)[0] + "_tiles_input"
        counter = 0
        print("Logging the next print statements for every 200th POST request.")
        abort_index = random.randint(0, len(os.listdir(tiles_dir_path)))
        for file_name in os.listdir(tiles_dir_path):
            if file_name.endswith('.bmp'):
                tile_name, _ = os.path.splitext(file_name)
                _, row_idx, column_idx = tile_name.split('_')
                tile_image_path = os.path.join(tiles_dir_path  , file_name)
                if is_docker_running:
                    tile_image_path = os.path.join(docker_base_dir  , file_name)
                image_tile_payload = {
                    "slide_name": slide_name,
                    "tile_name": file_name,
                    "tile_image_path": tile_image_path,
                    "row_idx": row_idx,
                    "col_idx": column_idx
                }
                counter +=1
                if counter == 1:
                    print(f"Sending payload : {image_tile_payload}")

                api_url = f"http://localhost:{api_port}"
                if abort_scan and counter == abort_index:
                    image_tile_payload = {
                        "slide_name" : slide_name
                    }
                    res = requests.put(api_url + "/v1/scan/abort", json=image_tile_payload)
                    print("calling PUT /v1/scan/abort")
                    if res.status_code == 204:
                        print("Scan Aborted")
                        exit()

                res = requests.post(api_url + "/v1/scan/image-tile", json=image_tile_payload)
                if counter % 200 == 0:
                    if res.status_code == 202:
                        print(f"Tile Posted. Status Code received : {res.status_code}")
                    else:
                        print(f"""failed to submit tile {tile_name},
                              row {row_idx}, column {column_idx},
                              image path {image_tile_payload['tile_image_path']}""")
    except Exception as e:
        print("Caught an error in process_tiles function : ", e)

####### Helper function to test the PUT /v1/scan/end API #######
def end_scan( api_port, slide_name):
    """
    End the scan for the specified slide.
    Will call PUT /v1/scan/end and will return a 204 status code.

    :param api_url: The URL of the API.
    :param slide_name: The name of the slide.
    """
    try:
        # End scan
        print("Testing the PUT /v1/scan/end API")
        end_scan_payload = {
            "slide_name": slide_name
        }
        print(f"Sending payload : {end_scan_payload}")
        api_url = f"http://localhost:{api_port}"
        res = requests.put(api_url + "/v1/scan/end", json=end_scan_payload)
        if res.status_code == 204:
            print("Scan Completed Successfully. Received a 204 Response.")
        else:
            print("Scan Failed")
    except Exception as e:
        print("Caught an error in end_scan function : ", e)

####### Helper function to test the POST /v1/postprocessing-data API #######
def send_pp_data(api_port):
    try:
        api_url = f"http://localhost:{api_port}/v1/postprocessing-data"
        with open('./data/postprocessing-data.json', 'r') as f:
            payload = json.load(f)

        time.sleep(5)
        res = requests.post(api_url, json=payload)
    except Exception as e:
        print("Caught an error in send_pp_data: ", e)

####### Helper function to crop images to bmp files in 2048x2048 size #######
def extract_tiles(input_file_path):
    """
    Extract tiles from the specified OME-TIFF file and save them as BMP files.

    :param ome_tif_file_path: The path to the OME-TIFF file.
    """
    try:
        file_size = os.path.getsize(input_file_path)
        time = int(file_size * 3.5 // 543367358)
        print(f"Estimated time to extract .bmp files : {time + 1} - {time + 2} minutes")
        tiles_path = os.path.splitext(input_file_path)[0] + "_tiles_input"
        extension = input_file_path # Checking extension whether it is a dcm file or a ome.tif file
        os.makedirs(tiles_path) ## Make a directory for the bmp files
        if 'tif' in extension:
            with tifffile.TiffFile(input_file_path) as tiff:
                base_image = tiff.pages[0] ## Extract the base image from the ome.tif file
            base_image = base_image.asarray()


        elif 'dcm' in extension:
            base_image = extract_pixel_data(input_file_path)


        counter = 0
        for i in tqdm(range(0, base_image.shape[0], 1192)):
            for j in range(0, base_image.shape[1], 1912):
                extracted_image = base_image[i:i+1192, j:j+1912]
                image = Image.fromarray(extracted_image)
                image.save(tiles_path + f"/tile_{i}_{j}.bmp")
                counter +=1
        print("All tiles extracted successfully!!")

    except Exception as e:
        print("Caught an error in extract_tiles function : ", e)

def main():
    ####### Import the constants from the config.ini file #######
    config = configparser.ConfigParser()
    config.read('config.ini')
    input_file_name=config.get('DEFAULT', 'INPUT_FILE_NAME')
    base_path=config.get('DEFAULT', 'BASE_PATH')
    algorithm_id = config.get('DEFAULT', 'ALGORITHM_ID')
    slide_name = config.get('DEFAULT', 'SLIDE_NAME')
    stain_name = config.get('DEFAULT', 'STAIN_NAME')
    organ_name =config.get('DEFAULT', 'ORGAN_NAME')
    api_port = config.get('DEFAULT', "API_PORT")
    path_to_output = config.get('DEFAULT', "PATH_TO_OUTPUT")

    file_path = os.path.join(base_path, 'data', input_file_name)

    print("*" * 68)
    print("*" + " " * 33 + "*" + " " * 32 + "*")
    print("*" + " " * 14 + "Welcome to Pramana's Inline Simulator!" + " " * 14 + "*")
    print("*" + " " * 33 + "*" + " " * 32 + "*")
    print("*" * 68)
    print()
    # Create the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode if -i is present."
    )
    parser.add_argument(
        "-d",
        "--docker",
        action="store_true",
        help="Run with -d if the algorithm api service is running as a docker container"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if the -i flag is present
    if args.interactive:
        ####### Helper function to crop images to bmp files in 1936x1216 size #######
        while True:
            response = input("""Do you wish to start extracting tiles from the input file ?
                             Note: If you have already saved the .bmp files you can skip
                             to the API part by pressing No [Y/N] : """)
            if response.upper() == "Y" or response.upper() == "YES":
                extract_tiles(file_path)
                break

            if response.upper() == "N" or response.upper() == "NO":
                response_1 = input("""Do you wish to proceed to the API requests if you
                have already saved the tiles before ? [Y/N] : """)
                if response_1.upper() == "Y" or response_1.upper() == "YES":
                    break

                if response_1.upper() == "N" or response_1.upper() == "NO":
                    return
                print("Invalid Response. Please try again...")

            else:
                print("Invalid Response. Please try again...")

        while True:
            response_abort = input("Do you wish to simulate the /v1/scan/abort API call ? [Y/N]: ")
            if response_abort.upper() == "Y" or response_abort.upper() == "YES":
                abort_bool = True
                break

            if response_abort.upper() == "N" or response_abort.upper() == "NO":
                abort_bool = False
                break
            print("Invalid Response. Please try again...")

        while True:
            response = input("Do you wish to simulate the API requests ? [Press Enter]: ")
            if response.upper() == "" or response.upper() == "":
                ####### Helper function to test the PUT /v1/scan/start API #######
                start_scan(
                    algorithm_id,
                    slide_name,
                    stain_name,
                    organ_name,
                    api_port,
                    path_to_output
                )
                ####### Helper function to test the POST /v1/scan/image-tile API #######
                file_path_to_docker = os.path.join('/data/acquired_data',  input_file_name)
                process_tiles(
                    api_port,
                    slide_name,
                    file_path,
                    file_path_to_docker,
                    abort_bool,
                    args.docker
                )
                ####### Helper function to test the PUT /v1/scan/end API #######
                end_scan(api_port, slide_name)

                ###### Helper function to test the POST /v1/postprocessing-data #######
                send_pp_data(api_port)
                break
            if response.upper() == "N" or response.upper() == "NO":
                return
            print("Invalid Response. Please try again...")
    else:
        ####### Helper function to crop images to bmp files in 1936x1216 size #######
        extract_tiles(file_path)
        ####### Helper function to test the PUT /v1/scan/start API #######
        start_scan(
            algorithm_id,
            slide_name,
            stain_name,
            organ_name,
            api_port,
            path_to_output
        )
        ####### Helper function to test the POST /v1/scan/image-tile API #######
        file_path_to_docker = os.path.join('/data/acquired_data',  input_file_name)
        process_tiles(
            api_port,
            slide_name,
            file_path,
            file_path_to_docker,
            is_docker_running=args.docker
        )
        ####### Helper function to test the PUT /v1/scan/end API #######
        end_scan(api_port, slide_name)

        ###### Helper function to test the POST /v1/postprocessing-data #######
        send_pp_data(api_port)

if __name__ == "__main__":
    main()
