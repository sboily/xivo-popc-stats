# -*- coding: utf-8 -*-

# Copyright (C) 2015 Sylvain Boily
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_confd import BasePlugin
from database import create_db
from calls import PopcStats
from config import init_config
from views import popc
from pprint import pprint

class XiVOPopcStats(BasePlugin):
    def load(self, app, config):
        config_popc = init_config()
        db_session = create_db(config_popc)

        app.register_blueprint(popc)

        calls = PopcStats()
        pprint(calls.create_stats_from_db_popc())
