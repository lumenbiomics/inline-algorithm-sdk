
from models import ScanStart, ScanOngoing, ScanEnd, ScanAbort
import cv2
import numpy as np
import requests
import os
import json
from skimage import io, color, measure
import cv2


def findContourArea(countour):
    c = np.expand_dims(countour.astype(np.float32), 1)
    # Convert it to UMat object
    c = cv2.UMat(c)
    area = cv2.contourArea(c)
    return area, c

def model_detection_helper(model, path):
    ##TODO: you the 'model' here for your image analysis algorithm
    image = io.imread(path)
    gray_image = color.rgb2gray(image)

    # Find contours
    contours = measure.find_contours(gray_image, 0.3, 'low')

    struct_countours = []

    cnt = 0
    for contour in contours:
        cnt += 1
        area, cv2_cont = findContourArea(contour)
        cont_dict = {"contour":contour, "area":area, "color":None,"id":cnt,"cv2_cont":cv2_cont}
        struct_countours.append(cont_dict)
    res = [] 
    if contours:
        areas = [x['area'] for x in struct_countours]
        percentile_high = np.percentile(areas, 98)
        percentile_low = np.percentile(areas, 95)
        
        filtered_contours = [x for x in struct_countours if x['area'] > percentile_low and x['area'] < percentile_high]
        for cont in filtered_contours:
            centroid_x = int(cont['contour'][:, 1].mean())
            centroid_y = int(cont['contour'][:, 0].mean())
            res.append([centroid_x, centroid_y, 1, 'Mitosis'])

    return res

def api_call_handler_loop(api_call_queue, is_running_as_docker, error_event, model):
    try:
        while True:
            message = api_call_queue.get()
            if type(message) == ScanStart:
                algorithm_id = message.algorithm_id
                slide_name = message.slide_name
                organ_name = message.organ_name
                path_to_output = message.path_to_output
                print('start scan message processed')
            elif type(message) == ScanOngoing:
                path = message.tile_image_path
                slide_name = message.slide_name
                tile_name = message.tile_name
                row_idx = message.row_idx
                col_idx = message.col_idx
                results = model_detection_helper(model, path)
                data_json = {
                    "algorithm_id": algorithm_id,
                    "slide_name": slide_name,
                    "tile_name": tile_name,
                    "results": {
                    "detection_array": results,
                    "row_idx": row_idx,
                    "col_idx": col_idx
                    }
                } 
                url = 'http://localhost:8001/v1/tile-results'
                if is_running_as_docker:
                    url = 'http://host.docker.internal:8001/v1/tile-results'
                requests.post(url, data = json.dumps(data_json), timeout=1)

            elif type(message) == ScanEnd:
                data_json = {
                "algorithm_id": algorithm_id,
                "slide_name": slide_name
                }
                url = 'http://localhost:8001/v1/algorithm-completed'
                if is_running_as_docker:
                    url = 'http://host.docker.internal:8001/v1/algorithm-completed'
                requests.post(url, data = json.dumps(data_json), timeout=1)
                print('scan ended')

            elif type(message) == ScanAbort:
                algorithm_id = None
                slide_name = None

    except BaseException as e:
        error_event.set()
        raise e
