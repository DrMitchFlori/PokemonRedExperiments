"""WebSocket broadcast wrapper for Gym environments.

``StreamWrapper`` decorates an environment to send the player's in-game
coordinates to ``wss://transdimensional.xyz/broadcast``. This enables live
visualization of training progress on the shared online map. Wrap your Gym
environment with this class prior to training.
"""

import asyncio
import websockets
import json
import logging

import gymnasium as gym

X_POS_ADDRESS, Y_POS_ADDRESS = 0xD362, 0xD361
MAP_N_ADDRESS = 0xD35E

class StreamWrapper(gym.Wrapper):
    """Gym wrapper for broadcasting coordinate data via WebSocket.

    The ``stream_step_counter`` attribute tracks how many environment
    steps have occurred since the last broadcast so that updates are sent
    periodically.
    """

    def __init__(self, env, stream_metadata={}):
        super().__init__(env)
        self.ws_address = "wss://transdimensional.xyz/broadcast"
        self.stream_metadata = stream_metadata
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.websocket = None
        self.loop.run_until_complete(
            self.establish_wc_connection()
        )
        self.upload_interval = 300
        self.stream_step_counter = 0
        self.env = env
        self.coord_list = []
        if hasattr(env, "pyboy"):
            self.emulator = env.pyboy
        elif hasattr(env, "game"):
            self.emulator = env.game
        else:
            raise Exception("Could not find emulator!")

    def step(self, action):

        x_pos = self.emulator.get_memory_value(X_POS_ADDRESS)
        y_pos = self.emulator.get_memory_value(Y_POS_ADDRESS)
        map_n = self.emulator.get_memory_value(MAP_N_ADDRESS)
        self.coord_list.append([x_pos, y_pos, map_n])

        if self.stream_step_counter >= self.upload_interval:
            self.stream_metadata["extra"] = f"coords: {len(self.env.seen_coords)}"
            self.loop.run_until_complete(
                self.broadcast_ws_message(
                    json.dumps(
                        {
                          "metadata": self.stream_metadata,
                          "coords": self.coord_list
                        }
                    )
                )
            )
            self.stream_step_counter = 0
            self.coord_list = []

        self.stream_step_counter += 1

        return self.env.step(action)

    async def broadcast_ws_message(self, message):
        if self.websocket is None:
            await self.establish_wc_connection()
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except websockets.exceptions.WebSocketException as e:
                self.websocket = None

    async def establish_wc_connection(self):
        try:
            self.websocket = await websockets.connect(self.ws_address)
        except Exception as e:
            logging.warning(
                "Failed to establish websocket connection to %s: %s",
                self.ws_address,
                e,
            )
            self.websocket = None

    def close(self):
        """Close WebSocket connection and underlying environment."""
        if self.websocket is not None:
            try:
                self.loop.run_until_complete(self.websocket.close())
            except Exception as e:  # pragma: no cover - best effort
                logging.warning("Error closing websocket: %s", e)
            finally:
                self.websocket = None

        if not self.loop.is_closed():
            self.loop.close()

        super().close()
