import datetime

__author__ = 'wojtowpj'

from beer_api import Beer
from user_api import User
from auth import requires_auth, get_user
from db_helper import IdUrlField, generate_sorted_query
from flask.ext.restful import Resource, fields, reqparse, marshal, abort
from flask import request
from google.appengine.ext import db


class BeerReview(db.Model):
    beer = db.ReferenceProperty(Beer, required=True)
    user = db.ReferenceProperty(User, required=True)
    date_created = db.DateTimeProperty(auto_now_add=True)
    aroma = db.FloatProperty(required=True)
    appearance = db.FloatProperty(required=True)
    taste = db.FloatProperty(required=True)
    palate = db.FloatProperty(required=True)
    bottle_style = db.FloatProperty(required=True)
    overall = db.FloatProperty(required=True)
    comments = db.StringProperty()


class BeerReviewSummary(db.Model):
    beer = db.ReferenceProperty(Beer, required=True)
    count = db.IntegerProperty()
    aroma = db.FloatProperty(required=True)
    appearance = db.FloatProperty(required=True)
    taste = db.FloatProperty(required=True)
    palate = db.FloatProperty(required=True)
    bottle_style = db.FloatProperty(required=True)
    overall = db.FloatProperty(required=True)


beer_reference_fields = {
    'name': fields.String,
    'uri': IdUrlField('beer', absolute=True),
}

user_reference_fields = {
    'user_name': fields.String,
    'uri': IdUrlField('user', absolute=True),
}

beer_review_fields = {
    'user': fields.Nested(user_reference_fields),
    'beer': fields.Nested(beer_reference_fields),
    'date_created': fields.DateTime,
    'aroma': fields.Float,
    'appearance': fields.Float,
    'taste': fields.Float,
    'palate': fields.Float,
    'bottle_style': fields.Float,
    'overall': fields.Float,
    'comments': fields.String,
    'uri': IdUrlField('review', absolute=True)
}

beer_review_summary_fields = {
    'count': fields.Integer,
    'aroma': fields.Float,
    'appearance': fields.Float,
    'taste': fields.Float,
    'palate': fields.Float,
    'bottle_style': fields.Float,
    'overall': fields.Float,
    'beer': fields.Nested(beer_reference_fields),
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('aroma', type=float, required=True, help='aroma is required')
post_parser.add_argument('appearance', type=float, required=True, help='appearance is required')
post_parser.add_argument('taste', type=float, required=True, help='taste is required')
post_parser.add_argument('palate', type=float, required=True, help='palate is required')
post_parser.add_argument('bottle_style', type=float, required=True, help='bottle_style is required')
post_parser.add_argument('comment', type=str)


class BeerReviewListApi(Resource):
    def __init__(self):
        self.getparse = reqparse.RequestParser()
        self.getparse.add_argument('type', type=str, location='args')

        super(BeerReviewListApi, self).__init__()

    @requires_auth
    def get(self):
        args = self.getparse.parse_args()
        if args.type == 'summary':
            summaries = []
            for s in generate_sorted_query(BeerReviewSummary):
                summaries.append(s)
            return {'beer_review_summaries': map(lambda s: marshal(s, beer_review_summary_fields), summaries)}
        else:
            review_list = []
            for r in generate_sorted_query(BeerReview):
                review_list.append(r)
            return {'beer_reviews': map(lambda r: marshal(r, beer_review_fields), review_list)}

    @requires_auth
    def post(self):
        args = post_parser.parse_args()
        if args.get('beer_id') is None:
            abort(400, message="beer_id is required")
        b = Beer.get_by_id(args.beer_id)

        return add_review(b, args)


class BeerReviewApi(Resource):
    @requires_auth
    def get(self, id):
        r = BeerReview.get_by_id(id)
        if not r:
            abort(404)
        return {"beer_review": marshal(r, beer_review_fields)}


class BeerReviewBeerApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type=str, location='args')

        super(BeerReviewBeerApi, self).__init__()

    @requires_auth
    def get(self, id):
        review_list = []
        b = Beer.get_by_id(id)
        if not b:
            abort(404, message="Beer not found")
        args = self.reqparse.parse_args()
        if args.type == 'summary':
            summary = BeerReviewSummary.all().filter('beer', b).get()
            return {'beer_review_summary': marshal(summary, beer_review_summary_fields)}
        else:
            for r in generate_sorted_query(BeerReview).filter('beer', b):
                review_list.append(r)
            return {'beer_reviews': map(lambda r: marshal(r, beer_review_fields), review_list)}

    @requires_auth
    def post(self, id):
        args = post_parser.parse_args()
        b = Beer.get_by_id(id)

        return add_review(b, args)


class BeerReviewUserApi(Resource):
    def __init__(self):
        super(BeerReviewUserApi, self).__init__()

    @requires_auth
    def get(self, id):
        review_list = []
        u = User.get_by_id(id)
        if not u:
            abort(404, message="User not found")
        for r in generate_sorted_query(BeerReview).filter('user', u):
            review_list.append(r)

        return {'beer_reviews': map(lambda r: marshal(r, beer_review_fields), review_list)}


def moving_average(prev, current, count):
    return prev + (current - prev) / count


def add_review(beer, review_dict):
    def create_review_summary(beer_review):
        summary = BeerReviewSummary.all().filter('beer', beer_review.beer).get()
        if summary:
            summary.count += 1
            summary.aroma = moving_average(summary.aroma, beer_review.aroma, summary.count)
            summary.appearance = moving_average(summary.appearance, beer_review.appearance, summary.count)
            summary.taste = moving_average(summary.taste, beer_review.taste, summary.count)
            summary.palate = moving_average(summary.palate, beer_review.palate, summary.count)
            summary.bottle_style = moving_average(summary.bottle_style, beer_review.bottle_style, summary.count)
            summary.overall = moving_average(summary.overall, beer_review.overall, summary.count)
        else:
            summary = BeerReviewSummary(count=1,
                                        beer=beer_review.beer,
                                        aroma=beer_review.aroma,
                                        appearance=beer_review.appearance,
                                        taste=beer_review.taste,
                                        palate=beer_review.palate,
                                        bottle_style=beer_review.bottle_style,
                                        overall=beer_review.overall)

        summary.put()

    if beer is None:
        abort(404, message="Beer %s not found.")
    user = get_user()
    if user is None:
        abort(404, message="User is not found.")

    date_added = datetime.datetime.utcnow()
    r = BeerReview.all() \
        .filter('beer', beer) \
        .filter('user', user) \
        .filter('date_created >', date_added - datetime.timedelta(days=7)) \
        .get()

    if r:
        allowed_in = (r.date_created + datetime.timedelta(days=7) - date_added).total_seconds()
        abort(429, message="Only one review per user per beer per week allowed.", allowed_in=round(allowed_in))

    scores = [float(review_dict['aroma']), float(review_dict['appearance']), float(review_dict['taste']),
              float(review_dict['palate']),
              float(review_dict['bottle_style'])]
    overall = (sum(scores) / len(scores))
    r = BeerReview(beer=beer,
                   user=user,
                   aroma=review_dict['aroma'],
                   appearance=review_dict['appearance'],
                   taste=review_dict['taste'],
                   palate=review_dict['palate'],
                   bottle_style=review_dict['bottle_style'],
                   overall=overall,
                   comments=review_dict.get('comment'))

    r.put()
    create_review_summary(r)

    return {'beer_review': marshal(r, beer_review_fields)}
