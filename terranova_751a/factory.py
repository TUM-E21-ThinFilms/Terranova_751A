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
from e21_util.log import get_sputter_logger
from e21_util.port.insitu import Ports

from terranova_751a.driver import Terranova751ADriver
from terranova_751a.protocol import Terranova751AProtocol


class Terranova751AFactory:
    def get_logger(self):
        return get_sputter_logger('Terranova 751A', 'terranova_751a.log')

    def create_terranova(self, transport=None, logger=None):
        if logger is None:
            logger = self.get_logger()

        if transport is None:
            transport = Ports().get_transport(Ports.DEVICE_TERRANOVA)

        return Terranova751ADriver(Terranova751AProtocol(transport, logger))
