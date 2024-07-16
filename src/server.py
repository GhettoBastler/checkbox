#!/usr/bin/env python


import argparse
import asyncio
import websockets
import json


connections = set()


class StateFlag:
    def __init__(self, start_state):
        self.state = start_state


state_flag = StateFlag(False)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, default='0.0.0.0')
    parser.add_argument('port', type=int, default=5000)
    return parser


async def handler(websocket):
    connections.add(websocket)
    while True:
        try:
            raw_message = await websocket.recv()
            # Check message
            try:
                message = json.loads(raw_message)
                if not ("state" in message or "ask" in message):
                    # Ignore message
                    print("Message has no \"state\" or \"ask\" field")
                    continue

                if "state" in message:
                    if not isinstance(message["state"], bool):
                        # Ignore message
                        print("State field is not a boolean")
                        continue

                    state_flag.state = message["state"]

                elif "ask" in message:
                    # Telling the state
                    response = json.dumps({"state": state_flag.state})
                    await websocket.send(response)
                    continue

            except json.decoder.JSONDecodeError:
                # Ignore message
                print("Message is malformed")
                continue

            # Broadcast
            broadcast_message = json.dumps({"state": state_flag.state})

            for conn in connections:
                await conn.send(broadcast_message)

        except Exception as e:
            print(e)
            connections.remove(websocket)
            break


async def main(host, port):
    async with websockets.serve(handler, host, port):
        await asyncio.Future()


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    print(f"Starting server on {args.host}:{args.port}")
    asyncio.run(main(args.host, args.port))
