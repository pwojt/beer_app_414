from beer_glass_api import BeerGlass
from user_api import User

__author__ = 'wojtowpj'
from auth import requires_auth
from db_helper import IdUrlField, update_model, generate_sorted_query, ReferenceUrlField
from flask.ext.restful import Resource, fields, reqparse, marshal, abort
from google.appengine.ext import db
import datetime


class Beer(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty()
    ibu = db.FloatProperty()
    calories = db.FloatProperty()
    abv = db.FloatProperty()
    style = db.StringProperty()
    brewery_location = db.StringProperty()
    beer_glass = db.ReferenceProperty(BeerGlass)

glass_uri_fields = {
    'uri': IdUrlField('beer_glass', absolute=True),
}

beer_fields = {
    'name': fields.String,
    'description': fields.String,
    'ibu': fields.Float,
    'calories': fields.Float,
    'abv': fields.Float,
    'style': fields.String,
    'brewery_location': fields.String,
    'beer_glass': ReferenceUrlField('beer_glass', absolute=True),
    'uri': IdUrlField('beer', absolute=True),
}


class BeerListApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, help='name is required')
        self.reqparse.add_argument('user_id', type=int, required=True, help='user_id is required')
        self.reqparse.add_argument('description', type=str)
        self.reqparse.add_argument('ibu', type=float)
        self.reqparse.add_argument('calories', type=float)
        self.reqparse.add_argument('abv', type=float)
        self.reqparse.add_argument('style', type=str)
        self.reqparse.add_argument('brewery_location', type=str)
        self.reqparse.add_argument('beer_glass_id', type=int)

        super(BeerListApi, self).__init__()

    @requires_auth
    def get(self):
        beer_list = []
        for b in generate_sorted_query(Beer):
            beer_list.append(b)
        return {'beer': map(lambda b: marshal(b, beer_fields), beer_list)}

    @requires_auth
    def post(self):
        args = self.reqparse.parse_args()
        b = Beer.all(keys_only=True).filter('name', args.name).get()
        if b:
            abort(409, message="Beer with name '%s' already exists" % args.name)
        g = None
        if args.beer_glass_id:
            g = BeerGlass.get_by_id(args.beer_glass_id)
        u = User.get_by_id(args.user_id)
        if u is None:
            abort(404, message="User not found.")
        date_added = datetime.datetime.utcnow()
        if u.last_beer_add_date is not None:
            next_allowed = (u.last_beer_add_date + datetime.timedelta(days=1) - date_added).total_seconds()
            if next_allowed > 0:
                abort(429, message="User can only add one beer per day.", allowed_in=round(next_allowed))

        if args.description is not None:
            args.description = args.description[:500]
        b = Beer(name=args.name,
                 description=args.description,
                 ibu=args.ibu,
                 calories=args.calories,
                 abv=args.abv,
                 style=args.style,
                 brewery_location=args.brewery_location,
                 beer_glass=g)
        b.put()
        u.last_beer_add_date = date_added
        u.put()
        return marshal(b, beer_fields)


class BeerApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        self.reqparse.add_argument('description', type=str)
        self.reqparse.add_argument('ibu', type=float)
        self.reqparse.add_argument('calories', type=float)
        self.reqparse.add_argument('abv', type=float)
        self.reqparse.add_argument('style', type=str)
        self.reqparse.add_argument('brewery_location', type=str)
        self.reqparse.add_argument('beer_glass_id', type=int)

        super(BeerApi, self).__init__()

    @requires_auth
    def get(self, id):
        beer = Beer.get_by_id(id)
        return {'beer': marshal(beer, beer_fields)}

    @requires_auth
    def put(self, id):
        args = self.reqparse.parse_args()
        b = Beer.get_by_id(id)
        if not b:
            abort(404)
        g = None
        if args.beer_glass_id is not None:
            g = BeerGlass.get_by_id(args.beer_glass_id)
            b.beer_glass = g

        u = dict(filter(lambda (k, v): v is not None, args.items()))
        update_model(b, u)
        b.put()
        return marshal(b, beer_fields)

    @requires_auth
    def delete(self, id):
        b = Beer.get_by_id(id)
        if b:
            b.delete()
            return {'beer': marshal(b, beer_fields), 'action': 'deleted'}
        abort(404)
