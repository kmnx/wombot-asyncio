from .exceptions import AlreadyConnectedError, NotConnectedError, WebSocketClosure

import typing
import asyncio
import aiohttp
import sys
import traceback
import socket
import logging

#logging.basicConfig(filename='connection.log', encoding='utf-8', level=logging.DEBUG)
background_tasks = set()

class Connection:
    def __init__(self, client, ws=True):
        logging.debug('__init__')
        self.client = client
        self._connected = False
        self.type = "ws" if ws else "sock"
        self._connection = None
        self._recv_task = None
        self._ping_task = None
        self._first_command = True
        self._recv = None if not ws else False

    async def sock_connect(
        self,
        user_name: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
    ):
        """
        user_name, password. For the socket client
        """
        logging.debug("sock_connect")
        if self.type == "ws":
            return
        if self.connected:
            raise AlreadyConnectedError(getattr(self, "name", None), self)
        self._recv, self._connection = await asyncio.open_connection(
            f"{self.server}", self.port
        )
        self._connected = True
        self._recv_task = asyncio.create_task(self.s_do_recv())
        background_tasks.add(self._recv_task)
        logging.debug('add_done_callback sock_connect _recv')
        self._recv_task.add_done_callback(background_tasks.discard)
        self._ping_task = asyncio.create_task(self._do_ping())
        background_tasks.add(self._ping_task)
        logging.debug('add_done_callback sock_connect _ping_task')
        self._ping_task.add_done_callback(background_tasks.discard)
        await self._login(user_name, password)

    async def connect(
        self,
        user_name: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
    ):
        logging.debug("connect")
        if self.type == "sock":
            return
        if self.connected:
            raise AlreadyConnectedError(getattr(self, "name", None), self)
        self._first_command = True
        await self._login(u=user_name, p=password)
        self._connected = True
        self._recv_task = asyncio.create_task(self.ws_do_recv())
        background_tasks.add(self._recv_task)
        self._recv_task.add_done_callback(background_tasks.discard)
        logging.debug('add_done_callback connect _recv_task')
        self._ping_task = asyncio.create_task(self._do_ping())
        background_tasks.add(self._ping_task)
        self._ping_task.add_done_callback(background_tasks.discard)
        logging.debug('add_done_callback connect _ping_task')

    @property
    def connected(self):
        return self._connected

    async def cancel(self):
        logging.debug("cancel")
        self._connected = False
        self._recv_task.cancel()
        self._ping_task.cancel()
        if hasattr(self._connection, "is_closing"):
            logging.debug("is_closing")
            self._connection.close()
        else:
            await self._connection.close()

    async def _send_command(self, *args, terminator="\r\n\0"):
        logging.debug("_send_command")
        message = ":".join(args) + terminator
        if self._first_command:
            terminator = "\x00"
            self._first_command = False
        else:
            terminator = "\r\n\0"
        if self.type == "sock":
            self._connection.write(message.encode())
            await self._connection.drain()
        else:
            if not self._connection._closed:
                await self._connection.send_str(message)

    async def _do_ping(self):
        logging.debug("_do_ping")
        await asyncio.sleep(20)
        # ping is an empty message
        await self._send_command("\r\n", terminator="\x00")
        await self.client._call_event("ping", self)
        if self.connected:
            self._ping_task = asyncio.create_task(self._do_ping())
            background_tasks.add(self._ping_task)
            logging.debug('add_done_callback _do_ping ')
            self._ping_task.add_done_callback(background_tasks.discard)

    async def ws_do_recv(self):
        count = 0
        while self.connected:
            try:
                message = await self._connection.receive()
                if message.type is aiohttp.WSMsgType.TEXT:
                    await self._do_process(message.data)
                elif message.type in (
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSE,
                ):
                    raise WebSocketClosure
            except (asyncio.TimeoutError, WebSocketClosure) as error:
                if self._connection.closed:
                    logging.debug("Timeout, _connection.closed")
                    count += 1
                if self.client.debug:
                    logging.debug("Connection reset by host")
                    print(f"[{self.name} :Connection Reset by Host]", error)
                if count > 3:
                    await self.cancel()

    async def s_do_recv(self):
        while self.connected:
            # TODO if the rcv is higher than bytes, may is cutted
            rcv = await self._recv.read(4096)
            await asyncio.sleep(0.0001)
            if rcv:  # si recibe datos.
                data = rcv.decode()
                if data == "\r\n\x00":  # pong
                    await self._do_process("")
                else:
                    recv = data.split("\r\n\x00")  # event
                    for r in recv:
                        if r != "":
                            await self._do_process(r)
            else:
                print(f"Disconnected from {self}")
                logging.debug("Disconnected")
                await self.cancel()
        raise ConnectionAbortedError

    async def _do_process(self, recv):
        """
        Process socket event
        """
        if not recv:
            cmd = "pong"
            args = ""
        else:
            cmd, _, args = recv.partition(":")
            args = args.split(":")
        if hasattr(self, f"_rcmd_{cmd}"):
            try:
                await asyncio.ensure_future(getattr(self, f"_rcmd_{cmd}")(args))
            except (ConnectionResetError, asyncio.exceptions.CancelledError):
                logging.debug("ConnectionResetError")
                self._connected = False
                return
            except:
                logging.debug("Error handling command")
                if __debug__:
                    print("Error while handling command", cmd, file=sys.stderr)

                    traceback.print_exc(file=sys.stderr)
        elif __debug__:
            print("Unhandled received command", cmd, repr(args), file=sys.stderr)
