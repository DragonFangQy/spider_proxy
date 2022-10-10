from spider_proxy.utils.utils_db import open_session, close_session, commit_session


class BasePipeline(object):

	def __init__(self):
		self.db_session = None
		# 满足条件时提交一次, 默认1000
		self.session_commit_num = 100 * 1

	def open_spider(self, spider):
		self._open_session()
		self._open_spider(spider)

	def _open_session(self):
		self.db_session = open_session()

	def _open_spider(self, spider):
		pass

	def close_spider(self, spider):

		self._close_spider(spider)
		self._close_session()

	def _close_session(self):
		close_session(self.db_session)

	def _close_spider(self, spider):
		pass

	def _commit_session(self, commit_num=None):
		if not commit_num:
			commit_num = self.session_commit_num

		commit_session(self.db_session, commit_num)

	def _session_add_model(self, model):
		self.db_session.add(model)

	def _session_add_model_auto_commit(self, model, commit_num=None):
		self._session_add_model(model)
		self._commit_session(commit_num)
