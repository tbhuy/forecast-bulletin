import os
import re
import uuid

from flask import Flask, request
from flask_restplus import Api, Resource, fields
from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

from sparkinclimate.pdf import PDFDocument
from sparkinclimate.places import Communes

communes = Communes()

app = Flask(__name__)
api = Api(app, version='1.0', title='SparkInClimate API',
          description='An API for extraction climate data',
          )

nsplaces = api.namespace('places', description='Place extraction API')

annotation_args = api.parser()
annotation_args.add_argument('text', type=str, required=True, location='form', help='The text to be annotated')
annotation_args.add_argument('context', type=str, required=False, location='form',
                             help='Comma-separated contexts (e.g. region:aquitaine)')

location = api.model('Location', {
    'lat': fields.Float(required=True, description='The latitude'),
    'lon': fields.Float(required=True, description='The longitude')
})
geometry = api.model('Geometry', {
    'location': fields.Nested(location, required=False, description='The location')
})
place = api.model('Place', {
    'name': fields.String(required=True, description='The name of the place'),
    'country': fields.String(required=False, description='The country of the place'),
    'region': fields.String(required=False, description='The region of the place (France)'),
    'department': fields.String(required=False, description='The department of the place (France)'),
    'prefecture': fields.String(required=False, description='The prefecture of the place (France)'),
    'commune': fields.String(required=False, description='The commune of the place (France)'),
    'code_insee': fields.String(required=False, description='The INSEE code of the place'),
    'zip': fields.String(required=False, description='The zip code of the place (France)'),
    'geometry': fields.Nested(geometry, required=False, description='The geometry')
})
places = api.model('Places', {'places': fields.List(fields.Nested(place))})


@nsplaces.route('/lookup/<name>')
@nsplaces.response(404, 'Place not found')
@nsplaces.param('name', 'The name of place')
class PlaceLookup(Resource):
    '''Lookup and extract places'''

    @nsplaces.doc('get_place')
    @nsplaces.marshal_with(place)
    def get(self, name):
        '''Gets a place by its name'''
        place = communes.lookup(name)
        if place:
            return place
        else:
            api.abort(404, "Place {} doesn't exist".format(name))


@nsplaces.route('/annotate')
class PlaceExtract(Resource):
    '''Annotate a text with places'''

    @nsplaces.doc('post_places_annotate')
    @nsplaces.marshal_with(places)
    @api.expect(annotation_args, validate=True)
    def post(self):
        '''Annotates text with palces'''

        args = annotation_args.parse_args()
        text = args['text']
        context = {}
        if 'context' in args:
            if args['context']:
                for constraint in re.split(',+', args['context']):
                    options = re.split('\:+', constraint.strip())
                    if len(options) > 1:
                        context[options[0].strip()] = options[1].strip()

        print(context)
        return communes.annotate(text, context=context)


nspdf = api.namespace('pdf', description='PDF file parsing')

pdf_parser = reqparse.RequestParser()
pdf_parser.add_argument('pdf', location='files', type=FileStorage, required=True, help='The PDF file to be parsed')

templates=['custom']
for template in os.listdir('resources/templates'):
    templates.append(template.replace('.json',''))

pdf_logical = pdf_parser.copy()
pdf_logical.add_argument('template', choices=templates, type=str, required=False, location='from', help='The text to be annotated')
pdf_logical.add_argument('custom-template', location='files', type=FileStorage, required=False, help='The PDF file to be parsed')



html = api.model('html', {'html': fields.String(required=False, description='HTML source code')})

level = api.model('Level', {
    'selectors': fields.List(fields.String, required=True, description='The name of the place'),
    'tag': fields.String(required=True, description='The country of the place'),
    'level': fields.Integer(required=True, description='The region of the place (France)')
})
template = api.model('Template', {
    'levels': fields.List(fields.Nested(level))
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


@nspdf.route('/facts')
class PDFFacts(Resource):
    '''Parse PDF Document'''

    @nspdf.doc('post_pdffacts')
    #@nspdf.marshal_with(html)
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
            facts = pdf.facts()

        if facts:
            return facts
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

        args = pdf_parser.parse_args()


        uploaded_pdf = args['pdf']
        pdf_file = 'cache/pdf/' + str(uuid.uuid4()) + '.pdf'
        if not os.path.exists(os.path.dirname(pdf_file)):
            os.makedirs(os.path.dirname(pdf_file))
        uploaded_pdf.save(pdf_file)


        template_file=None
        if 'template' in args:
            if args['template']:
                template=args['template']
                if template=='custom':
                    if 'custom-template' in args:
                        if args['custom-template']:
                            uploaded_template = args['custom-template']
                            file = 'cache/json/' + str(uuid.uuid4()) + '.json'
                            if not os.path.exists(os.path.dirname(file)):
                                os.makedirs(os.path.dirname(file))
                            uploaded_template.save(file)
                            template_file=file
                else:
                    file='resources/templates/'+template+'.json'
                    if os.path.exists(os.path.dirname(file)):
                        template_file=file
        html = None
        if os.path.isfile(pdf_file):
            pdf = PDFDocument(pdf_file)
            html = pdf.logical(template_file=template_file)

        if html:
            return {'html': html}
        else:
            api.abort(500, "Problem while parsing the PDF")


if __name__ == '__main__':
    # app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
    # app.config['RESTPLUS_VALIDATE'] = True
    app.config['RESTPLUS_MASK_SWAGGER'] = False
    # app.config['ERROR_404_HELP'] = False

    app.run(debug=True, host='0.0.0.0')
