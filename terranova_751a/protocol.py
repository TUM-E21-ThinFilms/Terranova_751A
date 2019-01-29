# Copyright (C) 2017, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from e21_util.lock import InterProcessTransportLock
from e21_util.error import CommunicationError
from e21_util.interface import Loggable
from e21_util.serial_connection import AbstractTransport, SerialTimeoutException

from terranova_751a.message import Message, Response, GetData, SetData


class Terranova751AProtocol(Loggable):
    def __init__(self, transport, logger):
        assert isinstance(transport, AbstractTransport)

        super(Terranova751AProtocol, self).__init__(logger)
        self._transport = transport

    def clear(self):
        with InterProcessTransportLock(self._transport):
            self._logger.debug("Clearing message buffer ...")

            try:
                while True:
                    self._transport.read_bytes(32)
            except SerialTimeoutException:
                return

    def get_response(self):
        try:
            return self._transport.read_until("\r")
        except SerialTimeoutException:
            raise CommunicationError("Received a timeout")

    def _do_communicate(self, message):
        with InterProcessTransportLock(self._transport):
            raw_msg = message.get_message()
            self._logger.debug('Sending: %s', repr(raw_msg))
            with self._transport:
                self._transport.write(raw_msg)
                response = self.get_response()
            self._logger.debug('Response: %s', repr(response))
            return Response(response)

    def query(self, message):
        if not isinstance(message, Message):
            raise ValueError("message is not an instance of Message")

        if not isinstance(message.get_data(), GetData):
            raise ValueError("message is not a query-message")

        return self._do_communicate(message)

    def write(self, message):
        if not isinstance(message, Message):
            raise ValueError("message is not an instance of Message")

        if not isinstance(message.get_data(), SetData):
            raise ValueError("message is not a write-message")

        return self._do_communicate(message)
