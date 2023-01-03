from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spider_proxy.spider_common.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

def open_session():
    # 创建session
    session_connect = sessionmaker(bind=engine)
    db_session = session_connect()
    return db_session


def commit_session(db_session, commit_num=1):
    print("commit_num: %s, len(db_session.new): %s" % (commit_num, len(db_session.new)))
    if not commit_num or len(db_session.new) < commit_num:
        return

    if db_session:
        db_session.flush()
        db_session.commit()
    else:
        raise ValueError("db_session IS None")


def close_session(db_session):

    try:
        # 关闭前提交事务
        commit_session(db_session)
    except ValueError as ve:
        # 如果 db_session is none，认为已关闭，不抛出异常
        pass
    except:

        # TODO 暂不处理，具体问题问题具体分析
        pass

    if db_session:
        db_session.close()
