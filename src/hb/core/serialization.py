import base64
import dataclasses
import json
import logging
import os
import time

from datetime import datetime
from io import BytesIO
from uuid import uuid4

import numpy as np
import bson
import dateutil.parser
import pytz
from PIL.PngImagePlugin import PngImageFile
from bson import ObjectId
from dataclasses_serialization.bson import bson_int_deserializer
from dataclasses_serialization.serializer_base import Serializer, dict_serialization, dict_deserialization, \
    list_deserialization, noop_serialization, noop_deserialization, DeserializationError, SerializationError
from pydantic import BaseModel

from hb.core.reflection import Reflection

log = logging.getLogger(__name__)


def mongo_datetime_deserializer(cls, obj):
    """
    Mongo implicitly converts ints to floats
    Attempt to coerce back
    Fail if coercion lossy
    """

    if isinstance(obj, cls):
        return obj
    try:
        return dateutil.parser.parse(str(obj))
    except:
        coerced_obj = None
    if coerced_obj == obj:
        return coerced_obj

    raise DeserializationError("Cannot deserialize {} {!r} to type {}".format(
        type(obj).__name__,
        obj,
        cls.__name__
    ))


def bytes_deserializer(cls, obj):
    #
    if isinstance(obj, cls):
        return obj

    try:
        return base64.b64decode(str(obj))
    except:
        coerced_obj = None

    if coerced_obj == obj:
        return coerced_obj

    raise DeserializationError("Cannot deserialize {} {!r} to type {}".format(
        type(obj).__name__,
        obj,
        cls.__name__
    ))


def bytes_serializer(obj):
    return base64.b64encode(obj).decode("utf-8")


def mongo_datetime_serializer(obj):
    return obj.isoformat()


def numpy_serializer(obj):
    return obj.tolist()


def time_serializer(obj: time.struct_time):
    dt = datetime.fromtimestamp(time.mktime(obj))
    dt = pytz.UTC.localize(dt)
    return dt.isoformat()


def numpy_deserializer(cls, obj):
    #
    if isinstance(obj, cls):
        return obj

    try:
        return np.asarray(obj)
    except:
        coerced_obj = None

    if coerced_obj == obj:
        return coerced_obj

    raise DeserializationError("Cannot deserialize {} {!r} to type {}".format(
        type(obj).__name__,
        obj,
        cls.__name__
    ))


def number_serializer(obj):
    return obj


def number_deserializer(obj):
    return obj


def bool_serializer(obj):
    return obj


def bool_deserializer(cls, obj):
    return obj


def image_serializer(image):
    # ========= SERIALIZE
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = base64.b64encode(buffered.getvalue())
    img_str = img_bytes.decode('utf-8')
    return img_str


def image_deserializer(cls, source):
    # ========= DESERIALIZE
    r_img_bytes = source.encode('utf-8')
    r_buffered = base64.b64decode(r_img_bytes)
    r_buffer = BytesIO(r_buffered)
    r_image = PngImageFile(r_buffer)
    return r_image


def objectid_serializer(source):
    return str(source)

def pyobjectid_serializer(source):
    return ObjectId(str(source))

def objectid_deserializer(source):
    if source is None or source is not str:
        raise DeserializationError("Cannot deserialize {} {!r} to type {}".format(
            type(source).__name__,
            source,
            source.__name__
        ))
    return bson.ObjectId(source)


def pyobjectid_deserializer(source):
    if source is None or source is not str:
        raise DeserializationError("Cannot deserialize {} {!r} to type {}".format(
            type(source).__name__,
            source,
            source.__name__
        ))
    return PyObjectId(source)


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')




