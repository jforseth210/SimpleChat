import inspect
import logging
from functools import wraps
from typing import get_origin

from flask import request, abort
from werkzeug.datastructures import MultiDict


logger = logging.getLogger(__name__)


def body_to_args(func):
    """
    This is a decorator I wrote a while ago that takes a request body 
    and converts it to arguments.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = load_request_data(**kwargs)

        # See what arguments the decorated function is expecting
        sig = inspect.signature(func)
        expected_parameters = sig.parameters

        # Warn if we recieve more json than expected
        if len(request_data) > len(expected_parameters):
            logger.warning("Extra argument provided")

        # Check for each of the expected arguments in the json
        for param_name, expected_param in expected_parameters.items():
            # If this parameter has a default value, it's optional
            is_required = expected_param.default == inspect.Parameter.empty

            if param_name in request_data:
                kwargs[param_name] = attempt_type_conversion(
                    request_data.get(param_name), expected_param.annotation)

            # If the decorated function is expecting a value we don't have in the request json,
            # tell the client.
            elif is_required and param_name not in request_data:
                logger.warning(f'Missing required argument: {param_name}')
                abort(400, f'Missing required argument: {param_name}')
        return func(*args, **kwargs)
    return wrapper


def load_request_data(**kwargs):
    # Load json from request
    json = request.get_json(silent=True, force=True)
    if json is None:
        json = {}

    request_data = MultiDict()
    for k, v in kwargs.items():
        request_data.add(k, [v])

    for k, v in json.items():
        request_data.add(k, [v])

    for k, v in request.args.lists():
        request_data.add(k, v)

    for k, v in request.form.lists():
        request_data.add(k, v)

    logger.debug(f"Data: {request_data}")

    # Catch empty data
    if request_data is None:
        logger.warning("No data")
        abort(400, 'No data provided')
    return request_data


def attempt_type_conversion(data: list, type_to_convert_to: type):
    # Add the json kv pair to the function kwargs
    if type_to_convert_to == list or get_origin(type_to_convert_to) == list:
        return data
    elif type_to_convert_to == bool:
        return data[0] in ["true", "on", "yes"]
    elif type_to_convert_to == str:
        return str(data[0])
    elif type_to_convert_to == float:
        return float(data[0])
    elif type_to_convert_to == int:
        return int(data[0])
    else:
        return data[0]
