#!/usr/bin/env python

import time
import json
import pytest
from server import process_message


def send_dict(dictionary):
    response_string, _ = process_message(json.dumps(dictionary))
    return json.loads(response_string)


def test_empty_message():
    response_string, _ = process_message("")
    response = json.loads(response_string)

    assert response["type"] == "error"


def test_not_json():
    response_string, _ = process_message("hello")
    response = json.loads(response_string)

    assert response["type"] == "error"


def test_no_type():
    data = {"state": True}

    response = send_dict(data)

    assert response["type"] == "error"


def test_bad_type():
    data = {"type": "foo"}

    response = send_dict(data)

    assert response["type"] == "error"


def test_ask():
    data = {"type": "ask"}

    response = send_dict(data)

    assert response["type"] == "tell"
    assert isinstance(response["timestamp"], float)
    assert isinstance(response["state"], bool)


def test_set():
    for state in (True, False):
        data = {"type": "set", "state": state}

        response = send_dict(data)

        assert response["type"] == "tell"
        assert response["state"] == state


def test_persistence():
    for state in (True, False):
        data1 = {"type": "set", "state": not state}
        data2 = {"type": "set", "state": state}

        send_dict(data1)
        response = send_dict(data2)

        assert response["type"] == "tell"
        assert response["state"] == state


def test_timestamp():
    data1 = {"type": "set", "state": True}

    send_time = time.time()
    response = send_dict(data1)

    assert response["type"] == "tell"
    assert pytest.approx(response["timestamp"], 0.1) == send_time
