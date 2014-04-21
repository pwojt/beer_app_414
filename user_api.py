from functools import wraps

from google.appengine.ext import db
from google.appengine.api import users

from db_helper import IdUrlField, generate_sorted_query, update_model
from flask import abort, redirect, request
from flask.ext.restful import Resource, reqparse, fields, marshal
from auth import requires_auth, hash_password


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)

    return decorated_view


class User(db.Model):
    user_name = db.StringProperty(required=True)
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    last_beer_add_date = db.DateTimeProperty(required=False)

    @property
    def id(self):
        return self.key().id()


user_fields = {
    'user_name': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'last_beer_add_date': fields.DateTime,
    'uri': IdUrlField('user', absolute=True),
}


class UserListApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("user_name", type=str, required=True, help='User Name Is Required')
        self.reqparse.add_argument("first_name", type=str, required=True, help='First Name Is Required')
        self.reqparse.add_argument("last_name", type=str, required=True, help='Last Name Is Required')
        self.reqparse.add_argument("password", type=str, required=True, help='Password Is Required')

        super(UserListApi, self).__init__()

    @requires_auth
    def get(self):
        user_list = []
        for u in generate_sorted_query(User):
            user_list.append(u)
        return {'users': map(lambda u: marshal(u, user_fields), user_list)}

    @requires_auth
    def post(self):
        args = self.reqparse.parse_args()

        u = User.all(keys_only=True).filter('user_name', args['user_name']).get()
        if u:
            abort(409, message="User with user_name '%s' already exists" % args['user_name'])
        u = User(user_name=args.user_name,
                 first_name=args.first_name,
                 last_name=args.last_name,
                 password=hash_password(args.password))
        u.put()
        return {'user': marshal(u, user_fields)}


class UserApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("user_name", type=str)
        self.reqparse.add_argument("first_name", type=str)
        self.reqparse.add_argument("last_name", type=str)
        self.reqparse.add_argument("password", type=str)
        self.reqparse.add_argument("last_beer_add_date", type=str)

        super(UserApi, self).__init__()

    @requires_auth
    def get(self, id):
        user = User.get_by_id(id)
        if user is None:
            abort(404)
        return {'user': marshal(user, user_fields)}

    @requires_auth
    def put(self, id):
        user = User.get_by_id(id)
        if user is None:
            abort(404)
        args = self.reqparse.parse_args()
        u = dict(filter(lambda (k, v): v is not None, args.items()))
        if u.get('password') is not None:
            u['password'] = hash_password(u['password'])
        update_model(user, u)

        user.put()
        return {'user': marshal(user, user_fields)}

    @requires_auth
    def delete(self, id):
        user = User.get_by_id(id)
        if user is None:
            abort(404)

        user.delete()
        return {'user': marshal(user, user_fields), 'action': 'deleted'}
