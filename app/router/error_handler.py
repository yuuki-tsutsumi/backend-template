import traceback

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.usecase.error import (
    AppAdminAccessDeniedError,
    AppAdminOnlyAccessError,
    ConflictError,
    DuplicateError,
    EntityNotFoundError,
    GenerationAccessDeniedError,
    GetListUserOrganizationByUserIdEmptyError,
    LackOfPlaceholderInOpenAIResponseError,
    LackOfRequiredAnswerError,
    MemberAccessDeniedError,
    OrgMemberAccessDeniedError,
    PermissionDeniedError,
    ValidationParamError,
)
from app.util import setup_logger

logger = setup_logger(__name__)


class ErrorHandler(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response: Response = await call_next(request)
        except (ValidationParamError, TypeError) as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": f"{str(exc)}"},
            )
        except (
            EntityNotFoundError,
            GetListUserOrganizationByUserIdEmptyError,
        ) as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": str(exc)},
            )
        except (ConflictError, DuplicateError) as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"message": f"{str(exc)}"},
            )
        except (
            AppAdminAccessDeniedError,
            OrgMemberAccessDeniedError,
            GenerationAccessDeniedError,
            MemberAccessDeniedError,
        ) as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": str(exc)},
            )
        except (
            PermissionDeniedError,
            AppAdminOnlyAccessError,
        ) as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": str(exc)},
            )
        except LackOfPlaceholderInOpenAIResponseError as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                content={"message": str(exc)},
            )
        except LackOfRequiredAnswerError as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": str(exc)},
            )
        except Exception as exc:
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"{str(exc)}"},
            )

        return response
