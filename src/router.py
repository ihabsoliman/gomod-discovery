import re
from urllib.parse import urlparse
from typing import Callable, Dict, List, Optional, Pattern, NamedTuple
from log import get_logger

# Configure logging
logger = get_logger(__name__)


class Route(NamedTuple):
    """
    Represents a route with its regex pattern, HTTP method, handler function,
    and parameter names.
    """

    regex: Pattern[str]
    method: str
    func: Callable
    param_names: List[str]


class RouteMatch(NamedTuple):
    """
    Represents a successful route match with the handler function and parameters.
    """

    func: Callable
    params: Dict[str, str]


class Router:
    def __init__(self) -> None:
        self.routes: List[Route] = []

    def route(self, pattern: str, method: str = "GET") -> Callable:
        """
        Decorator to register a route with a specific pattern and method.
        The pattern can contain placeholders in the format {placeholder}.
        """

        param_names = []
        regex_parts = []

        for part in pattern.split("/"):
            if not part:
                regex_parts.append(r"")
                continue

            placeholders = re.findall(r"{([^}]+)}", part)

            if placeholders:
                regex_part = part

                for placeholder in placeholders:
                    param_names.append(placeholder)
                    regex_part = regex_part.replace(f"{{{placeholder}}}", r"(.*)")

                regex_parts.append(regex_part)
            else:
                regex_parts.append(re.escape(part))

        regex_pattern = "/".join(regex_parts) + r"$"
        logger.debug(
            f"Generated regex pattern: {regex_pattern} with params: {param_names}"
        )
        compiled_regex = re.compile(regex_pattern)
        logger.debug(f"Compiled regex: {compiled_regex}")
        logger.debug(f"Registered route: {pattern} with regex: {regex_pattern}")

        def decorator(func: Callable) -> Callable:
            route = Route(compiled_regex, method.upper(), func, param_names)
            self.routes.append(route)
            return func

        return decorator

    def match(self, url: str, request_method: str = "GET") -> Optional[RouteMatch]:
        parsed_url = urlparse(url)
        path = parsed_url.path
        logger.debug(f"Matching URL: {url} with path: {path}")
        logger.debug(f"Routes: {self.routes}")
        for regex, method, func, param_names in self.routes:
            match = regex.match(path)
            logger.debug(f"Trying regex: {regex} on path: {path}")
            if match:
                if method != request_method:
                    logger.debug(
                        f"Method mismatch: {method} != {request_method}, skipping route."
                    )
                    continue
                params = {
                    name: match.group(i + 1) for i, name in enumerate(param_names)
                }
                logger.debug(
                    f"Match found: {func.__name__} {method} with params: {params}"
                )
                return RouteMatch(func, params)

        logger.warning(f"No match found for URL: {url}")
        return None
