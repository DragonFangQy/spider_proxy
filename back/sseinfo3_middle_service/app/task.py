from app import app
from tasks import make_celery

celery_app = make_celery(app)

if __name__ == "__main__":
    import sys
    sys.argv.append("-E")
    sys.argv.append("-lINFO")
    sys.argv.append("-b")
    app.worker_main()


    """
    
ALTER TABLE di_down_file ADD COLUMN extract_last_update_time datetime DEFAULT NULL COMMENT '抽取更新时间';
CREATE INDEX di_down_file_file_id ON di_down_file (file_id);
CREATE INDEX di_down_file_extract_last_update_time ON di_down_file (extract_last_update_time);

    """
