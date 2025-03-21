from js import Response, Object
from pyodide.ffi import to_js as _to_js

from urllib.parse import urlparse, urlunparse, parse_qs, ParseResult
from typing import Optional

from router import Router
from log import get_logger


# Configure logging

router = Router()
logger = get_logger(__name__)


# to_js converts between Python dictionaries and JavaScript Objects
def to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)


def parse_url(request_url: str) -> tuple[Optional[ParseResult], Optional[dict]]:
    url = urlparse(request_url)
    is_valid_url = bool(url.scheme and url.netloc) or url.path.startswith("/")
    if not is_valid_url:
        logger.debug(f"Invalid URL: {request_url}")
        return None, None
    params = parse_qs(url.query)
    return url, params


def strip_query_params(url: ParseResult) -> str:
    return urlunparse(url._replace(query=""))


def required_env_variables(env) -> bool:
    required_vars = ["GITHUB_ACCOUNT"]
    if any(var not in env.as_object_map() for var in required_vars):
        logger.error(f"Missing required environment variables: {required_vars}")
        return False
    return True


async def on_fetch(request, env):
    logger = get_logger(__name__, env.LOG_LEVEL)
    if not required_env_variables(env):
        return Response.new("", status=500)

    url, params = parse_url(request.url)
    if url is None:
        return Response.new("Invalid URL", status=400)
    request_method = request.method.upper()
    logger.debug(f"Request method: {request_method}")
    logger.debug(f"Request URL: {strip_query_params(url)} with params: {params}")
    handler, params = router.match(request.url, request_method)
    if handler:
        logger.debug(
            f"Handler found for URL: {strip_query_params(url)} with params: {params}"
        )
        response = handler(**params)
        logger.debug(f"Response: {response}")
        return Response.json(to_js(response))
    else:
        logger.debug(f"No handler found for URL: {strip_query_params(url)}")
        return Response.new("Not found", status=404)


@router.route("/")
def get_root():
    logger.debug("Handling get_root")
    return {"action": "get_root"}


@router.route("/{module}/@latest")
def get_latest_module(module: str):
    logger.debug(f"Handling get_latest_module for module: {module}")
    return {"action": "get_latest", "module": module}


@router.route("/{module}/@v/latest")
def get_latest_module_alt(module: str):
    logger.debug(f"Handling get_latest_module_alt for module: {module}")
    return {"action": "get_latest_alt", "module": module}
