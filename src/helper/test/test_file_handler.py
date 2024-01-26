"""This File contains tests for the FileHandler class."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
import datetime
import json
import os

import pytest
from src.test_base.cleanup_data_fixture import cleanup_data
from src.helper.file_handler import FileHandler

FILE_HANDLER = FileHandler()
TEST_FILE_PATH = os.getcwd() + "/src/helper/test/test.json"
TEST_FILE_DATA = {"test": "test"}


@pytest.fixture(autouse=True)
def setup_and_teardown_file():
    """Creates a test file and deletes it after the test."""
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(TEST_FILE_DATA, f)
    yield
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


def test_read_json_success(setup_and_teardown_file):
    """Tests reading a JSON file that exists."""
    data = FILE_HANDLER.read_json(TEST_FILE_PATH)
    assert data == TEST_FILE_DATA


def test_read_json_fail():
    """Tests reading a JSON file that does not exist."""
    data = FILE_HANDLER.read_json("does/not/exist.json")
    assert data is None


def test_write_json_success(setup_and_teardown_file):
    """Tests writing a JSON file by writing the current time."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json(TEST_FILE_PATH, data)
    assert success is True
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) == data


def test_write_json_fail():
    """Tests writing a non existing JSON file by writing the current time."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json("does/not/exist.json", data)
    assert success is False


def test_delete_file():
    """Tests deleting a file."""
    # create a file first
    data = {"test": "test"}
    FILE_HANDLER.create(TEST_FILE_PATH, data)
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) == data
    # delete the file
    success = FILE_HANDLER.delete(TEST_FILE_PATH)
    assert success is True
    # check if the file still exists
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) is None
