from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(String(32), primary_key=True, nullable=True, server_default=func.sys_guid())
    create_time = Column(TIMESTAMP, nullable=True, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=True, server_default=func.now())
