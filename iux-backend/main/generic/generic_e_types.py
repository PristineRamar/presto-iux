from fastapi import HTTPException

class DataHTTPException(HTTPException):
    def __init__(self, status_code, detail, error_message):
        super().__init__(status_code=status_code, detail=detail)
        self.error_message = error_message

class LLMHTTPException(HTTPException):
    def __init__(self, status_code, detail, custom_message):
        super().__init__(status_code=status_code, detail=detail)
        self.custom_message = custom_message