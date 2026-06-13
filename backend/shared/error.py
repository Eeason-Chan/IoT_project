"""
TypedError - global error handling utilities.
"""


class TypedError(Exception):
    """Exception with a typed error code."""

    def __init__(self, message, code='UNKNOWN_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DataProcessingError(TypedError):
    def __init__(self, message):
        super().__init__(message, 'DATA_PROCESSING_ERROR')


class NotFoundError(TypedError):
    def __init__(self, message):
        super().__init__(message, 'NOT_FOUND')