import inspect
from json import dumps
from werkzeug.wrappers import Response
from flask import request

from scip.api.region import region
from scip.api.population import population

methods = {"region": region, "population": population}

__all__ = list(methods.keys()) + ["call"]


def call(session, request_type):
    # this function is mostly copied from PCEX
    try:
        func = methods[request_type]
    except KeyError:
        return Response("Endpoint {} not recognized".format(request_type), status=400)

    # check for required arguments
    required_params = set(get_required_args(func)).difference(["session"])

    provided_params = set(request.args.keys())
    optional_params = set(get_keyword_args(func))

    missing_params = required_params.difference(provided_params)
    if missing_params:
        return Response(
            "Missing query parameters: {}".format(missing_params), status=400
        )

    args = {key: request.args.get(key) for key in required_params}
    kwargs = {
        key: request.args.get(key)
        for key in optional_params
        if request.args.get(key) is not None
    }

    args.update(kwargs)

    rv = func(session, **args)
    resp = Response(dumps(rv), content_type="application/json")
    return resp


# from http://stackoverflow.com/q/196960/
def get_required_args(func):
    args, _, _, defaults, _, _, _ = inspect.getfullargspec(func)
    if defaults:
        args = args[: -len(defaults)]
    return args  # *args and **kwargs are not required, so ignore them.


def get_keyword_args(func):
    args, _, _, defaults, _, _, _ = inspect.getfullargspec(func)
    if defaults:
        return args[-len(defaults) :]
    else:
        return []