CustomSerializer = Serializer(
    serialization_functions={
        dict: lambda dct: dict_serialization(dct, key_serialization_func=CustomSerializer.serialize,
                                             value_serialization_func=CustomSerializer.serialize),
        list: lambda lst: list(map(CustomSerializer.serialize, lst)),
        datetime: mongo_datetime_serializer,
        time.struct_time: time_serializer,
        PngImageFile: image_serializer,
        bool: bool_serializer,
        bytes: bytes_serializer,
        np.ndarray: numpy_serializer,
        bson.ObjectId: objectid_serializer,
        PyObjectId: objectid_serializer,
        (str, int, float, type(None)): noop_serialization
    },
    deserialization_functions={
        dict: lambda cls, dct: dict_deserialization(cls, dct, key_deserialization_func=CustomSerializer.deserialize,
                                                    value_deserialization_func=CustomSerializer.deserialize),
        list: lambda cls, lst: list_deserialization(cls, lst, deserialization_func=CustomSerializer.deserialize),
        int: bson_int_deserializer,
        datetime: mongo_datetime_deserializer,
        PngImageFile: image_deserializer,
        np.ndarray: numpy_deserializer,
        bool: bool_deserializer,
        bytes: bytes_deserializer,
        PyObjectId: pyobjectid_deserializer,
        bson.ObjectId: objectid_deserializer,
        (str, float, type(None)): noop_deserialization
    }

)

MongoDBSerializer = Serializer(
    serialization_functions={
        dict: lambda dct: dict_serialization(dct, key_serialization_func=CustomSerializer.serialize,
                                             value_serialization_func=CustomSerializer.serialize),
        list: lambda lst: list(map(CustomSerializer.serialize, lst)),
        datetime: mongo_datetime_serializer,
        time.struct_time: time_serializer,
        PngImageFile: image_serializer,
        bool: bool_serializer,
        PyObjectId: pyobjectid_serializer,
        bytes: bytes_serializer,
        np.ndarray: numpy_serializer,
        (str, int, float, bson.ObjectId,  type(None)): noop_serialization
    },
    deserialization_functions={
        dict: lambda cls, dct: dict_deserialization(cls, dct, key_deserialization_func=CustomSerializer.deserialize,
                                                    value_deserialization_func=CustomSerializer.deserialize),
        list: lambda cls, lst: list_deserialization(cls, lst, deserialization_func=CustomSerializer.deserialize),
        int: bson_int_deserializer,
        datetime: mongo_datetime_deserializer,
        PngImageFile: image_deserializer,
        np.ndarray: numpy_deserializer,
        bool: bool_deserializer,
        bytes: bytes_deserializer,
        (str, float, bson.ObjectId, PyObjectId, type(None)): noop_deserialization
    }

)


class MarshallSerializer(Serializer):
    def serialize(self, obj):
        jsoned = Serializer.serialize(self, obj)
        jsoned['_cls'] = "{0}.{1}".format(obj.__module__, obj.__class__.__name__)
        return jsoned

    def deserialize(self, cls, serialized_obj):
        if type(serialized_obj) is dict and '_cls' in serialized_obj:
            log.debug('Inner Unmarshalling: {0}'.format(serialized_obj['_cls']))
            clz = Reflection.load(serialized_obj['_cls'])
            del serialized_obj['_cls']
            return Serializer.deserialize(self, clz, serialized_obj)
        else:
            return Serializer.deserialize(self, cls, serialized_obj)


CustomMarshaller = MarshallSerializer(
    serialization_functions={
        dict: lambda dct: dict_serialization(dct, key_serialization_func=CustomMarshaller.serialize,
                                             value_serialization_func=CustomMarshaller.serialize),
        list: lambda lst: list(map(CustomMarshaller.serialize, lst)),
        datetime: mongo_datetime_serializer,
        PngImageFile: image_serializer,
        PyObjectId: objectid_serializer,
        bytes: bytes_serializer,
        np.ndarray: numpy_serializer,
        bson.objectid: objectid_serializer,
        (str, int, float, bool, type(None)): noop_serialization
    },
    deserialization_functions={
        dict: lambda cls, dct: dict_deserialization(cls, dct, key_deserialization_func=CustomMarshaller.deserialize,
                                                    value_deserialization_func=CustomMarshaller.deserialize),
        list: lambda cls, lst: list_deserialization(cls, lst, deserialization_func=CustomMarshaller.deserialize),
        int: bson_int_deserializer,
        PngImageFile: image_deserializer,
        datetime: mongo_datetime_deserializer,
        np.ndarray: numpy_deserializer,
        PyObjectId: pyobjectid_deserializer,
        bson.objectid: objectid_deserializer,
        bool: bool_deserializer,
        bytes: bytes_deserializer,
        (str, float, type(None)): noop_deserialization
    }
)


