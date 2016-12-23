import csv
import datetime
import os
import uuid

from flask_restplus import Resource, fields
from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

from sparkinclimate.api import api
from sparkinclimate.api import communes
from sparkinclimate.pdf import PDFDocument
from sparkinclimate.api.pdf import pdf_parser
from sparkinclimate.api.places import geometry
from sparkinclimate.api.places import place

nsfacts = api.namespace('facts', description='Facts extraction API')


regions = []
try:
    file = open('resources/region_list.csv', "r", encoding='utf-8')
    reader = csv.reader(file, delimiter="\t", quotechar='"')
    first = True
    for row in reader:
        if len(row) > 0:
            id = row[0] if row[0] != "" else None
            name = row[1] if row[1] != "" else None
            regions.append(name)
finally:
    file.close()

pdf_facts = pdf_parser.copy()
pdf_facts.add_argument('region', type=str, required=True, trim=True, location='form', choices=regions,
                       help='The region of the weather report')
pdf_facts.add_argument('date', type=str, required=True, trim=True, location='form',
                       default=datetime.datetime.now().strftime("%Y-%m-%d"),
                       help='The issue date of the weather report ')


day = api.model('Day', {
    'year': fields.Integer(required=True, description='The region of the place (France)'),
    'month': fields.String(required=False, description='The country of the place'),
    'day': fields.Integer(required=True, description='The region of the place (France)')
})

region = api.model('Region', {
    'name': fields.String(required=False, description='The country of the place'),
    'formatted_address': fields.String(required=False, description='The country of the place'),
    'geometry': fields.Nested(geometry, required=False, description='The geometry')
})

fact = api.model('Fact', {
    'title': fields.String(required=True, description='The country of the place'),
    'description': fields.String(required=False, description='The country of the place'),

    'dateIssued': fields.String(required=False, description='The country of the place'),
    'startDate': fields.String(required=False, description='The country of the place'),
    'endDate': fields.String(required=False, description='The country of the place'),
    'date': fields.Nested(day, required=False, description='The country of the place'),

    'facts': fields.List(fields.String, required=False, description='The country of the place'),
    'keywords': fields.List(fields.String, required=False, description='The country of the place'),

    'places': fields.List(fields.Nested(place), required=False, description='The country of the place'),
    'region': fields.List(fields.Nested(region), required=False, description='The country of the place')

})
facts = api.model('Facts', {
    'facts': fields.List(fields.Nested(fact))
})

@nsfacts.route('/extract')
class PDFFacts(Resource):
    '''Parse PDF Document'''

    @nsfacts.doc('post_facts_extract')
    @nsfacts.marshal_with(facts)
    @nsfacts.expect(pdf_facts, validate=True)
    def post(self):
        '''Extracts weather facts from PDF document of Meteo France weather reports.'''

        args = pdf_facts.parse_args()
        uploaded_file = args['pdf']  # This is FileStorage instance
        input_file = 'cache/pdf/' + str(uuid.uuid4()) + '.pdf'
        if not os.path.exists(os.path.dirname(input_file)):
            os.makedirs(os.path.dirname(input_file))
        uploaded_file.save(input_file)

        date = args['date'] if args['pdf']  else datetime.datetime.now().strftime("%Y-%m-%d")
        region = args['region'] if args['region']  else 'Alsace'

        html = None
        if os.path.isfile(input_file):
            pdf = PDFDocument(input_file)
            facts = pdf.facts(date=date, region=region)

        if facts:
            return facts
        else:
            api.abort(500, "Problem while parsing the PDF")