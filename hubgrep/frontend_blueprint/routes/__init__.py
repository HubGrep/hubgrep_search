from flask import request

def get_from_request(key, default=None):
    try:
        return request.form[key]
    except KeyError:
        return request.args.get(key, default)
