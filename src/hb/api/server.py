# LIBRARY IMPORTS
import json
import logging
import os

from fastapi import FastAPI
from fastapi.routing import APIRoute
import logging.config
from pydantic import BaseConfig
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from jsonschema import validate

from hb.api import record, learn, common
from hb.api.config import Config, ApiConfig
from hb.clients.mongodb import db_startup, db_shutdown


def custom_generate_unique_id(route: APIRoute):
    '''
    This utility function is used to generate unique ids for every route,
    taking the tags and the route.name to avoid long id descriptions
    :param route:
    :return:
    '''
    if len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    return f"{route.name}"

# Loading the configuration file
config_path = 'conf/server.json'
with open(config_path) as f:
    config_dict = json.load(f)

config: Config = Config.parse_obj(config_dict)
api_config: ApiConfig = config.api

# Setup logging
if not os.path.exists(config.logs_folder):
    os.mkdir(config.logs_folder)
logging_schema_path = 'conf/schemas/python.logging.json'
with open(logging_schema_path) as f:
    logging_schema = json.load(f)

logging_config = config.logging
validate(instance=logging_config, schema=logging_schema)
logging.config.dictConfig(logging_config)
log = logging.getLogger(__name__)

# Initting Fastapi
app: FastAPI = FastAPI(
    title=api_config.title,
    version=api_config.version,
    description=api_config.description,
    servers=config_dict['api']['servers'],
    openapi_tags=config_dict['api']['tags'],
    generate_unique_id_function=custom_generate_unique_id
)

# Binding state configuration
app.state.config = config

# Setting app arbitrary types
BaseConfig.arbitrary_types_allowed = api_config.arbitrary_types_allowed

# Initting CORS Management
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.allow_hosts,
    allow_credentials=api_config.allow_credentials,
    allow_methods=api_config.allow_methods,
    allow_headers=api_config.allow_headers,
)


@app.get("/",tags=['root'])
def read():
    return {'status': 'ok','version':api_config.version}

# Startup handlers
app.add_event_handler("startup", db_startup(app, config.database))

# Shutdown handlers
app.add_event_handler("shutdown", db_shutdown(app))

# Routers
app.include_router(record.router)
app.include_router(learn.router)
app.include_router(common.router)