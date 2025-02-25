class CustomException(Exception):
    def __init__(self, status_code, message=None, errors=None):
        self.message = message
        self.status_code = status_code
        self.errors = errors
