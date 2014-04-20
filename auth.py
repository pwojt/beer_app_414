from passlib.hash import sha512_crypt
from functools import wraps
from flask import request, Response, abort
from google.appengine.ext import db


def check_auth(user_name, password):
    user = db.GqlQuery("SELECT * from User WHERE user_name = :user", user=user_name).get()
    if user is None:
        return False
    return sha512_crypt.verify(password, user.password)


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return abort(401)


def hash_password(password):
    return sha512_crypt.encrypt(password)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

