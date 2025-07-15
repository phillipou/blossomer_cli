from fastapi import HTTPException
import logging
from typing import Callable, Awaitable, Any
from fastapi import status

logger = logging.getLogger(__name__)

async def run_service(service_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
    """
    Standardizes service execution and error handling for API routes.

    - Calls the given service function with provided arguments.
    - Catches and logs exceptions, raising a standard HTTP 500 error.
    - Returns the service function's result on success.

    Args:
        service_func: The asynchronous service function to execute.
        *args: Positional arguments to pass to the service function.
        **kwargs: Keyword arguments to pass to the service function.

    Returns:
        The result of the service function.

    Raises:
        HTTPException: If the service function raises any exception.
    """
    try:
        # Correctly log both positional and keyword arguments
        arg_log = f"args={args}, " if args else ""
        kwarg_log = f"kwargs={kwargs}" if kwargs else ""
        logger.debug(f"Running service: {service_func.__name__} with {arg_log}{kwarg_log}")
        return await service_func(*args, **kwargs)
    except Exception as e:
        # Log the full exception traceback for better debugging
        logger.error(f"Error in service {service_func.__name__}: {e}", exc_info=True)
        # Re-raise a standard HTTPException to avoid leaking implementation details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred in {service_func.__name__}: {e}",
        ) 