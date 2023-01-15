from flask_restful import Api as _Api


class Api(_Api):

    def handle_user_exception(self, e):
        """
        DO NOT CHANGE ERROR HANDLER !!!!
        """
        return self.app.handle_user_exception(e)
