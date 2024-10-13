class NotFoundError(Exception):
    """Error raised when a resource is not found."""
    pass

class PermissionDeniedError(Exception):
    """Error raised when a user does not have the required permissions."""
    pass

class BadRequestError(Exception):
    """Error raised for a malformed or invalid request."""
    pass

class UnauthorizedError(Exception):
    """Error raised when authentication is required and has failed or has not been provided."""
    pass

class ConflictError(Exception):
    """Error raised when a request conflicts with the current state of the server (e.g., duplicate entry)."""
    pass

class InternalServerError(Exception):
    """Generic server error."""
    pass

