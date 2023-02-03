import json
import os
from typing import Union, List
import base64
from io import BytesIO
from PIL import Image
import cv2
from fastapi import APIRouter, Depends, Request
import logging

from fastapi.encoders import jsonable_encoder
from fastapi.openapi.models import Response

from hb.api import get_database
# from pin.api.auth import check_user, check_token
# from pin.api.websocket import WebsocketManager
from hb.clients.mongodb import AsyncMongodbClient
from hb.core.serialization import PyObjectId
from hb.models.record import Scenario

# from pin.signals.auth import User, Token
# from pin.signals.storage import FileUpload, FileUploadPreview, FileInput

router = APIRouter()

log = logging.getLogger(__name__)


@router.get('/record/models',
            tags=['record'],
            response_model=Union[None,Scenario])
async def models(database: AsyncMongodbClient = Depends(get_database),
                 request: Request = None):
    return None


@router.get('/record/scenarios',
            tags=['record'],
            response_model=List[Scenario])
async def scenarios(database: AsyncMongodbClient = Depends(get_database),
                    request: Request = None):
    items = await Scenario.all(database, {})
    ret = []
    for item in items:
        content = jsonable_encoder(item)
        ret.append(content)
    folder = os.path.join(os.getcwd(), 'recordings')
    print(folder)
    for item in os.listdir(folder):
        fpath = os.path.join(folder,item)
        if os.path.isdir(fpath):
            with open(os.path.join(fpath, 'events.json'), 'r') as f:
                data = json.load(f)
                content = jsonable_encoder(Scenario.parse_obj(data))
                ret.append(content)
    return ret


@router.get('/record/scenario',
            tags=['record'],
            response_model=Union[None, Scenario])
async def scenario(database: AsyncMongodbClient = Depends(get_database),
                   request: Request = None):
    items = await Scenario.find(database, {''})
    ret = []
    for item in items:
        content = jsonable_encoder(item)
        ret.append(content)
    folder = os.path.join(os.getcwd(),'recordings')
    print(folder)
    for item in os.listdir(folder):
        if os.path.isdir(item):
            with open(os.path.join(item,'events.json'),'r') as f:
                data = json.load(f)
                content = jsonable_encoder(Scenario.parse_obj(data))
                ret.append(content)
    return ret


@router.get('/record/frame',
            tags=['record'],
            response_model=Union[None,str])
async def frame(scenario: str,
                number: int,
                database: AsyncMongodbClient = Depends(get_database),
                request: Request = None):
    folder = os.path.join(os.getcwd(),'recordings')
    fpath = os.path.join(os.path.join(folder, scenario))
    filename = os.path.join(fpath, 'video.avi')
    vidcap = cv2.VideoCapture(filename)
    success, image = vidcap.read()
    success = True
    count = 0
    previous = None
    while success:

        # vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
        success, image = vidcap.read()
        if count == number:
            _, im_arr = cv2.imencode('.png', image)  # im_arr: image in Numpy one-dim array format.
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            return im_b64.decode("utf-8")
        count +=1

    return None
