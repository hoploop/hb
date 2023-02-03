"""
Synchronous MongoDB Client
"""
# Python Imports
import logging
import ssl
from dataclasses import dataclass

# Custom Imports
from io import StringIO
from typing import Tuple, List

from motor.motor_asyncio import AsyncIOMotorClientEncryption
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from motor.motor_asyncio import AsyncIOMotorClient
import gridfs
import pymongo
from fastapi import FastAPI
from pymongo.encryption import ClientEncryption, Algorithm
from bson import ObjectId, CodecOptions

import certifi

from hb.api.config import DatabaseConfig

log = logging.getLogger(__name__)


@dataclass
class EncryptionConfig:
    salt: str
    namespace: str


@dataclass
class MongoConfig:
    uri: str
    name: str
    encryption: EncryptionConfig


class AsyncMongodbClient:

    def __init__(self, config: MongoConfig):
        self.driver: AsyncIOMotorClient = AsyncIOMotorClient(config.uri, ssl=True)#, ssl_cert_reqs=ssl.CERT_NONE)
        self.client = self.driver[config.name]
        local_master_key = config.encryption.salt.encode()  # os.urandom(96) #byte[]
        kms_providers = {"local": {"key": local_master_key}}
        self.key_vault_namespace = config.encryption.namespace
        key_vault_client = self.driver

        self.encryption = AsyncIOMotorClientEncryption(
            kms_providers,
            self.key_vault_namespace,
            key_vault_client,
            CodecOptions())

        self.buckets = {}

    async def open(self):
        await self.client.drop_collection(self.key_vault_namespace)
        self.encryption_data_key_id = await self.encryption.create_data_key('local', key_alt_names=['encryption'])

    async def server_info(self) -> dict:
        return await self.driver.server_info()



    def bucket(self, name):
        if name in self.buckets:
            return self.buckets[name]
        else:
            self.buckets[name] = AsyncIOMotorGridFSBucket(self.client, bucket_name=name)
            return self.buckets[name]

    async def insert_one(self, klass, data: dict) -> ObjectId:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = await self.client[self.normalize_collection(collection)].insert_one(data)
        return result.inserted_id

    async def upload_file(self,
                          bucket_name: str,
                          filename: str,
                          data: bytes,
                          content_type: str = 'text/plain') -> ObjectId:
        grid_in = self.bucket(bucket_name).open_upload_stream(filename, metadata={"contentType": content_type})
        await grid_in.write(data)
        await grid_in.close()  # uploaded on close
        return grid_in._id

    async def download_file(self, bucket_name: str, file_id: ObjectId) -> bytes:
        grid_out = await self.bucket(bucket_name).open_download_stream(file_id)
        contents = await grid_out.read()
        return contents

    async def download_file_by_name(self, bucket_name: str, filename: str) -> bytes:
        grid_out = await self.bucket(bucket_name).open_download_stream_by_name(filename)
        contents = await grid_out.read()
        return contents

    async def delete_file(self, bucket_name: str, file_id):
        result = await self.bucket(bucket_name).delete(file_id)

    async def list_files(self, bucket_name: str, query: dict = {}) -> List[bytes]:
        cursor = await self.bucket(bucket_name).find(query, no_cursor_timeout=True)
        ret = []
        async for grid_data in cursor:
            data = await grid_data.read()
            ret.append(data)
        return ret

    async def replace_one(self, klass, query: dict, data: dict) -> Tuple[int, int]:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = await self.client[self.normalize_collection(collection)].replace_one(query, data)
        return result.matched_count, result.modified_count

    async def update_many(self, klass, query: dict, action: dict) -> Tuple[int, int]:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = await self.client[self.normalize_collection(collection)].update_many(query,
                                                                                      action)  # {'x': 1}, {'$inc': {'x': 3}})
        return result.matched_count, result.modified_count


    async def index_field(self, klass,field:str,background=True):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        await self.client[self.normalize_collection(collection)].create_index(field,background=background)



    async def update_one(self, klass, query: dict, statement: dict) -> Tuple[int, int]:
        """
        Updates a document specified by query, by statement
        :param collection: The name of the collection to update the document in
        :param query: The dict representing the mongodb query
        :param statement: The dict representing the mongodb document or update statement
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = await self.client[self.normalize_collection(collection)].update_one(query, statement)
        return result.matched_count, result.modified_count

    async def delete_one(self, klass, query: dict) -> int:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        return await self.client[self.normalize_collection(collection)].delete_one(query)

    async def delete_many(self, klass, query: dict) -> int:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = await self.client[self.normalize_collection(collection)].delete_many(query)
        return result.deleted_count

    async def count(self, klass, query: dict) -> int:
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        return await self.client[self.normalize_collection(collection)].count_documents(query)

    async def find_one(self, klass, query: dict):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        return await self.client[self.normalize_collection(collection)].find_one(query)

    async def distinct(self, klass, query: dict, key: str):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        cursor = self.client[self.normalize_collection(collection)].find(query)
        return await cursor.distinct(key)

    async def find_many(self,
                        klass,
                        query: dict = {},
                        skip: int = None,
                        limit: int = None,
                        sort: dict = None,
                        distinct: str = None):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        res = self.client[self.normalize_collection(collection)].find(query)

        if sort is not None and len(list(sort.keys())) > 0:
            sorting = []
            for key in sort:
                if sort[key] == 1:
                    sorting.append([key, pymongo.ASCENDING])
                else:
                    sorting.append([key, pymongo.DESCENDING])
            res = res.sort(sorting)
        if skip is not None:
            res = res.skip(skip)
        if limit is not None:
            res = res.limit(limit)
        if distinct is not None:
            res = res.distinct(distinct)

        return await res.to_list(length=None)

    async def aggregate(self,
                        klass,
                        pipeline):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        ret = await self.client[self.normalize_collection(collection)].aggregate(pipeline).to_list(length=None)
        return ret

    def normalize_collection(self, collection: str):
        if 'system' in collection:
            return collection.replace('system', 'sys')
        return collection

    async def close(self):
        await self.encryption.close()
        self.driver.close()

    async def encrypt(self, value: str):
        return await self.encryption.encrypt(value,
                                             key_id=self.encryption_data_key_id,
                                             algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random)

    async def decrypt(self, encrypted: str):
        return await self.encryption.decrypt(encrypted)


class MongodbClient:
    """
    MongoDB Client Synchronous based on PyMongo
    """

    def __init__(self, config: MongoConfig):
        log.info('Connecting to MongoDb: %s' % (config.uri,))
        self.client = pymongo.MongoClient(config.uri, ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client[config.name]
        self.buckets = {}
        local_master_key = config.encryption.salt.encode()  # os.urandom(96) #byte[]
        kms_providers = {"local": {"key": local_master_key}}
        key_vault_namespace = config.encryption.namespace
        key_vault_client = self.client
        self.encryption = ClientEncryption(kms_providers, key_vault_namespace, key_vault_client, CodecOptions())
        self.encryption_data_key_id = self.encryption.create_data_key('local', key_alt_names=['encryption'])

    def insert_one(self, klass, document: dict) -> ObjectId:
        """
        Insert a new document inside mongodb collection
        :param collection: The name of the collection to insert the element in (string)
        :param document: The dict element to be inserted, (python dict)
        :return: the Python dict representing the inserted doc
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        return self.db[self.normalize_collection(collection)].insert(document)

    def update_one(self, klass, query: dict, statement: dict) -> int:
        """
        Updates a document specified by query, by statement
        :param collection: The name of the collection to update the document in
        :param query: The dict representing the mongodb query
        :param statement: The dict representing the mongodb document or update statement
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = self.db[self.normalize_collection(collection)].update_one(query, statement)
        return result.modified_count

    def update_many(self, klass, query: dict, statement: dict) -> int:
        """
        Updates a document specified by query, by statement
        :param collection: The name of the collection to update the document in
        :param query: The dict representing the mongodb query
        :param statement: The dict representing the mongodb document or update statement
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        result = self.db[self.normalize_collection(collection)].update_many(query, statement)
        return result.modified_count

    def delete_one(self, klass, query: dict) -> None:
        """
        Removes by searching a set of documents
        :param collection: The name of the collection to delete the document from
        :param query: a python dict containing a MongoDb Query Language
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        self.db[self.normalize_collection(collection)].delete_one(query)

    def delete_many(self, klass, query: dict) -> None:
        """
        Removes by searching a set of documents
        :param collection: The name of the collection to delete the document from
        :param query: a python dict containing a MongoDb Query Language
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        log.debug("Deleting document: " + str(query) + " | " + str(collection))
        self.db[self.normalize_collection(collection)].delete_many(query)

    def count_many(self, klass, query: dict = None) -> int:
        """
        Returns a reader of documents, specified by query
        :param collection: The name of the collection to search the document
        :param query: a python dict containing a MongoDb Query Language
        :return: A python number containing the size reader of found document
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        total = self.db[self.normalize_collection(collection)].count(query)
        return total

    def find_one(self, klass, query: dict = None) -> dict:
        """
        Returns a document, specified by query
        :param collection: The name of the collection to search the document
        :param query: a python dict containing a MongoDb Query Language
        :return: A python dict containing the found document
        """
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        return self.db[self.normalize_collection(collection)].find_one(query)

    def exist_one(self, collection: str, query: dict) -> bool:
        """
        Check if a document exists in the mongodb collection
        :param collection: The name of the collection to search the document
        :param query: a python dict containing a MongoDb Query Language
        :return: True if document exists
        """
        if self.db[self.normalize_collection(collection)].find_one(query) is not None:
            return True
        return False

    def insert_file(self, collection: str, filename: str, fb: StringIO) -> ObjectId:
        bucket = self.gridfs_bucket(self.normalize_collection(collection))
        grid_in = bucket.open_upload_stream(filename)
        grid_in.write(fb.read().encode("UTF-8"))
        grid_in.close()
        return grid_in._id

    def rename_file(self, collection: str, id: ObjectId, filename: str):
        bucket = self.gridfs_bucket(self.normalize_collection(collection))
        bucket.rename(id, filename)

    def delete_file_by_id(self, collection: str, id):
        bucket = self.gridfs_bucket(self.normalize_collection(collection))
        bucket.delete(ObjectId(id))

    def read_file_by_name(self, collection: str, filename: str):
        bucket = self.gridfs_bucket(self.normalize_collection(collection))
        grid_out = bucket.open_download_stream_by_name(filename)
        data = grid_out.read()
        return data

    def read_file_by_id(self, collection: str, id: ObjectId):
        bucket = self.gridfs_bucket(self.normalize_collection(collection))
        grid_out = bucket.open_download_stream(id)
        data = grid_out.read()
        return data

    def gridfs_bucket(self, name):
        if name in self.buckets:
            return self.buckets[name]
        else:
            self.buckets[name] = gridfs.GridFSBucket(self.db, bucket_name=name)
            return self.buckets[name]

    def index_collection(self, collection: str, field: str):
        """
        Force / ensure the indexing of a collection by a specified field name
        :param collection: The name of the collection to be indexed
        :param field: The name of the document field to be the ensured index
        """
        log.debug("Indexing: " + str(field) + " | " + str(collection))
        self.db[self.normalize_collection(collection)].ensure_index(field)

    def drop_collection(self, collection: str = None):
        """
        Fully removes a collection in the current mongodb database
        :param collection: The name of the collection
        """
        log.debug("Dropping collection: " + str(collection))
        self.db.drop_collection(collection)

    def list_many(self, klass, query: dict, skip: int = None, limit: int = None, sort: dict = None,
                  distinct: str = None):
        collection = '{0}.{1}'.format(klass.__module__, klass.__name__)
        res = self.db[self.normalize_collection(collection)].find(query)
        if skip is not None:
            res = res.skip(skip)
        if limit is not None:
            res = res.limit(limit)
        if sort is not None and len(list(sort.keys())) > 0:
            sorting = []
            for key in sort:
                if sort[key] == 1:
                    sorting.append([key, pymongo.ASCENDING])
                else:
                    sorting.append([key, pymongo.DESCENDING])
            res = res.sort(sorting)
        if distinct:
            res = res.distinct(distinct)
        return res

    def normalize_collection(self, collection: str):
        if 'system' in collection:
            return collection.replace('system', 'sys')
        return collection

    def server_info(self) -> dict:
        return self.client.server_info()

    def encrypt(self, value: str):
        return self.encryption.encrypt(value, key_id=self.encryption_data_key_id,
                                       algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random)

    def decrypt(self, encrypted: str):
        return self.encryption.decrypt(encrypted)

    def close(self):
        self.client.close()


def db_startup(app: FastAPI, db_config: DatabaseConfig):
    async def start_app() -> None:
        log.info('Connecting to mongodb: {0}'.format(db_config.uri))
        app.state.database: AsyncMongodbClient = AsyncMongodbClient(MongoConfig(uri=db_config.uri,
                                                                                name=db_config.name,
                                                                                encryption=EncryptionConfig(
                                                                                    salt=db_config.encryption.salt,
                                                                                    namespace=db_config.encryption.namespace)))

        info = await app.state.database.server_info()
        await app.state.database.open()
        log.info(str(info))

    return start_app


def db_shutdown(app: FastAPI):
    async def stop_app() -> None:
        log.info('Disconnecting from mongodb')
        await app.state.database.close()

    return stop_app
