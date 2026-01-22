class AppException(Exception):
    status_code: int
    detail: str

class MiddlewareInternalError(AppException):
    status_code = 500
    detail = "Internal Server Error at Middleware"

class Unauthorized(AppException):
    status_code = 401
    detail = "Invalid google token"

class BadRequest(AppException):
    status_code = 400
    detail = "Bad request"

class GoogleCodeMissError(AppException):
    status_code = 422
    detail = "Failed to get Google Auth Code"

class InvalidCookieError(AppException):
    status_code = 401
    detail = "None or Invalid Cookie value"

class InvalidSessionError(AppException):
    status_code = 401
    detail = "Invalid or expired session_id"


class WebSearchToolError(AppException):
    status_code = 500
    detail = "Error during use web tool"