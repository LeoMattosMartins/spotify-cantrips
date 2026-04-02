from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import Awaitable, Callable

import websockets
from websockets.server import WebSocketServerProtocol


class TelemetryBridge:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._loop: asyncio.AbstractEventLoop | None = None
        self._clients: set[WebSocketServerProtocol] = set()
        self._thread: threading.Thread | None = None

    async def _handler(self, websocket: WebSocketServerProtocol) -> None:
        self._clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._clients.discard(websocket)

    async def _start_server(self) -> None:
        async with websockets.serve(self._handler, self.host, self.port):
            await asyncio.Future()

    def start(self) -> None:
        def runner() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._start_server())

        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()

    async def _broadcast(self, payload: dict) -> None:
        if not self._clients:
            return
        serialized = json.dumps(payload)
        await asyncio.gather(
            *[client.send(serialized) for client in list(self._clients)],
            return_exceptions=True,
        )

    def broadcast(self, payload: dict) -> None:
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(self._broadcast(payload), self._loop)

    def run_on_loop(self, action: Callable[[], Awaitable[None]]) -> None:
        if self._loop:
            asyncio.run_coroutine_threadsafe(action(), self._loop)
