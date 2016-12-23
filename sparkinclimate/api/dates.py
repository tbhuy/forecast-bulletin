import re
import datetime

from flask_restplus import Resource, fields

from sparkinclimate.api import api
from sparkinclimate.api import communes
from sparkinclimate.text import TextUtils

nsdates = api.namespace('dates', description='Date and periods extraction API')

dates_args = api.parser()
dates_args.add_argument('text', type=str, required=True,  help='A text containing a date reference')
dates_args.add_argument('context', type=str, required=False, trim=True,
                       default=datetime.datetime.now().strftime("%Y-%m-%d"),
                       help='Contextual date (yyyy-MM-dd)')


date = api.model('date', {
    'date': fields.String(required=False, description='The date (yyyy-MM-dd)'),
    'endDate': fields.String(required=False, description='The start date for a period (yyyy-MM-dd)'),
    'startDate': fields.String(required=False, description='The end date for a period (yyyy-MM-dd)'),
})

dates = api.model('dates', {
    'original_text': fields.String(required=False, description='Original submitted text to API'),
    'nodate_text': fields.String(required=False, description='The text after removing identified dates'),
    'dates': fields.List(fields.Nested(date), required=False, description='The list of extracted dates')
})


@nsdates.route('/extract')
class DateParser(Resource):

    @nsdates.doc('get_dates_extract')
    @nsdates.marshal_with(dates)
    @nsdates.expect(dates_args, validate=True)
    def get(self):
        '''Extracts and resolve date and periods from a text based on contextual date'''
        args = dates_args.parse_args()
        res= TextUtils.extract_date(args.text, context=args.context) 
        return res

