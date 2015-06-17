from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None

def create_db(config):
    global engine

    engine = create_engine(config['db_uri'], convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))

    Base.query = db_session.query_property()

    return db_session

def init_db():
    Base.metadata.create_all(bind=engine)

