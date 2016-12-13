import csv
import json
import os
import re
import sys
import uuid

# noinspection PyPackageRequirements
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from bs4 import BeautifulSoup, NavigableString
from sparkinclimate.text import TextUtils
import treetaggerwrapper

from nltk.stem.snowball import FrenchStemmer
from sparkinclimate.places import Communes


class PDFDocument(object):
    month_names = [None, "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août",
                   "Septembre", "Octobre", "Novembre", "Décembre"]

    def __init__(self, filename):
        self.__filename = filename
        self.__communes = None
        self.__tagger = None
        self.__stemmer = None
        self.__lexical = None
        self.__loaded = False

    def __load(self):
        if not self.__loaded:
            self.__communes = Communes()
            tagdir = 'treetagger/'
            if sys.platform.startswith('win'):
                tagdir = 'treetagger-win/'
            self.__tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=tagdir, TAGINENC='utf-8',
                                                         TAGOUTENC='utf-8')

            self.__stemmer = FrenchStemmer()
            self.__lexical = []
            files = ['resources/lexical/meteo-facts.csv', 'resources/lexical/meteo-words.csv',
                     'resources/lexical/phenomenes-meteo-franc.csv']
            for filename in files:
                file = open(filename, "r", encoding='utf-8')
                try:
                    reader = csv.reader(file, delimiter="\t", quotechar='"')
                    for row in reader:
                        word = row[0]
                        word = word.strip().lower()
                        if word != "":
                            self.__lexical.append(word)
                            stem = self.__stemmer.stem(word)
                            if word != stem:
                                self.__lexical.append(stem)

                finally:
                    file.close()
            self.__lexical = set(self.__lexical)
            self.__loaded = True

    def html(self):
        html = None
        if os.path.isfile(self.__filename):
            output_file = 'cache/html/' + str(uuid.uuid4()) + '.html'
            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))
            codec = 'utf-8'
            maxpages = 0
            pagenos = None
            html = True
            outfp = open(output_file, 'wb')
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = HTMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams, layoutmode='normal', text_colors={})
            fp = open(self.__filename, 'rb')
            # noinspection PyBroadException
            try:
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages):
                    interpreter.process_page(page)
            except:
                pass
            fp.close()
            device.close()
            outfp.flush()
            outfp.close()
            if os.path.isfile(output_file):
                file = open(output_file, "r", encoding='utf-8')
                html = file.read()
        return html

    def logical(self, template_file=None):

        temple_file = "resources/template.html"
        output_file = 'cache/html/' + str(uuid.uuid4()) + '.html'
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        soup1 = BeautifulSoup(self.html(), 'html5lib')
        elts = soup1.select("div a")
        spans = soup1.select('span[style]')

        soup = BeautifulSoup(open(temple_file, "rb"), 'html5lib')

        body = soup.find('body')
        body = body.find('div')

        template = None
        if os.path.isfile(template_file):
            with open(template_file, 'r') as file:
                template = json.load(file)
        if not template:
            template = {
                'levels': [
                    {'selectors': [".*?font-size:38px.*?"],
                     'tag': 'h1',
                     'level': 1
                     },
                    {'selectors': [".*?font-size:33px.*?", ".*?font-size:21px.*?"],
                     'tag': 'h2',
                     'level': 2
                     },
                    {'selectors': [".*?font-size:17px.*?"],
                     'tag': 'h3',
                     'level': 3
                     },
                    {'selectors': [".*?font-size:14px.*?"],
                     'tag': 'h4',
                     'level': 4
                     },
                    {'selectors': [".*?"],
                     'tag': 'p',
                     'level': None
                     }
                ]
            }

        for i in range(len(spans)):
            span = spans[i]
            style = span['style']
            if 'fusion' in template:
                for fusion in template['fusion']:
                    m1 = False
                    for first in fusion['first']:
                        m1 = m1 or re.match(first, style)
                    if m1:
                        for j in range(i + 1, len(spans)):
                            # for next in span.next_siblings:
                            next = spans[j]
                            m2 = False
                            for second in fusion['second']:
                                m2 = m2 or re.match(second, next['style'])
                            if m2 and len(span.string.strip()) > 0:
                                if len(span.string.strip()) == 1:
                                    span.string = span.string.strip()
                                span.string += next.text
                                next.string = ""
                            else:
                                break

        section_tag = 'section'

        sections = {}
        section = body
        level = 1

        for span in spans:
            text = span.text
            text = re.sub("\\s+", " ", text)
            text = text.strip()
            style = span['style']
            if text != "" and not re.match("\\W+", text):
                for rule in template['levels']:

                    selected = False;
                    for selector in rule['selectors']:
                        selected = selected or re.match(selector, style)

                    if 'exclude' in template:
                        if len(template['exclude']) > 0:
                            for excluded in template['exclude']:
                                selected = selected and not re.match(excluded, style)

                    if selected:
                        if rule['level'] is not None:
                            # print(text)
                            pass
                        if rule['level'] is not None:
                            for l in range(1, rule['level']):
                                if l not in sections:
                                    sections[l] = soup.new_tag(section_tag)
                                    if l == 1:
                                        body.append(sections[l])
                                    else:
                                        sections[l - 1].append(sections[l])
                        if rule['level'] is not None:
                            section = soup.new_tag(section_tag)
                            if rule['level'] == 1:
                                body.append(section)
                            else:
                                sections[rule['level'] - 1].append(section)
                            sections[rule['level']] = section

                        tag = soup.new_tag(rule['tag'])
                        tag.append(text)
                        section.append(tag)
                        break

        return soup.prettify()

    def facts(self, region=None, date=None):
        logical = self.logical(template_file='resources/templates/bulletin-climatique.json')
        soup = BeautifulSoup(logical, 'html5lib')
        return {'facts': self.__extract(soup.find('div'), date=date, region=region)}

    def __noungroups(self, text):
        tags = self.__pos_tags(text)
        chunks = []
        chunk = ""
        for tag in tags:
            if tag[1] not in ["NOM", "ADJ"]:
                if chunk != "":
                    chunks.append(chunk)
                chunk = ""
            else:
                if chunk != "":
                    chunk += " "
                chunk += tag[0]
        if chunk != "":
            chunks.append(chunk)
            chunk = ""
        return chunks

    def __pos_tags(self, text):
        tags = []
        for tag in self.__tagger.TagText(text):
            fields = re.split("\t", tag)
            if len(fields) > 2:
                tags.append(fields)
        return tags



    def __find_facts(self, text):
        facts =set()
        keywords=set()
        groups = self.__noungroups(text)
        for group in groups:
            terms = re.split("\s+", group.strip().lower())
            for term in terms:
                term = term.strip().lower()
                stem = self.__stemmer.stem(term)
                if term in self.__lexical or stem in self.__lexical:
                    keywords.add(term)
                    facts.add(group.strip())
                    break
        return facts,keywords

    def __extract(self, node, parent_title=None, date=None, region=None):
        self.__load()
        records = []
        (year, month, day) = date.split("-")
        fcount = 0
        for child in node.children:
            if not isinstance(child, NavigableString):
                if child.name:
                    if child.name == 'section':
                        section = child

                        header = section.select_one('h1,h2,h3,h4,h5,h6')
                        fact_raw = header.text.strip()
                        title = TextUtils.strip_accents(header.text).lower().strip()

                        description = ""
                        for parag in section.findAll('p'):
                            description += " " + parag.text
                        description = re.sub("\s+", " ", description)
                        description = description.strip()
                        is_fact = (parent_title == 'faits marquants')

                        if is_fact:
                            fcount += 1

                            fact = title

                            extracted_dates = TextUtils.extract_date(fact, context=date)

                            (facts,keywords) = self.__find_facts(extracted_dates['nodate_text'])
                            detected_places = self.__communes.annotate(title + " " + description, context={'region':region})

                            for date_instance in extracted_dates['dates']:
                                fact = WeatherFact()

                                fact.dateIssued = date

                                fact.startDate = date_instance['startDate'] if 'startDate' in date_instance else date_instance['date']
                                fact.endDate = date_instance['endDate'] if'endDate' in  date_instance else date_instance['date']

                                fact.title = fact_raw
                                fact.description = description

                                fact.facts = facts
                                fact.keywords = keywords

                                fact.places = detected_places['places']

                                region_file = "resources/regions/" + TextUtils.normalize(region) + ".json"
                                if os.path.exists(region_file):
                                    with open(region_file) as json_data:
                                        region_object = json.load(json_data)
                                        fact.region = region_object

                                fact.date = {'year': int(year), 'month': PDFDocument.month_names[int(month)],
                                             'day': int(day)}

                                records.append(fact)
                        else:
                            rds = self.__extract(section, parent_title=title, date=date, region=region)
                            if rds:
                                for r in rds:
                                    records.append(r)
        return records


class JSONSerializable(object):
    def __repr__(self):
        return json.dumps(self.__dict__)


class WeatherFact(JSONSerializable):
    def __init__(self):
        super().__init__()
        self.dateIssued = None
        self.startDate = None
        self.endDate = None
        self.date = None

        self.title = None
        self.description = None

        self.facts = None
        self.keywords = None
        self.places = None
        self.region = None
