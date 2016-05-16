import lib.models as models


class Session():

    def __init__(self):
        self.session = models.Session()

    def __enter__(self):
        return self.session

    def __exit__(self, *exception):
        if exception[0] is not None:
            self.session.rollback()
        self.session.close()
