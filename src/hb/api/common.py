import logging
from typing import Union, Optional, Dict

from fastapi import APIRouter, Depends
from starlette.requests import Request

from hb.api import get_database, generic_error
from hb.clients.mongodb import AsyncMongodbClient
from hb.core.serialization import PyObjectId
from hb.models.common import Application, ApplicationScenarios, Applications
from hb.models.record import Scenario

router = APIRouter()

log = logging.getLogger(__name__)


@router.get('/common/models', tags=['common'], response_model=Union[None, Application])
async def models(database: AsyncMongodbClient = Depends(get_database),
                 request: Request = None):
    return None


@router.get('/common/application/load', tags=['common'], response_model=Application)
async def applicationLoad(application: PyObjectId,
                          database: AsyncMongodbClient = Depends(get_database),
                          request: Request = None):
    found = await Application.find(database, {'_id': application})
    if found is None:
        generic_error('Application not found')
    return found


@router.post('/common/application/save', tags=['common'], response_model=str)
async def applicationSave(application: Application,
                          database: AsyncMongodbClient = Depends(get_database),
                          request: Request = None):
    found = await Application.count(database, {'name': application.name})
    if found > 0:
        generic_error('Application already existing with this name')
    ret = await application.insert(database)
    return str(ret)


@router.put('/common/application/update', tags=['common'], response_model=str)
async def applicationUpdate(application: Application,
                            database: AsyncMongodbClient = Depends(get_database),
                            request: Request = None):
    found = await Application.count(database, {'_id': application.id})
    if found == 0:
        generic_error('Application not found')
    ret = await application.replace(database)
    return str(application.id)


@router.delete('/common/application/delete', tags=['common'], response_model=Application)
async def applicationDelete(id: PyObjectId,
                            database: AsyncMongodbClient = Depends(get_database),
                            request: Request = None):
    found = await Application.find(database, {'_id': id})
    if not found:
        generic_error('Application not found')
    await Scenario.delete_many(database, {'application': id})
    await found.delete(database)
    return found


@router.get('/common/application/applications',
            tags=['common'],
            response_model=Applications)
async def applicationList(skip: int = 0,
                          limit: int = 10,
                          filter: Optional[str] = None,
                          sort: Optional[Dict] = None,
                          query: Optional[Dict] = None,
                          database: AsyncMongodbClient = Depends(get_database),
                          request: Request = None):
    qry = query
    if qry is None:
        qry = {}

    if filter is not None:
        qry['$or'] = []
        qry['$or'].append({'name': {'$regex': '.*{0}.*'.format(filter), '$options': 'i'}})
        qry['$or'].append({'description': {'$regex': '.*{0}.*'.format(filter), '$options': 'i'}})

    total = await Application.count(database, qry)
    results = await Application.list(database, qry, skip, limit, sort)
    return Applications(applications=results, total=total)


@router.get('/common/application/scenarios',
            tags=['common'],
            response_model=ApplicationScenarios)
async def applicationScenarios(application: PyObjectId,
                               skip: int = 0,
                               limit: int = 10,
                               filter: Optional[str] = None,
                               sort: Optional[Dict] = None,
                               query: Optional[Dict] = None,
                               database: AsyncMongodbClient = Depends(get_database),
                               request: Request = None):
    found = await Application.find(database, {'_id': application})

    qry = query
    if qry is None:
        qry = {}

    if filter is not None:
        qry['$or'] = []
        qry['$or'].append({'name': {'$regex': '.*{0}.*'.format(filter), '$options': 'i'}})
        qry['$or'].append({'description': {'$regex': '.*{0}.*'.format(filter), '$options': 'i'}})
    if found == 0:
        generic_error('Application not found')
    total = await Scenario.count(database, qry)
    results = await Scenario.list(database, qry, skip, limit, sort)
    return ApplicationScenarios(application=application, total=total, scenarios=results)
