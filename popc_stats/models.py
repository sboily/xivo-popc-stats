from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String
from database import Base


class ModelPopc(Base):

    __tablename__ = 'popc'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    callerid = Column(String(128), nullable=False)
    type = Column(String(128), nullable=False)
    uniqueid = Column(String(128), nullable=False)
    linkedid = Column(String(128), nullable=False)
    queue = Column(String(128))
    callered = Column(String(128))
    origin_uuid = Column(String(128), nullable=False)
    time = Column(String(128), nullable=False)

class CEL(Base):
    __tablename__ = 'cel'

    id = Column(Integer, primary_key=True, nullable=False)
    EventName = Column('eventtype', String(30), nullable=False)
    EventTime = Column('eventtime', DateTime, nullable=False)
    CallerIDnum = Column('cid_num', String(80, convert_unicode=True), nullable=False)
    CallerIDani = Column('cid_ani', String(80), nullable=False)
    Exten = Column('exten', String(80, convert_unicode=True), nullable=False)
    Context = Column('context', String(80), nullable=False)
    Channel = Column('channame', String(80, convert_unicode=True), nullable=False)
    Application = Column('appname', String(80), nullable=False)
    AppData = Column('appdata', String(512), nullable=False)
    UniqueID = Column('uniqueid', String(150), nullable=False)
    LinkedID = Column('linkedid', String(150), nullable=False)

    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])

