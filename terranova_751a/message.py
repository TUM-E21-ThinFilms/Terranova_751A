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

class Message(object):
    def __init__(self, data):
        if not isinstance(data, Data):
            raise ValueError("data is not an instance of Data")
        self._data = data

    def compute_checksum(self):
        return '00'

    def get_message(self):
        return "".join(['*', self._data.get_data(), ",", self.compute_checksum(), '\r'])

    def get_data(self):
        return self._data

class Data(object):
    def __init__(self, mnemonic):
        if not isinstance(mnemonic, basestring):
            raise ValueError("mnemonic is not a string")

        if not len(mnemonic) == 2:
            raise ValueError("mnemonic must be of length 2")

        self._mnemonic = mnemonic.upper()

    def get_data(self):
        raise NotImplementedError()

class GetData(Data):
    def get_data(self):
        return "".join([self._mnemonic, '?'])

class SetData(Data):
    def __init__(self, mnemonic, value):
        super(SetData, self).__init__(mnmnemonic)
        self._value = str(value)

    def get_data(self):
        return "".join(self._mnemonic, ":", self._value)


class Response(object):
    def __init__(self, raw_response):
        self._suc = ''
        self._data = ''
        self._checksum = ''

        self._parse_raw(raw_response)

    def _parse_raw(self, raw):
        index_colon = raw.find(':')
        index_comma = raw.find(',')
        index_cr = raw.find("\r")

        if index_colon == -1 or index_comma == -1 or index_cr == -1 or index_colon > index_comma:
            raise RuntimeError("Cannot parse string '%s'" % raw)

        self._suc = raw[0:index_colon]
        self._data = raw[index_colon + 1:index_comma]
        self._checksum = raw[index_comma + 1:index_comma + 3]

    def get_success(self):
        return self._suc

    def get_data(self):
        return self._data

    def get_checksum(self):
        return self._checksum

    def is_success(self):
        return self._suc == 'OK'