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

---

Handler for acquisition messages
'''
import os
import cv2

from models_scanner import TileResults, AlgorithmCompleted

def api_call_handler_scanner(api_call_queue, base_path, input_file_name, error_event):
    try:
        while True:
            message = api_call_queue.get()
            if isinstance(message, TileResults):
                algorithm_id = message.algorithm_id
                results = message.results
                tile_name = message.tile_name
                slide_name = message.slide_name
                detection_array = results.get('detection_array')
                print(detection_array)
                if len(detection_array) > 0:
                    input_file_path = os.path.join(base_path, 'data', input_file_name)
                    tiles_path = os.path.splitext(input_file_path)[0] + "_tiles_input"
                    source_img_path = os.path.join(tiles_path, tile_name)
                    image = cv2.imread(source_img_path)
                    for detection in detection_array:
                        x1, y1, _, _ = detection
                        # Draw a rectangle on the image
                        image = cv2.circle(image, (x1, y1), 20, (255, 0, 0) , 2)
                    output_path = os.path.join(base_path,'output', tile_name)
                    cv2.imwrite(output_path, image)
            elif isinstance(message, AlgorithmCompleted):
                print('algorithm completed hit')

    except BaseException as e:
        error_event.set()
        raise e
