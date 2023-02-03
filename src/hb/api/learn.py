import base64
import logging
from typing import Union

from fastapi import APIRouter, Depends
from starlette.requests import Request
import os.path
import cv2
from hb.api import get_database
from hb.clients.mongodb import AsyncMongodbClient
import numpy as np
from pytesseract import Output
import pytesseract

from hb.learn.label import YoloLabel

router = APIRouter()

log = logging.getLogger(__name__)



@router.post('/learn/label',
             tags=['learn'],
             response_model=bool)
async def label(req: YoloLabel,
              database: AsyncMongodbClient = Depends(get_database),
              request: Request = None):
    await req.insert(database)
    return True

@router.get('/learn/ocr',
            tags=['learn'],
            response_model=Union[None, str])
async def ocr(scenario: str,
              number: int,
              database: AsyncMongodbClient = Depends(get_database),
              request: Request = None):
    folder = os.path.join(os.getcwd(), 'recordings')
    fpath = os.path.join(os.path.join(folder, scenario))
    filename = os.path.join(fpath, 'video.avi')
    vidcap = cv2.VideoCapture(filename)
    success, image = vidcap.read()
    success = True
    count = 0
    previous = None
    while success:

        # vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
        success, image= vidcap.read()
        if count == number:

            # Clean up image
            norm_img = np.zeros((image.shape[0], image.shape[1]))
            img = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
            img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]
            img = cv2.GaussianBlur(img, (1, 1), 0)

            results = pytesseract.image_to_data(img, output_type=Output.DICT)
            for i in range(0, len(results['text'])):
                x = results['left'][i]
                y = results['top'][i]
                w = results['width'][i]
                h = results['height'][i]

                text = results['text'][i]
                conf = int(results['conf'][i])

                if conf > 50:
                    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)
            _, im_arr = cv2.imencode('.png', image)  # im_arr: image in Numpy one-dim array format.
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            return im_b64.decode("utf-8")
        count +=1
    return None