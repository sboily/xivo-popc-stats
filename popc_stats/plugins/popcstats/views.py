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

from flask import Blueprint, jsonify
from popc_stats.calls import PopcStats

popc = Blueprint('popc', __name__, url_prefix='0.1')

@popc.route("/popc")
def index():
    calls = PopcStats()

    return jsonify({'data': calls.create_stats_from_db_popc()})
