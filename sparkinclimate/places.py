import csv
import json

import nltk
import jsonpickle

from sparkinclimate.text import TextUtils




class JSONSerializable(object):
    def __repr__(self):
        return jsonpickle.encode(self)


class Location(JSONSerializable):
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon


class Geometry(JSONSerializable):
    def __init__(self, location=None):
        self.location = location


class Place(JSONSerializable):
    def __init__(self, name):
        self.name = name
        self.geometry = None


class FrenchCommune(Place):
    def __init__(self, name):
        super().__init__(name)
        self.country = 'France'
        self.region = None
        self.department = None
        self.prefecture = None
        self.commune = name
        self.code_insee = None
        self.zip = None


class Communes:
    def __init__(self):
        self.__places = {}
        self.__load(files=['/sparkinclimate/data/eucircos_regions_departements_circonscriptions_communes_gps.csv'])

    def __tokenize(self, text):
        return nltk.word_tokenize(text)

    def lookup(self, name):
        key = TextUtils.normalize(name)
        if key in self.__places:
            return self.__places[key]
        return None

    def annotate(self, text, context=None):
        places = []
        for token in set(self.__tokenize(text)):
            place = self.lookup(token)
            if place:
                conextual = False
                if context:
                    if 'region' in context:
                        pregion = TextUtils.normalize(place.region)
                        cregion = TextUtils.normalize(context['region'])
                        if pregion == cregion or pregion.startswith(cregion) or cregion.startswith(pregion):
                            conextual = True
                else:
                    conextual = True
                if conextual:
                    places.append(place)
        return {'places': places}

    def __load(self, files=None):
        if files is None:
            files = []
        for filename in files:
            file = open(filename, "r", encoding='utf-8')
            try:
                reader = csv.reader(file, delimiter=";", quotechar='"')
                first = True
                for row in reader:
                    if not first:
                        name = row[8] if row[8] != "" else None
                        commune = FrenchCommune(name)
                        commune.region = row[2] if row[2] != "" else None
                        commune.department = row[5] if row[5] != "" else None
                        commune.prefecture = row[6] if row[6] != "" else None
                        commune.code_insee = row[10] if row[10] != "" else None
                        commune.zip = row[9] if row[9] != "" else None
                        # noinspection PyBroadException
                        try:
                            lat = float(row[11].replace("\s+", "").replace(",", ".")) if row[11] != "" else None
                            lon = float(row[12].replace("\s+", "").replace(",", ".")) if row[12] != "" else None
                            location = Location(lat=lat, lon=lon) if lat and lon else None
                            geometry = Geometry(location=location) if location else None
                            commune.geometry = geometry if geometry else None
                        except:
                            pass
                        key = TextUtils.normalize(commune.name).lower().strip()
                        self.__places[key] = commune
                    first = False
            finally:
                file.close()
