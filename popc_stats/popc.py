#!/usr/bin/env python

from database import init_db, create_db
from calls import PopcStats, PopcStatConvert
from config import init_config
from pprint import pprint

config = init_config()
db_sessioe = create_db(config)
init_db()

stats = PopcStatConvert(db_session, config)
stats.insert_stats_to_db_popc()

calls = PopcStats()
pprint(calls.create_stats_from_db_popc())

