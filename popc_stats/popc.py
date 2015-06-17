#!/usr/local/bin/python

from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy import cast, DATE

from datetime import date

from database import init_db
from calls import follow_calls
from config import init_config
from models import CEL, ModelPopc


db_uri = 'postgresql://asterisk:proformatique@192.168.32.248/asterisk'
engine = create_engine(db_uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

config = init_config()
init_db()

for row in db_session.query(CEL).filter(cast(CEL.EventTime, DATE)==date.today()).order_by(CEL.EventTime):
    data = dict(data=row.to_dict(), origin_uuid=config['origin_uuid'][0])
    follow_calls(data, config)


def generate_stats():
    stats = ModelPopc.query.order_by(ModelPopc.linkedid).all()

    CALLS = {}

    for stat in stats:
        if not CALLS.has_key(stat.linkedid):
            CALLS.update({stat.linkedid : { 'time_incoming': '',
                                            'time_answer': '',
                                            'time_hangup' : '',
                                            'callerid': stat.callerid,
                                            'queue': '',
                                            'type': 'No answer',
                                            'callered': '',
                                            'origin_uuid': stat.origin_uuid,
                                          }
                         })

        if stat.type == 'incoming':
            CALLS[stat.linkedid]['time_incoming'] = stat.time
        if stat.type == 'answer':
            CALLS[stat.linkedid]['time_answer'] = stat.time
            CALLS[stat.linkedid]['type'] = 'Answer'
        if stat.type == 'hangup':
            CALLS[stat.linkedid]['time_hangup'] = stat.time
        if stat.queue:
            CALLS[stat.linkedid]['queue'] = stat.queue
        if stat.callered:
            CALLS[stat.linkedid]['callered'] = stat.callered

    return CALLS

print generate_stats()
