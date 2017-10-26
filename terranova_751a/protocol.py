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

from slave.protocol import Protocol
from slave.transport import Timeout
from message import Message, Response, GetData, SetData


class Terranova751AProtocol(Loggable):
    def __init__(self, logger):
        super(Terranova751AProtocol, self).__init__(logger)

    def clear(self, transport):
        with InterProcessTransportLock(transport):
            self._logger.debug("Clearing message buffer ...")

            try:
                while True:
                    transport.read_bytes(32)
            except Timeout:
                return

    def get_response(self, transport):
        try:
            return transport.read_until("\r") + "\r"
        except slave.transport.Timeout:
            raise CommunicationError("Received a timeout")

    def _do_communicate(self, transport, message):
        with InterProcessTransportLock(transport):
            raw_msg = message.get_message()
            self._logger.debug('Sending: %s', repr(raw_msg))
            with transport:
                transport.write(raw_msg)
                response = self.get_response(transport)
            self._logger.debug('Response: %s', repr(response))
            return Response(response)

    def query(self, transport, message):
        if not isinstance(message, Message):
            raise ValueError("message is not an instance of Message")

        if not isinstance(message.get_data(), GetData):
            raise ValueError("message is not a query-message")

        return self._do_communicate(transport, message)

    def write(self, transport, message):
        if not isinstance(message, Message):
            raise ValueError("message is not an instance of Message")

        if not isinstance(message.get_data(), SetData):
            raise ValueError("message is not a write-message")

        return self._do_communicate(transport, message)
