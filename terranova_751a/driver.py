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

from terranova_751a.message import GetData, SetData, Message
from terranova_751a.protocol import Terranova751AProtocol
from e21_util.serial_connection import AbstractTransport

class Terranova751ADriver(object):
    UNIT_TORR = 'Torr'
    UNIT_MBAR = 'mBar'
    UNIT_PASCAL = 'Pascal'

    HV_ON = 'On'
    HV_OFF = 'Off'

    STATUS_OFF = '00'
    STATUS_RUNNING = '10'
    STATUS_COOLING = '02'
    STATUS_SHUTDOWN = '03'
    STATUS_INTERLOCK = '04'

    HV_POLARITY_POSITIVE = 'Pos'
    HV_POLARTIY_NEGATIVE = 'Neg'

    def __init__(self, transport, protocol):
        assert isinstance(transport, AbstractTransport)
        assert isinstance(protocol, Terranova751AProtocol)

        self._transport = transport
        self._protocol = protocol

    def _query_message(self, get_data):
        msg = Message(get_data)
        response = self._protocol.query(self._transport, msg)
        if response.is_success():
            return response.get_data()
        raise RuntimeError("Query was not successful")

    def _write_message(self, set_data):
        msg = Message(set_data)
        response = self._protocol.write(self._transport, msg)
        if response.is_success():
            return response.get_data()
        raise RuntimeError("Write was not successful")

    def get_model_number(self):
        return str(self._query_message(GetData('MO')))

    def get_firmware_version(self):
        return float(self._query_message(GetData('VE')))

    def get_current(self):
        # in A
        return float(self._query_message(GetData('CU')))

    def get_pressure(self):
        return float(self._query_message(GetData('PR')))

    def get_voltage(self):
        # in V
        return float(self._query_message(GetData('VO')))

    def get_status(self):
        stat = self._query_message(GetData('ST'))
        if stat in [self.STATUS_RUNNING, self.STATUS_COOLING, self.STATUS_INTERLOCK, self.STATUS_OFF, self.STATUS_SHUTDOWN]:
            return str(stat)

        raise RuntimeError("Received unknown status '%s'" % stat)

    def get_pressure_unit(self):
        unit = self._query_message(GetData('UN'))
        if unit in [self.UNIT_PASCAL, self.UNIT_TORR, self.UNIT_MBAR]:
            return unit

        raise RuntimeError("Received unknown pressure unit '%s'" % unit)

    def get_pump_size(self):
        return float(self._query_message(GetData('PS')))

    def get_hv_polarity(self):
        pol = self._query_message(GetData('PO'))
        if pol in [self.HV_POLARITY_POSITIVE, self.HV_POLARTIY_NEGATIVE]:
            return pol

        raise RuntimeError("Received unknown polarity '%s'" % pol)

    def get_hv(self):
        on_off = self._query_message(GetData('HV'))
        if on_off in [self.HV_OFF, self.HV_ON]:
            return on_off

        raise RuntimeError("Received unknown on/off signal '%s'" % on_off)

    def get_maximum_current(self):
        # in A
        return float(self._query_message(GetData('MC')))

    def get_setpoint(self):
        return float(self._query_message(GetData('SP')))

    def get_maximum_voltage(self):
        # in V
        return float(self._query_message(GetData('MV')))

    def set_pressure_unit(self, unit):
        if not unit in [self.UNIT_MBAR, self.UNIT_PASCAL, self.UNIT_TORR]:
            raise ValueError("Given unit '%s' is unknown" % unit)

        self._write_message(SetData('UN', unit))

    def set_pump_size(self, liters_per_second):
        liters_per_second = float(liters_per_second)
        if liters_per_second >= 1000 or liters_per_second < 0:
            raise ValueError("Given pump size %s is not in range (1000, 0]")

        liters_per_second = "%.1f" % round(liters_per_second, 1)

        self._write_message(SetData('PS', liters_per_second))

    def set_hv(self, on_or_off):
        if not on_or_off in [self.HV_OFF, self.HV_ON]:
            raise ValueError("Given parameter '%s' is unknown" % on_or_off)

        self._write_message(SetData('HV', on_or_off))

    def set_setpoint(self, setpoint):
        setpoint = float(setpoint)
        self._write_message(SetData('SP', "%.1f" % setpoint))

    def set_maximum_voltage(self, voltage):
        voltage = int(voltage)  # voltage in V
        # voltage will be rounded to the nearest 500 Volts
        if voltage > 9999 or voltage < 0:
            raise ValueError("Voltag must be in range (10000, 0)")
        self._write_message(SetData('MV', voltage))

    def set_maxmimum_current(self, current):
        current = int(current)  # current in mA
        if not (0 < current < 25):
            raise ValueError("Current must be in range[1, 25]")

        self._write_message(SetData('MC', current))
