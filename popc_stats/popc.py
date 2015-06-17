#!/usr/bin/env python

from sqlalchemy import create_engine, cast, DATE
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from database import init_db
from calls import follow_calls, generate_stats
from config import init_config
from models import CEL, ModelPopc

config = init_config()
init_db()

engine = create_engine(config['db_uri'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


for row in db_session.query(CEL).filter(cast(CEL.EventTime, DATE)==date.today()).order_by(CEL.EventTime):
    data = dict(data=row.to_dict(), origin_uuid=config['origin_uuid'][0])
    follow_calls(data, config)

calls = generate_stats()

from pprint import pprint
pprint(calls)
