#!/usr/bin/env python


import json
import time
import asyncio
import argparse
import websockets


class Flag:
    """
    Object holding a boolean value and a timestamp.

    Argument:
        init_state (bool): the initial state of the flag
    """
    def __init__(self, init_state=False):
        self.state = init_state
        self.timestamp = time.time()

    def set_state(self, new_state):
        self.state = new_state
        self.timestamp = time.time()


FLAG = Flag()
CONNECTIONS = set()


def process_message(message):
    """
    Get/set flag state and returns a response message.

    Message should be a one of the following dictionaries,
    JSON-encoded:

        {"type": "ask"} (ask for the current state of the flag)
        {"type": "set", "state": True/False} (set/unset the flag)

    Response messages are also JSON-encoded, and can be:

        {"type": "tell", "state": True/False, "timestamp": 123.456}
        {"type": "error"}

    An additional boolean value is return, indicating whether the
    response should be broadcasted to all open websockets.

    Parameter:
        message (str): The JSON-encoded message to process

    Returns:
        response (str), broadcast (bool)
    """

    response = {"type": "error"}
    broadcast = False

    try:
        data = json.loads(message)
    except json.decoder.JSONDecodeError:
        return json.dumps(response), broadcast

    if "type" in data:
        if data["type"] == "set":
            FLAG.set_state(data["state"])
            response["type"] = "tell"
            response["state"] = FLAG.state
            response["timestamp"] = FLAG.timestamp
            broadcast = True

        elif data["type"] == "ask":
            response["type"] = "tell"
            response["state"] = FLAG.state
            response["timestamp"] = FLAG.timestamp

    return json.dumps(response), broadcast


def _make_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, default='0.0.0.0')
    parser.add_argument('port', type=int, default=5000)
    return parser


async def _handler(websocket):
    """Handle websocket connections"""
    CONNECTIONS.add(websocket)
    try:
        async for message in websocket:
            response, broadcast = process_message(message)
            if broadcast:
                websockets.broadcast(CONNECTIONS, response)
            else:
                await websocket.send(response)
    finally:
        CONNECTIONS.remove(websocket)


async def start_server(host, port):
    """
    Start the websocket server.

    Arguments:

        host (str): IP address to bind to
        port (int): port to bind to

    """
    async with websockets.serve(_handler, host, port):
        await asyncio.Future()


if __name__ == "__main__":
    parser = _make_parser()
    args = parser.parse_args()

    print(f"Starting server on {args.host}:{args.port}")
    asyncio.run(start_server(args.host, args.port))
