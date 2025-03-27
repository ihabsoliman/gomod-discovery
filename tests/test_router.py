import pytest
from router import Router
from log import get_logger
import logging


@pytest.fixture
def router():
    return Router()


def test_get_latest_module(router):
    @router.route("/{module}/@latest")
    def get_latest_module(module: str):
        return {"action": "get_latest", "module": module}

    logger = get_logger(__name__, logging.DEBUG)
    logger.debug("Testing get_latest_module")
    handler, params = router.match("http://localhost.com/github.com/user/repo/@latest")
    assert handler is not None
    assert params == {"module": "github.com/user/repo"}
    response = handler(**params)
    assert response == {"action": "get_latest", "module": "github.com/user/repo"}


def test_get_list_versions(router):
    @router.route("/{module}/@v/list")
    def get_list_versions(module: str):
        return {"action": "get_list_versions", "module": module}

    logger = get_logger(__name__, logging.DEBUG)
    logger.debug("Testing get_list_versions")
    handler, params = router.match("http://localhost.com/github.com/user/repo/@v/list")
    assert handler is not None
    assert params == {"module": "github.com/user/repo"}
    response = handler(**params)
    assert response == {"action": "get_list_versions", "module": "github.com/user/repo"}


def test_get_version_info(router):
    @router.route("/{module}/@v/{version}.info")
    def get_version_info(module: str, version: str):
        return {"action": "get_version_info", "module": module, "version": version}

    logger = get_logger(__name__, logging.DEBUG)
    logger.debug("Testing get_version_info")
    handler, params = router.match(
        "http://localhost.com/github.com/user/repo/@v/1.0.2.info"
    )
    assert handler is not None
    assert params == {"module": "github.com/user/repo", "version": "1.0.2"}
    response = handler(**params)
    assert response == {
        "action": "get_version_info",
        "module": "github.com/user/repo",
        "version": "1.0.2",
    }


def test_not_found(router):
    route_match = router.match("/nonexistent/path")
    assert route_match is None
