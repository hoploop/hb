import json
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator


def uid_factory():
    return str(uuid4())


def list_factory():
    return []


def datetime_default():
    today = datetime.utcnow()
    # today = pytz.UTC.localize(today)
    return today


class ElementEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            ret = obj.dict(by_alias=True)
            ret['_cls'] = '{0}.{1}'.format(obj.__module__, obj.__class__.__name__)
            return ret
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

import json
import logging
from datetime import datetime
from typing import Tuple, List, Optional

from bson import ObjectId
from pydantic import Field

from hb.clients.mongodb import AsyncMongodbClient
from hb.core.serialization import PyObjectId
from hb.core.serialization import Serializer

log = logging.getLogger(__name__)


class MongodbEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def serialize_list_pyobjectid(source: List[PyObjectId]):
    ret = []
    for el in source:
        ret.append(str(el))
    return ret


class MongodbDocument(BaseModel):
    id: Optional[PyObjectId] = Field(metadata={'type': 'id', 'admin': True}, alias='_id')
    updated: datetime = Field(default_factory=Serializer.datetime_default,
                              metadata={'type': 'datetime', 'admin': True},
                              alias='_updated')
    created: datetime = Field(default_factory=Serializer.datetime_default,
                              metadata={'type': 'datetime', 'admin': True},
                              alias='_created')

    @classmethod
    def get_signature(cls) -> str:
        return '{0}.{1}'.format(cls.__module__, cls.__name__)


    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}

    async def on_insert(self, client: AsyncMongodbClient, id: ObjectId, current: dict):
        pass

    async def on_replace(self, client: AsyncMongodbClient, id: ObjectId, previous: dict, current: dict):
        pass

    async def on_delete(self, client: AsyncMongodbClient, id: ObjectId, current: dict):
        pass

    async def on_update(self, client: AsyncMongodbClient, id: ObjectId, previous: dict, updates: dict):
        pass

    async def insert(self, client: AsyncMongodbClient) -> ObjectId:
        jsoned = await self.mongonize(self.dict(by_alias=True))

        await self.enrich(client, jsoned)

        self.created = Serializer.datetime_default()
        id = await client.insert_one(self.__class__, jsoned)
        self.id = id
        await self.on_insert(client, id, jsoned)
        return id

    @classmethod
    async def index_field(cls, client: AsyncMongodbClient, field: str, background=False):
        await client.index_field(cls, field, background=background)

    async def update(self, client: AsyncMongodbClient, updates: dict) -> Tuple[int, int]:
        self.updated = Serializer.datetime_default()
        previous = await client.find_one(self.__class__, {"_id": self.id})
        await self.on_update(client, self.id, previous, updates)
        return await client.update_one(self.__class__, {"_id": self.id}, updates)

    async def replace(self, client: AsyncMongodbClient) -> Tuple[int, int]:
        self.updated = Serializer.datetime_default()
        jsoned = await self.mongonize(self.dict(by_alias=True))
        await self.enrich(client, jsoned)

        previous = await client.find_one(self.__class__, {"_id": self.id})
        await self.on_replace(client, self.id, previous, jsoned)
        return await client.replace_one(self.__class__, {"_id": self.id}, jsoned)

    async def delete(self, client: AsyncMongodbClient):
        current = await client.find_one(self.__class__, {"_id": self.id})
        await self.on_delete(client, self.id, current)
        await client.delete_one(self.__class__, {'_id': self.id})

    async def mongonize(self, original: dict):
        ret = {}
        for key in original:
            if original[key] is not None:
                ret[key] = original[key]
        return ret

    async def dictify(self):
        ret = self.dict(by_alias=True)
        for key in ret:
            value = ret[key]
            if isinstance(value, ObjectId):
                if value is not None:
                    ret[key] = str(value)
            if value is list:
                current = []
                for element in value:
                    if isinstance(element, ObjectId):
                        current.append(str(element))
                    else:
                        current.append(element)
                ret[key] = current

        return ret

    async def jsonify(self) -> str:
        payload = self.dict(by_alias=True)
        return json.dumps(payload, cls=MongodbEncoder)

    async def marshall(self):
        payload = await self.dictify()
        signature = '{0}.{1}'.format(self.__module__, self.__class__.__name__)
        return json.dumps({'signature': signature, 'payload': payload}, cls=MongodbEncoder)

    async def enrich(self, client: AsyncMongodbClient, jsoned):
        schema = self.schema()
        for key in schema['properties']:
            field = schema['properties'][key]
            if 'metadata' in field:
                if 'encrypt' in field['metadata'] and field['metadata']['encrypt'] is True and key in jsoned:
                    jsoned[key] = await client.encrypt(jsoned[key])

        return jsoned

    @classmethod
    async def unrich(cls, client: AsyncMongodbClient, jsoned):
        schema = cls.schema()
        for key in schema['properties']:
            field = schema['properties'][key]
            if 'metadata' in field:
                if 'encrypt' in field['metadata'] and field['metadata']['encrypt'] is True and key in jsoned:
                    jsoned[key] = await client.decrypt(jsoned[key])
        return jsoned

    @classmethod
    async def aggregate(cls,
                        client: AsyncMongodbClient,
                        pipeline):
        return await client.aggregate(cls, pipeline)

    @classmethod
    async def list(cls,
                   client: AsyncMongodbClient,
                   query: dict,
                   skip: int = None,
                   limit: int = None,
                   sort: dict = None):
        sig = '{0}.{1}'.format(cls.__module__, cls.__name__)
        result = await client.find_many(cls, query, skip, limit, sort)
        items = []
        for doc in result:
            jsoned = await cls.unrich(client, doc)
            item = cls.parse_obj(jsoned)
            items.append(item)
        return items

    @classmethod
    async def all(cls,
                  client: AsyncMongodbClient,
                  query: dict,
                  sort: dict = None,
                  ):
        sig = '{0}.{1}'.format(cls.__module__, cls.__name__)
        result = await client.find_many(cls, query, sort=sort)
        items = []
        for doc in result:
            jsoned = await cls.unrich(client, doc)
            item = cls.parse_obj(jsoned)
            items.append(item)
        return items

    @classmethod
    async def count(cls, client: AsyncMongodbClient, query: dict):
        return await client.count(cls, query)

    @classmethod
    async def find(cls, client: AsyncMongodbClient, query: dict):
        sig = '{0}.{1}'.format(cls.__module__, cls.__name__)
        doc = await client.find_one(cls, query)
        if doc is None:
            return None
        jsoned = await cls.unrich(client, doc)
        item = cls.parse_obj(jsoned)
        return item

    @classmethod
    async def delete_many(cls, client: AsyncMongodbClient, query: dict):
        await client.delete_many(cls, query)


