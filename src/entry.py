from js import Response, Object
from pyodide.ffi import to_js as _to_js

from router import Router
from log import get_logger


# Configure logging

router = Router()
logger = get_logger(__name__)


# to_js converts between Python dictionaries and JavaScript Objects
def to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)


async def on_fetch(request, env):
    logger = get_logger(__name__, env.LOG_LEVEL)
    logger.debug(f"Received request: {request.url}")
    handler, params = router.match(request.url)
    if handler:
        logger.debug(f"Handler found for URL: {request.url} with params: {params}")
        response = handler(**params)
        logger.debug(f"Response: {response}")
        return Response.json(to_js(response))
    else:
        logger.debug(f"No handler found for URL: {request.url}")
        return Response.new("Not found", status=404)


@router.get("/")
def get_root():
    logger.debug("Handling get_root")
    return {"action": "get_root"}


@router.get("/{module}/@latest")
def get_latest_module(module: str):
    logger.debug(f"Handling get_latest_module for module: {module}")
    return {"action": "get_latest", "module": module}


@router.get("/{module}/@v/latest")
def get_latest_module_alt(module: str):
    logger.debug(f"Handling get_latest_module_alt for module: {module}")
    return {"action": "get_latest_alt", "module": module}
