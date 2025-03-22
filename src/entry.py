from js import Response, Request, Headers, Object
from pyodide.ffi import to_js as _to_js
from pyodide.ffi import JsProxy

from urllib.parse import urlparse, urlunparse, parse_qs, ParseResult
from typing import Optional
from dataclasses import dataclass

from router import Router
from log import get_logger


@dataclass
class RouteRequest:
    Url: ParseResult
    QueryParams: dict
    Method: str
    Request: Request
    Env: JsProxy


# Configure logging

router = Router()
logger = get_logger(__name__)


# Cloudflare worker entry point
async def on_fetch(request, env):
    logger = get_logger(__name__, env.LOG_LEVEL)
    if not required_env_variables(env):
        return Response.new("", status=500)

    url, qs = parse_url(request.url)
    if url is None:
        return Response.new("Invalid URL", status=400)
    request_method = request.method.upper()
    route_request = RouteRequest(
        Url=url, QueryParams=qs or {}, Method=request_method, Request=request, Env=env
    )
    logger.debug(f"Request method: {request_method}")
    logger.debug(f"Request URL: {strip_query_params(url)} with qs: {qs}")
    handler, params = router.match(request.url, request_method)

    if handler:
        logger.debug(
            f"Handler found for URL: {strip_query_params(url)} with params: {params}"
        )
        return handler(route_request, **params)
    else:
        logger.debug(f"No handler found for URL: {strip_query_params(url)}")
        return Response.new("Not found", status=404)


@router.route("/")
def handle_root(route_request: RouteRequest):
    logger.debug("Handling handle_root")
    return {"action": "handle_root"}


@router.route("/{site}/{owner}/{project}")
def handle_module(route_request: RouteRequest, site: str, owner: str, project: str):
    logger.debug("Handling handle_module")
    if ("go-get" not in route_request.QueryParams) or (
        route_request.QueryParams["go-get"][0] != "1"
    ):
        return Response.json(
            to_js(
                {
                    "action": "handle_module",
                    "site": site,
                    "owner": owner,
                    "project": project,
                }
            ),
            status=404,
        )

    domain = route_request.Url.netloc
    github_account = route_request.Env.GITHUB_ACCOUNT

    headers = Headers.new({"content-type": "text/html; charset=utf-8"}.items())
    return Response.new(
        f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="go-import" content="{domain}/{project} git https://github.com/{github_account}/{project}">
<meta name="go-source" content="{domain}/{project} https://github.com/{github_account}/{project} https://github.com/{github_account}/{project}/tree/master{{/dir}} https://github.com/{github_account}/{project}/blob/master{{/dir}}/{{file}}#L{{line}} ">
<title>{project}</title>
</head>

<body>
<a href=\"https://{domain}\">https://{domain}</a>
</body>
</html>
        """,
        headers=headers,
    )


#########
# The following functions are helper functions
#########


def to_js(obj):
    """
    Converts a Python dictionary to a JavaScript object.
    Args:
        obj (dict): The Python dictionary to convert.
    Returns:
        js.Object: The converted JavaScript object.
    """
    return _to_js(obj, dict_converter=Object.fromEntries)


def parse_url(request_url: str) -> tuple[Optional[ParseResult], Optional[dict]]:
    """
    Parses the request URL and returns a tuple of the parsed URL and query parameters.
    Args:
        request_url (str): The URL to parse.
    Returns:
        tuple: A tuple containing the parsed URL and query parameters.
    """
    url = urlparse(request_url)
    is_valid_url = bool(url.scheme and url.netloc) or url.path.startswith("/")
    if not is_valid_url:
        logger.debug(f"Invalid URL: {request_url}")
        return None, None
    params = parse_qs(url.query)
    return url, params


def strip_query_params(url: ParseResult) -> str:
    """
    Strips the query parameters from the URL.
    Args:
        url (ParseResult): The parsed URL.
    Returns:
        str: The URL without query parameters, empty string if url is None.
    """
    if not url:
        return ""
    return urlunparse(url._replace(query=""))


def required_env_variables(env) -> bool:
    """
    Checks if the required environment variables are set.
    Args:
        env: The environment object.
    Returns:
        bool: True if all required environment variables are set, False otherwise.
    """
    required_vars = ["GITHUB_ACCOUNT"]
    if any(var not in env.as_object_map() for var in required_vars):
        logger.error(f"Missing required environment variables: {required_vars}")
        return False
    return True
