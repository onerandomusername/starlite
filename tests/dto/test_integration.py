from __future__ import annotations

from typing import Any, List

import pytest

from starlite import Starlite, get, post
from starlite.dto.exc import InvalidAnnotation
from starlite.status_codes import HTTP_201_CREATED
from starlite.testing import create_test_client

from . import ExampleDTO, Model

ScalarDTO = ExampleDTO[Model]
IterableDTO = ExampleDTO[List[Model]]


def test_dto_data() -> None:
    @post(path="/")
    def post_handler(data: ScalarDTO) -> ScalarDTO:
        assert isinstance(data, ExampleDTO)
        assert data.data == Model(a=1, b="two")
        return data

    with create_test_client(route_handlers=[post_handler]) as client:
        post_response = client.post("/", content=b'{"a":1,"b":"two"}')
        assert post_response.status_code == HTTP_201_CREATED
        assert post_response.json() == {"a": 1, "b": "two"}


def test_dto_iterable_data() -> None:
    @post(path="/")
    def post_handler(data: IterableDTO) -> IterableDTO:
        assert isinstance(data, ExampleDTO)
        assert isinstance(data.data, list)
        for item in data.data:
            assert isinstance(item, Model)
        return data

    with create_test_client(route_handlers=[post_handler]) as client:
        post_response = client.post("/", content=b'[{"a":1,"b":"two"},{"a":3,"b":"four"}]')
        assert post_response.status_code == HTTP_201_CREATED
        assert post_response.json() == [{"a": 1, "b": "two"}, {"a": 3, "b": "four"}]


def test_dto_supported_data() -> None:
    @post(path="/", data_dto=ExampleDTO[Model], return_dto=ExampleDTO[Model])
    def post_handler(data: Model) -> Model:
        return data

    with create_test_client(route_handlers=[post_handler]) as client:
        post_response = client.post("/", content=b'{"a":1,"b":"two"}')
        assert post_response.status_code == HTTP_201_CREATED
        assert post_response.json() == {"a": 1, "b": "two"}


def test_dto_supported_iterable_data() -> None:
    @post(path="/", data_dto=ExampleDTO[List[Model]], return_dto=ExampleDTO[List[Model]])
    def post_handler(data: list[Model]) -> list[Model]:
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, Model)
        return data

    with create_test_client(route_handlers=[post_handler]) as client:
        post_response = client.post("/", content=b'[{"a":1,"b":"two"},{"a":3,"b":"four"}]')
        assert post_response.status_code == HTTP_201_CREATED
        assert post_response.json() == [{"a": 1, "b": "two"}, {"a": 3, "b": "four"}]


def test_exception_if_incompatible_data_dto_type() -> None:
    @post(path="/", data_dto=ExampleDTO[Model])
    def post_handler(data: dict[str, Any]) -> None:
        ...

    with pytest.raises(InvalidAnnotation):
        Starlite(route_handlers=[post_handler])


def test_exception_if_incompatible_return_dto_type() -> None:
    @get(return_dto=ExampleDTO[List[Model]])
    def get_handler() -> list[int]:
        return []

    with pytest.raises(InvalidAnnotation):
        Starlite(route_handlers=[get_handler])