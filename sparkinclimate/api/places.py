import re

from flask_restplus import Resource, fields

from sparkinclimate.api import api
from sparkinclimate.api import communes

nsplaces = api.namespace('places', description='Place extraction API')

annotation_args = api.parser()
annotation_args.add_argument('text', type=str, required=True, location='form', help='The text to be annotated')
annotation_args.add_argument('context', type=str, required=False, location='form',
                             help='Comma-separated contexts (e.g. region:aquitaine)')

location = api.model('Location', {
    'lat': fields.Float(required=True, description='The latitude'),
    'lon': fields.Float(required=True, description='The longitude')
})

viewport = api.model('Viewport', {
    'northeast': fields.Nested(location, required=True, description='The location'),
    'southwest': fields.Nested(location, required=True, description='The location')
})

geometry = api.model('Geometry', {
    'location': fields.Nested(location, required=False, description='The location'),
    'viewport': fields.Nested(viewport, required=False, description='The location')
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
    @nsplaces.expect(annotation_args, validate=True)
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
