__author__ = 'wojtowpj'

from flask.ext.restful import fields, reqparse, abort


class IdUrlField(fields.Url):
    def output(self, key, obj):
        if obj is None or obj.key() is None:
            return None
        return super(IdUrlField, self).output(key, {'id': obj.key().id()})


class ReferenceUrlField(fields.Url):
    def output(self, key, obj):
        if obj is None:
            return None
        ref = getattr(obj, key)
        if ref is None or ref.key() is None:
            return None
        return super(ReferenceUrlField, self).output(key, {'id': ref.key().id()})


def update_model(model, *values, **kwargs):
    for dictionary in values:
        for key in dictionary:
            if dictionary[key] is not None:
                setattr(model, key, dictionary[key])
    for key in kwargs:
        setattr(model, key, kwargs[key])

sort_parser = reqparse.RequestParser()
sort_parser.add_argument('sort', type=str, location='args')
sort_parser.add_argument('order', type=str, location='args')

def generate_sorted_query(model):
    args = sort_parser.parse_args()
    query = model.all()
    if args.sort:
        if not hasattr(model, args.sort):
            abort(400, message='Cannot sort on "%s" property, invalid property name' % args.sort)
        order = args.sort
        if args.order == 'desc':
            order = '-%s' % order
        query.order(order)

    return query

