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
from sparkinclimate.api.places import geometry
from sparkinclimate.api.places import place

nspdf = api.namespace('pdf', description='PDF file parsing')

templates = ['custom']
for template in os.listdir('resources/templates'):
    templates.append(template.replace('.json', ''))

pdf_parser = reqparse.RequestParser()
pdf_parser.add_argument('pdf', location='files', type=FileStorage, required=True, help='The PDF file to be parsed')

pdf_logical = pdf_parser.copy()
pdf_logical.add_argument('custom-template', location='files', type=FileStorage, required=False,
                         help='The PDF file to be parsed')
pdf_logical.add_argument('template', type=str, required=True, trim=True, location='form', choices=templates, help='The text to be annotated')

html = api.model('html', {'html': fields.String(required=False, description='HTML source code')})

level = api.model('Level', {
    'selectors': fields.List(fields.String, required=True, description='The name of the place'),
    'tag': fields.String(required=True, description='The country of the place'),
    'level': fields.Integer(required=True, description='The region of the place (France)')
})
template = api.model('Template', {
    'levels': fields.List(fields.Nested(level))
})

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


@nspdf.route('/parse')
class PDFParse(Resource):
    '''Parse PDF Document'''

    @nspdf.doc('post_pdf_parse')
    @nspdf.marshal_with(html)
    @nspdf.expect(pdf_parser, validate=True)
    def post(self):
        '''Parse PDF Document'''

        args = pdf_parser.parse_args()
        uploaded_file = args['pdf']  # This is FileStorage instance
        input_file = 'cache/pdf/' + str(uuid.uuid4()) + '.pdf'
        if not os.path.exists(os.path.dirname(input_file)):
            os.makedirs(os.path.dirname(input_file))

        uploaded_file.save(input_file)

        html = None
        if os.path.isfile(input_file):
            pdf = PDFDocument(input_file)
            html = pdf.html()

        if html:
            return {'html': html}
        else:
            api.abort(500, "Problem while parsing the PDF")


@nspdf.route('/logical')
class PDFLogical(Resource):
    '''Extracts logical structure from PDF'''

    @nspdf.doc('post_pdf_logical')
    @nspdf.marshal_with(html)
    @nspdf.expect(pdf_logical, validate=True)
    def post(self):
        '''Transforms PDF to logical structure'''

        args = pdf_logical.parse_args()

        print(args)
        uploaded_pdf = args['pdf']
        pdf_file = 'cache/pdf/' + str(uuid.uuid4()) + '.pdf'
        if not os.path.exists(os.path.dirname(pdf_file)):
            os.makedirs(os.path.dirname(pdf_file))
        uploaded_pdf.save(pdf_file)

        template_file = None
        if 'template' in args:
            if args['template']:
                template = args['template']
                if template == 'custom':
                    if 'custom-template' in args:
                        if args['custom-template']:
                            uploaded_template = args['custom-template']
                            file = 'cache/json/' + str(uuid.uuid4()) + '.json'
                            if not os.path.exists(os.path.dirname(file)):
                                os.makedirs(os.path.dirname(file))
                            uploaded_template.save(file)
                            template_file = file
                else:
                    file = 'resources/templates/' + template + '.json'
                    if os.path.exists(os.path.dirname(file)):
                        template_file = file
        html = None
        print("Template File: "+str(template_file))
        if os.path.isfile(pdf_file):
            pdf = PDFDocument(pdf_file)
            html = pdf.logical(template_file=template_file)

        if html:
            return {'html': html}
        else:
            api.abort(500, "Problem while parsing the PDF")

