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
from popc_stats.calls import PopcStatConvert
from popc_stats.config import init_config
import argparse

def main(argv):

    parser = argparse.ArgumentParser(description='XiVO stats generator')
    parser.add_argument("-d", "--days", type=int, help="an integer for the days to generate stats")
    args = parser.parse_args()

    if not args.days:
        args.days = -1

    config = init_config()
    db_session = create_db(config)
    init_db()

    stats = PopcStatConvert(db_session, config, args.days)
    stats.insert_stats_to_db_popc()
