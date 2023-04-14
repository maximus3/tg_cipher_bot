from .error import register_handlers as register_handlers_error
from .start import register_handlers as register_handlers_start


list_of_register_functions = [
    register_handlers_error,
    register_handlers_start,
]


__all__ = [
    'list_of_register_functions',
]
