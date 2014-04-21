from auth import requires_auth
from db_helper import IdUrlField, update_model
from flask.ext.restful import Resource, fields, reqparse, marshal, abort

__author__ = 'wojtowpj'

from google.appengine.ext import db


class BeerGlass(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=False)
    capacity = db.FloatProperty(required=False)


glass_fields = {
    'name': fields.String,
    'description': fields.String,
    'capacity': fields.Float,
    'uri': IdUrlField('beer_glass', absolute=True),
}


class BeerGlassListApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, help="Beer Glass Name is required")
        self.reqparse.add_argument('description', type=str)
        self.reqparse.add_argument('capacity', type=float)

        super(BeerGlassListApi, self).__init__()

    @requires_auth
    def get(self):
        glass_list = []
        for g in db.Query(BeerGlass):
            glass_list.append(g)
        return {'beer_glasses': map(lambda g: marshal(g, glass_fields), glass_list)}

    @requires_auth
    def post(self):
        args = self.reqparse.parse_args()
        g = BeerGlass.all(keys_only=True).filter('name', args['name']).get()
        if g:
            abort(409, message="Beer glass with name %s already exists" % args['name'])
        g = BeerGlass(name=args['name'],
                      description=args.get('description'),
                      capacity=args.get('capacity'))
        g.put()
        return {'beer_glass': marshal(g, glass_fields)}


class BeerGlassApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        self.reqparse.add_argument('description')
        self.reqparse.add_argument('capacity')

        super(BeerGlassApi, self).__init__()

    @requires_auth
    def get(self, id):
        g = BeerGlass.get_by_id(id)
        if not g:
            abort(404)
        return {'beer_glass': marshal(g, glass_fields)}

    @requires_auth
    def put(self, id):
        args = self.reqparse.parse_args()
        g = BeerGlass.get_by_id(id)
        if not g:
            abort(404)

        u = dict(filter(lambda (k, v): v is not None, args.items()))
        update_model(g, u)

        g.put()
        return {'beer_glass': marshal(g, glass_fields)}

    @requires_auth
    def delete(self, id):
        g = BeerGlass.get_by_id(id)
        if g:
            g.delete()
            return {"beer_glass": marshal(g, glass_fields), 'action': 'deleted'}
        abort(404)
