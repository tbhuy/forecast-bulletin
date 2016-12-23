from flask import Flask
from flask_restplus import Api
from sparkinclimate.places import Communes



app = Flask(__name__)
api = Api(app, version='1.0', title='SparkInClimate API',
          description='A RESTful API for extraction weather facts extraction and search based on Meteo France monthly reports.',
          )
communes = Communes()