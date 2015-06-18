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

from popc_stats.database import init_db, create_db
from popc_stats.calls import PopcStatConvert, PopcStats
from popc_stats.config import init_config
from pprint import pprint
import argparse

def main(argv):

    parser = argparse.ArgumentParser(description='XiVO stats generator')
    parser.add_argument("-d", "--days", type=int, default=1, help="An integer for the days to generate/view stats")
    parser.add_argument("-v", "--view", action="store_true", help="View stats from db")
    args = parser.parse_args()

    config = init_config()
    db_session = create_db(config)
    init_db()

    if args.view:
        calls = PopcStats()
        pprint(calls.create_stats_from_db_popc(args.days))
    else:
        stats = PopcStatConvert(db_session, config, args.days)
        stats.insert_stats_to_db_popc()