def normalize_query_list(qry_custom: list) -> list:
    ret = []
    for item in qry_custom:
        if type(item) is str and item.startswith('OID_'):
            ret.append(ObjectId(item[4:]))
        elif type(item) is list:
            ret.append(normalize_query_list(item))
        elif type(item) is dict:
            ret.append(normalize_query(item))
        else:
            ret.append(item)
    return ret


def normalize_query(qry_custom: dict) -> dict:
    ret = {}

    for key in qry_custom.keys():
        value = qry_custom[key]
        if type(value) is str and value.startswith('OID_'):
            ret[key] = ObjectId(value[4:])
        elif type(value) is dict:
            ret[key] = normalize_query(value)
        elif type(value) is list:
            ret[key] = normalize_query_list(value)
        else:
            ret[key] = value
    return ret


def build_query(klass, filter: str) -> dict:
    qry = None
    if filter is not None and filter.strip() != '':
        schema = klass.schema()
        for key in schema['properties']:
            if not key.startswith('_'):
                field = schema['properties'][key]
                if 'metadata' in field and ('filter' in field['metadata']) and field['metadata']['filter']:
                    field_type = None
                    if 'type' in field['metadata']:
                        field_type = field['metadata']['type']
                    elif 'type' in field:
                        field_type = field['type']
                    if field_type is not None:
                        if qry is None:
                            qry = {'$or': []}
                        if field_type == 'string':
                            qry['$or'].append({key: {'$regex': '.*{0}.*'.format(filter), '$options': 'i'}})
                        if field_type == 'tags':
                            filters = filter.strip().split(' ')
                            qry['$or'].append({key: {'$in': filters}})
                        if field_type == 'array':
                            if 'items' in field and 'type' in field['items'] and field['items']['type'] == 'string':
                                filters = filter.strip().split(' ')
                                qry['$or'].append({key: {'$in': filters}})

    return qry


class Element(MongodbDocument):
    id: str = Field(default_factory=uid_factory)
    cls: str = Field(default='')

    @root_validator(pre=True)
    def set_type(cls, values):
        values['cls'] = '{0}.{1}'.format(cls.__module__, cls.__name__)
        return values

    def marshall(self) -> dict:
        signature = '{0}.{1}'.format(self.__module__, self.__class__.__name__)
        jsoned = self.dict(by_alias=True)
        jsoned['_cls'] = signature
        return jsoned

    @classmethod
    def unmarshall(cls, source: dict):
        ret = cls.parse_obj(source)
        return ret

    @classmethod
    def get_signature(cls) -> str:
        return '{0}.{1}'.format(cls.__module__, cls.__name__)

    def __repr__(self) -> str:
        return json.dumps(self.marshall(), sort_keys=True, indent=4)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        # json_encoders = {ObjectId: str}
