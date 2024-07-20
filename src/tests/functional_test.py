#! /usr/bin/env python


import json
from websockets.sync.client import connect


URI = "ws://localhost:5000"


def alice_iter():
    # Alice access the webpage. Their browner connects to the
    # websocket server and sends an "ask" message

    print("Alice: Connecting to server")
    alice_websocket = connect(URI)
    print("A->S: Asking for flag state")
    ask_message = {"type": "ask"}
    alice_websocket.send(json.dumps(ask_message))

    # The websocket server responds with the current state

    response = alice_websocket.recv()
    response_data = json.loads(response)

    assert response_data["type"] == "tell"
    assert isinstance(response_data["state"], bool)

    print("S->A: Flag state is", response_data["state"])

    # Alice toggles the checkbox. The browser sends a "set" message

    print("A->S: Setting flag to True")
    set_message = {"type": "set", "state": True}
    alice_websocket.send(json.dumps(set_message))

    # Waiting for Bob to do their thing
    yield

    # Alice's browser recieves a "tell" message from the server

    response = alice_websocket.recv()
    response_data = json.loads(response)

    assert response_data["type"] == "tell"
    assert response_data["state"] is True

    print("S->A: Flag state is", response_data["state"])

    # Alice sees Bob's modification in real time

    response = alice_websocket.recv()
    response_data = json.loads(response)

    assert response_data["type"] == "tell"
    assert response_data["state"] is False

    print("S->A: Flag state is", response_data["state"])

    # Alice closes their browser
    print("Alice: Closing connection")
    alice_websocket.close()
    yield


def bob_iter():
    # Bob access the webpage. Their browner connects to the
    # websocket server and sends an "ask" message

    print("Bob: Connecting to server")
    bob_websocket = connect(URI)
    print("B->S: Asking for flag state")
    ask_message = {"type": "ask"}
    bob_websocket.send(json.dumps(ask_message))

    # The bob_websocket server responds with the current state,
    # which is "True" because Alice just toggled the checkbox

    response = bob_websocket.recv()
    response_data = json.loads(response)

    assert response_data["type"] == "tell"
    assert response_data["state"] is True

    print("S->B: Flag state is", response_data["state"])

    # Bob toggles the checkbox. The browser sends a "set" message

    print("B->S: Setting flag to False")

    set_message = {"type": "set", "state": False}
    bob_websocket.send(json.dumps(set_message))

    # Bob browser recieves a "tell" message from the server

    response = bob_websocket.recv()
    response_data = json.loads(response)

    response_data["type"] == "tell"
    response_data["state"] is False

    print("S->B: Flag state is", response_data["state"])

    # Bob closes their browser
    print("Bob: Closing connection")
    bob_websocket.close()

    yield


def run_test():
    alice = alice_iter()
    bob = bob_iter()

    print("Starting test")
    next(alice)
    next(bob)
    next(alice)
    print("Test end")


if __name__ == "__main__":
    run_test()
