from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse

from core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    BadRequestError,
    UnauthorizedError,
    ConflictError,
    InternalServerError
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except NotFoundError as exc:
            return JSONResponse(status_code=404, content={"detail": str(exc)})
        except PermissionDeniedError as exc:
            return JSONResponse(status_code=403, content={"detail": str(exc)})
        except BadRequestError as exc:
            return JSONResponse(status_code=400, content={"detail": str(exc)})
        except UnauthorizedError as exc:
            return JSONResponse(status_code=401, content={"detail": str(exc)})
        except ConflictError as exc:
            return JSONResponse(status_code=409, content={"detail": str(exc)})
        except InternalServerError as exc:
            return JSONResponse(status_code=500, content={"detail": str(exc)})
        except Exception as exc:
            # Para cualquier otra excepción no prevista
            return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(exc)}"})