class Serializer:

    @staticmethod
    def json_expandvars(o):
        if isinstance(o, dict):
            return {Serializer.json_expandvars(k): Serializer.json_expandvars(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [Serializer.json_expandvars(v) for v in o]
        elif isinstance(o, str):
            if o.startswith('i$'):
                return int(os.path.expandvars(o[1:]))
            elif o.startswith('b$'):
                return bool(os.path.expandvars(o[1:]))
            else:
                return os.path.expandvars(o)
        else:
            return o

    @staticmethod
    def read(cls, filename, expand_variables=False):
        with open(filename, 'r') as fp:
            data = json.load(fp)
        if expand_variables:
            data = Serializer.json_expandvars(data)
        return Serializer.deserialize(cls, data)

    @staticmethod
    def write(obj, filename):
        with open(filename, 'w') as fp:
            json.dump(Serializer.serialize(obj), fp)

    @staticmethod
    def serialize(object):
        return CustomSerializer.serialize(object)

    @staticmethod
    def mongonize(object):
        return MongoDBSerializer.serialize(object)

    @staticmethod
    def demongonize(clazz, jsoned):
        if '_id' in jsoned:
            id = jsoned['_id']
            del jsoned['_id']
            jsoned['id'] = PyObjectId(str(id))
        return MongoDBSerializer.deserialize(clazz, jsoned)

    @staticmethod
    def deserialize(clazz, jsoned):
        return CustomSerializer.deserialize(clazz, jsoned)

    @staticmethod
    def marshall(object):
        jsoned = CustomMarshaller.serialize(object)
        return jsoned

    @staticmethod
    def unmarshall(jsoned):
        clazz = Reflection.load(jsoned['_cls'])
        log.info('Unmarshalling: {0}'.format(jsoned['_cls']))
        del jsoned['_cls']
        return CustomMarshaller.deserialize(clazz, jsoned)

    @staticmethod
    def datetime_default():
        today = datetime.utcnow()
        # today = pytz.UTC.localize(today)
        return today

    @staticmethod
    def timestamp_default():
        return (datetime.utcnow().toordinal() -  datetime(1970, 1, 1).toordinal()) * 24 * 60 * 60

    @staticmethod
    def dict_default():
        return {}

    @staticmethod
    def string_default():
        return ''

    @staticmethod
    def uuid_default():
        return str(uuid4())

    @staticmethod
    def list_default() -> list:
        return []

    @staticmethod
    def index(obj):
        return "{0}.{1}".format(obj.__module__, obj.__name__)

    @staticmethod
    def signature(obj):
        return "{0}.{1}".format(obj.__module__, obj.__name__)

    @staticmethod
    def text_indexes(object):
        fields = dataclasses.fields(object)
        ret = []
        for field in fields:
            metadata = field.metadata
            if 'text_index' in metadata and metadata['text_index'] and field.name not in ret:
                ret.append(field.name)
        return ret

    @staticmethod
    def fields(cls):
        return dataclasses.fields(cls)


class CeleryEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
           ret = obj.dict(by_alias=True)
           ret['_cls'] = '{0}.{1}'.format(obj.__module__,obj.__class__.__name__)
           return ret
        elif isinstance(obj,datetime):
            return obj.isoformat()
        elif isinstance(obj,ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def celery_decoder(obj):
    if '_cls' in obj:
        clazz = Reflection.load(obj['_cls'])
        del obj['_cls']
        return clazz.parse_obj(obj)
    return obj

# Encoder function
def celery_dumps(obj):
    return json.dumps(obj, cls=CeleryEncoder)

# Decoder function
def celery_loads(obj):
    return json.loads(obj, object_hook=celery_decoder)