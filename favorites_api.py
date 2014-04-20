from google.appengine.ext.db import Key

__author__ = 'wojtowpj'

from beer_api import Beer
from user_api import User
from auth import requires_auth
from db_helper import IdUrlField, generate_sorted_query
from flask.ext.restful import Resource, fields, reqparse, marshal, abort
from google.appengine.ext import db


class Favorites(db.Model):
    beer = db.ReferenceProperty(Beer)
    user = db.ReferenceProperty(User)

beer_summary_fields = {
    'name': fields.String,
    'uri': IdUrlField('beer', absolute=True),
}

user_summary_fields = {
    'user_name': fields.String,
    'uri': IdUrlField('user', absolute=True),
}

favorite_fields = {
    'beer': fields.Nested(beer_summary_fields),
    'user': fields.Nested(user_summary_fields),
    'uri': IdUrlField('favorite', absolute=True),
}

favorite_user_fields = {
    'beer': fields.Nested(beer_summary_fields),
    'uri': IdUrlField('favorite', absolute=True),
}


class FavoritesListApi(Resource):
    def __init__(self):
        self.postparse = reqparse.RequestParser()
        self.postparse.add_argument('beer_id', type=int, required=True, help='beer_id is required')
        self.postparse.add_argument('user_id', type=int, required=True, help='user_id is required')

        super(FavoritesListApi, self).__init__()

    @requires_auth
    def get(self):
        favorites = []
        for f in generate_sorted_query(Favorites):
            favorites.append(f)
        return {'favorites': map(lambda f: marshal(f, favorite_fields), favorites)}

    @requires_auth
    def post(self):
        args = self.postparse.parse_args()
        return add_favorite(args.user_id, args.beer_id)


class FavoritesApi(Resource):
    @requires_auth
    def get(self, id):
        f = Favorites.get_by_id(id)
        if f is None:
            abort(404)
        return {'favorite': marshal(f, favorite_fields)}

    @requires_auth
    def delete(self, id):
        f = Favorites.get_by_id(id)
        if f is None:
            abort(404)
        f.delete()
        return {'favorite': marshal(f, favorite_fields), 'action': 'deleted'}


class FavoritesUserApi(Resource):
    def __init__(self):
        self.postparse = reqparse.RequestParser()
        self.postparse.add_argument('beer_id', type=int, required=True, help='beer_id is required')

        super(FavoritesUserApi, self).__init__()

    @requires_auth
    def get(self, id):
        favorites = []
        u = User.get_by_id(id)
        if u is None:
            abort(404, message="User not found")
        for f in generate_sorted_query(Favorites).filter('user', u):
            favorites.append(f)
        return {'favorites': map(lambda f: marshal(f, favorite_user_fields), favorites)}

    @requires_auth
    def post(self, id):
        args = self.postparse.parse_args()
        return add_favorite(id, args.beer_id)

    @requires_auth
    def delete(self, id):
        args = self.postparse.parse_args()
        f = Favorites.all()\
            .filter('beer', Key.from_path("Beer", args.beer_id))\
            .filter('user', Key.from_path("User", id))\
            .get()
        if f is None:
            abort(404, message="Favorite not found")
        f.delete()
        return {'favorite': marshal(f, favorite_fields), 'action': 'deleted'}


def add_favorite(user_id, beer_id):
    u = User.get_by_id(user_id)
    if u is None:
        abort(404, message="User not found")

    b = Beer.get_by_id(beer_id)
    if b is None:
        abort(404, message="Beer not found")
    f = Favorites.all(keys_only=True) \
        .filter('user', u)\
        .filter('beer', b) \
        .get()
    if f:
        abort(409, message="User already has this beer marked as favorite")

    f = Favorites(user=u,
                  beer=b)
    f.put()
    return {'favorite': marshal(f, favorite_fields)}
