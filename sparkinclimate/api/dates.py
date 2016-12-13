import re
import datetime

from flask_restplus import Resource, fields

from sparkinclimate.api import api
from sparkinclimate.api import communes
from sparkinclimate.text import TextUtils

nsdates = api.namespace('dates', description='Date extraction API')

dates_args = api.parser()
dates_args.add_argument('text', type=str, required=True,  help='The text to be annotated')
dates_args.add_argument('context', type=str, required=False, trim=True,
                       default=datetime.datetime.now().strftime("%Y-%m-%d"),
                       help='Comma-separated contexts (e.g. region:aquitaine)')


date = api.model('date', {
    'date': fields.String(required=False, description='The country of the place'),
    'endDate': fields.String(required=False, description='The region of the place (France)'),
    'startDate': fields.String(required=False, description='The region of the place (France)'),
})

dates = api.model('dates', {
    'original_text': fields.String(required=False, description='The country of the place'),
    'nodate_text': fields.String(required=False, description='The country of the place'),
    'dates': fields.List(fields.Nested(date), required=False, description='The country of the place')
})


@nsdates.route('/extract')
class DateParser(Resource):
    '''Extracts logical structure from PDF'''

    @nsdates.doc('get_dates_extract')
    @nsdates.marshal_with(dates)
    @nsdates.expect(dates_args, validate=True)
    def get(self):
        '''Transforms PDF to logical structure'''
        args = dates_args.parse_args()
        res= TextUtils.extract_date(args.text, context=args.context)
        return res

