
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) )
sys.path.insert(1, os.path.abspath(os.path.dirname(__file__)) +"/spider_proxy")

from migrate.versioning import api
from spider_proxy.spider_model.base_model import Base
from spider_proxy.utils.utils_db import engine as db

from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel

if __name__ == '__main__':
    Base.metadata.create_all()
    repo = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db_repository')
    if not os.path.exists(repo):
        api.create(repo, 'db_repository')
        api.version_control(db, repo)

    # migration = repo + '/versions/%03d_migration.py' % (
    #         api.db_version(db, repo) + 1)
    # old_model = api.create_model(db, repo)
    # import types

    # new = types.ModuleType('old_model')
    # exec(old_model, new.__dict__)
    # script = api.make_update_script_for_model(db, repo, new.meta,
    #                                           Base.metadata)
    # print(script)
    # open(migration, 'wt').write(script)
    # api.upgrade(db, repo)

