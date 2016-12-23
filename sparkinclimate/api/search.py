import datetime
import json
import re

from elasticsearch import Elasticsearch
from flask_restplus import Resource

from sparkinclimate.api import api
from sparkinclimate.api.facts import facts

nssearch = api.namespace('search', description='Weather fact search API')

search_args = api.parser()
search_args.add_argument('query', type=str, required=False, help='The text query')
search_args.add_argument('start_date', type=str, required=False, trim=True,
                         default="2011-01-01",
                         # default=datetime.datetime.now().strftime("%Y-%m-%d"),
                         help='start date filter')

search_args.add_argument('end_date', type=str, required=False, trim=True,
                         default=datetime.datetime.now().strftime("%Y-%m-%d"),
                         help='End date filter')

geo_query_types = ['distance', 'bounding_box', 'polygon']

search_args.add_argument('geo_query_type', type=str, required=False, choices=geo_query_types, default='distance',
                         help='The type of geographical query (distance,bounding_box,polygon)')
search_args.add_argument('geo_query', type=str, required=False, default='43.6,1.433333,30km',
                         help='Comma-separated list of parameters of the geographical query. For distance, query, 3 parameters are expected to represent the circle of interest namely the latitude of center point, the longitude of center point and the circle radius (e.g. "43.6,1.43,30km"). For bounding box query, 4 comma-separated parameters are expected including the top-left point latitude, the top-left point longitude, the bottom-right point latitude  and  the bottom-right point longitude (e.g. "45.04,3.45,42.57,-0.32"). For polygon query, a pair number of comma-separated parameters is expected. Each two successive parameters represent the latitude and the longitude of a polygon point (e.g. "45.04,3.45,49.07,8.233,42.98,4.23,42.57,-0.32").')


@nssearch.route('/facts')
class Search(Resource):
    '''Extracts logical structure from PDF'''

    @nssearch.doc('get_dates_extract')
    @nssearch.marshal_with(facts)
    @nssearch.expect(search_args, validate=True)
    def get(self):
        '''Transforms PDF to logical structure'''

        es = Elasticsearch(['http://ns3038079.ip-5-135-160.eu/'])
        args = search_args.parse_args()
        query = args['query']
        start_date = args['start_date']
        end_date = args['end_date'] if args['start_date'] != args['end_date'] else None

        start_date = start_date if start_date != '' else None
        end_date = end_date if end_date != '' else None

        geo_query_type = args['geo_query_type']
        geo_query = args['geo_query']

        must = []
        if query:
            must.append({"match": {"facts": query}})
        else:
            must.append({"match_all": {}})

        if start_date and end_date:
            print("Case A")
            must.append({
                "range": {
                    "startDate": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            })
            must.append({
                "range": {
                    "endDate": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            })
        elif start_date and not end_date:
            print("Case B")
            must.append({
                "range": {
                    "startDate": {
                        "gte": start_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            })

        elif end_date and not start_date:
            print("Case C")
            must.append({
                "range": {
                    "startDate": {
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            })

        filter = None
        if geo_query_type == 'distance':
            (lat, long, radius) = re.split(',', geo_query)
            filter = {
                "geo_distance": {
                    "distance": radius,
                    "places.geometry.location": {
                        "lat": lat,
                        "lon": long
                    }
                }
            }
        elif geo_query_type == 'bounding_box':
            (top_left_lat, top_left_lon, top_right_lat, top_right_lon) = re.split(',', geo_query)
            filter = {
                "geo_bounding_box": {
                    "places.geometry.location": {
                        "top_left": {
                            "lat": top_left_lat,
                            "lon": top_left_lon
                        },
                        "bottom_right": {
                            "lat": top_right_lat,
                            "lon": top_right_lon
                        }
                    }
                }
            }
        elif geo_query_type == 'polygon':
            points = []
            fields = re.split(',', geo_query)
            for i in range(0, len(fields) - 1, 2):
                points.append({"lat": fields[i], "lon": fields[i + 1]})

            filter = {
                "geo_polygon": {
                    "places.geometry.location": {
                        "points": points
                    }
                }
            }

        body = {
            "query": {
                "bool": {
                }
            }
        }

        if len(must) > 0:
            body['query']['bool']['must'] = must
        if filter:
            body['query']['bool']['filter'] = filter

        print(json.dumps(body))

        res = es.search(index="sparkinclimate", doc_type='facts', body=body)
        facts = {'facts': []}
        for hit in res['hits']['hits']:
            facts['facts'].append(hit["_source"])
        # args = search_args.parse_args()
        return facts
