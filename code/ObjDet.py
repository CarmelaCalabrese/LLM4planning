
import yarp
import sys
import time
import json
import base64
import os.path
import importlib
import inspect
from io import BytesIO
from typing import (
    Literal,
    Union,
)
import numpy as np
from datetime import datetime
import torch
from transformers import Owlv2Processor, Owlv2ForObjectDetection
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


class ObjDet(yarp.RFModule):

    def configure(self, rf) :
        self.period = 2.0

        self.ObjDet_rpc_portName = "/objDet/rpc"
        self.ObjDet_rpc_port = yarp.Port()
        self.ObjDet_rpc_port.open(self.ObjDet_rpc_portName)
        self.attach(self.ObjDet_rpc_port)

        # ----------- INPUT PORT ----------
        # input port for image with bboxes
        self._input_image_port = yarp.BufferedPortImageRgb()
        imageInPortName = '/objDet/image:i'
        self._input_image_port.open(imageInPortName)
        print('{:s} opened'.format(imageInPortName))

        print('Preparing input image...')
        self._in_buf_array = np.ones((480, 640, 3), dtype=np.uint8)
        self._in_buf_image = yarp.ImageRgb()
        self._in_buf_image.resize(640, 480)
        self._in_buf_image.setExternal(self._in_buf_array.data, self._in_buf_array.shape[1], self._in_buf_array.shape[0])
        print('... ok \n')

        # ----------- OUTPUT PORT ----------
        # output port for image with bboxes
        self._output_image_port = yarp.Port()
        imageOutPortName = '/objDet/image:o'
        self._output_image_port.open(imageOutPortName)
        print('{:s} opened'.format(imageOutPortName))
     
        print('Preparing output image...')
        self._out_buf_array = np.ones((480, 640, 3), dtype=np.uint8)
        self._out_buf_image = yarp.ImageRgb()
        self._out_buf_image.resize(640, 480)
        self._out_buf_image.setExternal(self._out_buf_array.data, self._out_buf_array.shape[1], self._out_buf_array.shape[0])
        print('... ok \n')

        self.obj_image = np.ones((480, 640, 3), dtype=np.uint8)

        # Load the processor and model
        self.processor = Owlv2Processor.from_pretrained("google/owlv2-base-patch16")
        self.model = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16")

        return True
               




    def find_obj(self, image, text_queries):
        # Define text queries
        # text_queries = ["a knife", "a fork", "a spoon", "a cup", "tomatos", "kettle"]

        # Preprocess the inputs
        inputs = self.processor(text=text_queries, images=image, return_tensors="pt")

        # Perform object detection
        with torch.no_grad():
            print('Performing object detection...')
            outputs = self.model(**inputs)

        # Extract boxes and scores
        target_sizes = torch.tensor([image.size[::-1]])  # Convert (W, H) to (H, W)
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.1)

        

        # Draw the bounding boxes
        draw = ImageDraw.Draw(image)

        # Try loading a larger font, otherwise use default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)  # Bigger font for visibility
        except:
            font = ImageFont.load_default()

        print("\n🔹 **All Detections Before Filtering:**")
        # Draw the bounding boxes with proper text background
        # Draw the bounding boxes with proper text background and centroids
        for result in results:
            for score, label, box in zip(result["scores"], result["labels"], result["boxes"]):
                raw_score = score.item()
                rounded_score = round(raw_score, 1)

                #label_name = model.config.id2label[label.item()]
                label_name = text_queries[label.item()]
                box = [round(i, 2) for i in box.tolist()]  # Round box coordinates
                print(f"🔍 Detected: {label_name} with confidence {raw_score:.6f} (Rounded: {rounded_score}) at {box}")

                if rounded_score >= 0.40:
                    # Draw the bounding box
                    draw.rectangle(box, outline="red", width=2)

                    # Calculate and draw the centroid
                    centroid_x = (box[0] + box[2]) / 2  # Average of x-coordinates
                    centroid_y = (box[1] + box[3]) / 2  # Average of y-coordinates
                    draw.ellipse(
                        [
                            (centroid_x - 2, centroid_y - 2),  # Top-left of the circle
                            (centroid_x + 2, centroid_y + 2),  # Bottom-right of the circle
                        ],
                        fill="blue", outline="blue", width=0.5,
                    )

                    # Text and background
                    text = f"{label_name}: {rounded_score}"
                    text_width, text_height = draw.textsize(text, font=font)

                    # Ensure text background stays within image boundaries
                    text_x = box[0]
                    text_y = max(0, box[1] - text_height - 5)  # Avoid cutting off at the top

                    # Adjust rectangle dimensions for the text
                    rect_x1 = text_x
                    rect_y1 = text_y
                    rect_x2 = text_x + text_width
                    rect_y2 = text_y + text_height

                    # Draw the black background rectangle
                    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill="black")

                    # Draw the label text
                    draw.text((text_x, text_y), text, fill="yellow", font=font)

        return image

                           

    def respond(self, command, reply):
        if command.get(0).asString()=='find_obj':
            print('Received command FIND_OBJ')
            text_query = command.get(1).asString()
            print('Text query:', text_query)
            received_image = self._input_image_port.read()
            self._in_buf_image.copy(received_image)   
            frame = self._in_buf_array
            img=Image.fromarray(np.uint8(frame)).convert('RGB')
            text_query = command.get(1).asString()
            obj_image = self.find_obj(img, text_query)
            self._out_buf_array[:, :] = obj_image
            self._output_image_port.write(self._out_buf_image)
            reply.addString('Done')
        return True



    
    def updateModule(self):
      
        print('ObjDet module running...')

        return True

    def getPeriod(self):
        return self.period
    
        
    def close(self):
        self.ObjDet_rpc_port.close()
        self._input_image_port.close()
        return True
    
    
    def interruptModule(self):
        self.ObjDet_rpc_port.interrupt()   
        self._input_image_port.interrupt()
        return True
    
#########################################333

if __name__ == '__main__':
    
    yarp.Network.init()

    mod = ObjDet()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
