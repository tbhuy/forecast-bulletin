import json
import os
import uuid

from flask_restplus import Resource, fields
from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

from sparkinclimate.api import api
from sparkinclimate.pdf import PDFDocument

nspdf = api.namespace('pdf', description='PDF file parsing API')

template_choices = ['custom']
for template in os.listdir('resources/templates'):
    template_choices.append(template.replace('.json', ''))

pdf_parser = reqparse.RequestParser()
pdf_parser.add_argument('pdf', location='files', type=FileStorage, required=True, help='The PDF file to be parsed')

pdf_logical = pdf_parser.copy()
pdf_logical.add_argument('custom-template', location='files', type=FileStorage, required=False,
                         help='The JSON template file to be used for parsing PDF file. Check "Template" model for more information about how this file must be structured.')
pdf_logical.add_argument('template', type=str, required=True, trim=True, location='form', choices=template_choices,
                         help='The predefined tempate that sould be used for parsing file. Setting this paramter to "custom" allow to consider the submitted template file.')
html = api.model('html', {'html': fields.String(required=False, description='HTML source code')})

level = api.model('level', {
    'selectors': fields.List(fields.String, required=False, description='The country of the place'),
    'tag': fields.String(required=False, description='The country of the place'),
    'level': fields.Integer(required=False, description='The country of the place')
})

fusion = api.model('fusion', {
    'first': fields.List(fields.String, required=False, description='The country of the place'),
    'second': fields.List(fields.String, required=False, description='The country of the place')
})

template = api.model('template', {
    'levels': fields.List(fields.Nested(level), required=False, description='The country of the place'),
    'exclude': fields.List(fields.String, required=False, description='The country of the place'),
    'fusion': fields.List(fields.String, required=False, description='The country of the place')
})

templates = api.model('templates',
                      {'templates': fields.List(fields.String, required=False, description='The list of templates')})


@nspdf.route('/template/<id>')
@nspdf.response(404, 'Template not found')
@nspdf.param('id', 'The identifier of the template')
class Template(Resource):
    @nspdf.doc('get_template')
    @nspdf.marshal_with(template)
    def get(self, id):
        '''Retrieve the template using its identifier'''

        file = 'resources/templates/' + str(id) + '.json'
        if os.path.isfile(file):
            with open(file, 'r') as file:
                return json.load(file)
        else:
            api.abort(404, "Template {} doesn't exist".format(id))


@nspdf.route('/templates')
class Templates(Resource):
    @nspdf.doc('get_templates')
    @nspdf.marshal_with(templates)
    def get(self):
        '''Retrieve the liste of templates'''


        global template_choices

        return {'templates': template_choices[1:]}


@nspdf.route('/parse')
class PDFParse(Resource):
    @nspdf.doc('post_pdf_parse')
    @nspdf.marshal_with(html)
    @nspdf.expect(pdf_parser, validate=True)
    def post(self):
        '''Transforms PDF document to HMTL'''

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
        '''Transforms PDF document into a logically structured HTML'''

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
        print("Template File: " + str(template_file))
        if os.path.isfile(pdf_file):
            pdf = PDFDocument(pdf_file)
            html = pdf.logical(template_file=template_file)

        if html:
            return {'html': html}
        else:
            api.abort(500, "Problem while parsing the PDF")
