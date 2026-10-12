class ApiError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class ValidationError(ApiError):
    def __init__(self, message):
        super().__init__("VALIDATION_ERROR", message, 400)


class NotFoundError(ApiError):
    def __init__(self, message):
        super().__init__("NOT_FOUND", message, 404)
