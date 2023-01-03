from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from spider_proxy.utils.utils_db import engine
Base = declarative_base(engine)


class BaseModel(Base):
    __abstract__ = True

    id = Column(String(50), primary_key=True, nullable=True, server_default=func.gen_random_uuid())
    create_time = Column(TIMESTAMP, nullable=True, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=True, server_default=func.now())
