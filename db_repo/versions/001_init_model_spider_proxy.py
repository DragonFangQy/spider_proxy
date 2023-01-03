from sqlalchemy import MetaData
from migrate import *
from migrate.versioning import api
from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel

meta = MetaData()
def upgrade(migrate_engine):
    # meta.bind = migrate_engine
    SpiderProxyModel.metadata.create_all()
    
def downgrade(migrate_engine):
    # meta.bind = migrate_engine
    SpiderProxyModel.metadata.drop_all()
    

