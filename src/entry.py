from js import Response, Request, Headers, Object
from pyodide.ffi import to_js as _to_js
from pyodide.ffi import JsProxy

from urllib.parse import urlparse, urlunparse, parse_qs, ParseResult
from typing import Optional, Dict, Any
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
    return Response.json(
        to_js(
            {
                "status": "not found",
            }
        ),
        status=404,
    )


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
    provider = route_request.Env.VERSION_CONTROL_PROVIDER
    provider_account = route_request.Env.PROVIDER_ACCOUNT

    # Prepare template context with all variables needed for rendering
    template_context = {
        "domain": domain,
        "project": project,
        "repository_url": f"https://{provider}.com/{provider_account}/{project}",
    }

    html_content = render_go_import_template(template_context)

    headers = Headers.new({"content-type": "text/html; charset=utf-8"}.items())
    return Response.new(html_content, headers=headers)


def render_go_import_template(context: Dict[str, Any]) -> str:
    """
    Renders the Go import HTML template with the provided context variables.

    Args:
        context (Dict[str, Any]): Dictionary with template variables
            Required keys:
            - domain: Domain name for the import path
            - project: Go project name
            - repository_url: Full URL to the Provider repository

    Returns:
        str: Rendered HTML content for Go module import
    """
    # Build the go-source meta content in parts to avoid exceeding line length
    repo_url = context["repository_url"]
    source_base = f"{context['domain']}/{context['project']} {repo_url}"
    tree_url = f"{repo_url}/tree/master{{/dir}}"
    blob_url = f"{repo_url}/blob/master{{/dir}}/{{file}}#L{{line}}"
    go_source = f"{source_base} {tree_url} {blob_url}"

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="go-import" content="{context['domain']}/{context['project']} git {repo_url}">
    <meta name="go-source" content="{go_source}">
    <title>{context['project']} - Go Module Proxy</title>
</head>
<body>
    <h1>Go Module: {context['project']}</h1>
    <p>This page is part of the Go Module Proxy service.</p>
    <p>Repository: <a href="{repo_url}">{repo_url}</a></p>
    <p>Import with: <code>import "{context['domain']}/{context['project']}"</code></p>
</body>
</html>"""


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
    required_vars = ["VERSION_CONTROL_PROVIDER", "PROVIDER_ACCOUNT"]
    if any(var not in env.as_object_map() for var in required_vars):
        logger.error(f"Missing required environment variables: {required_vars}")
        return False
    return True
