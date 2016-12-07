import datetime
import re
import unicodedata

import pytz


class TextUtils:
    @staticmethod
    def normalize(text):
        text = re.sub("\\W+", " ", text).strip()
        text = re.sub("\\s+", "-", text).lower()
        return text

    @staticmethod
    def uncamel(text):
        text = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', text)

    @staticmethod
    def datetime(created_at):
        created_at = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
        created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
        return created_at

    @staticmethod
    def strip_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')

    @staticmethod
    def extract_date(text, year=None, month=None, day=None):
        result = []
        new_text = re.sub("\s+", " ", text)
        days = '(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)'
        months = '(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)'

        month_names = {}
        month_names["janvier"] = "01"
        month_names["février"] = "02"
        month_names["fevrier"] = "02"
        month_names["mars"] = "03"
        month_names["avril"] = "04"
        month_names["mai"] = "05"
        month_names["juin"] = "06"
        month_names["juillet"] = "07"
        month_names["août"] = "08"
        month_names["aout"] = "08"
        month_names["septembre"] = "09"
        month_names["octobre"] = "10"
        month_names["novembre"] = "11"
        month_names["décembre"] = "12"
        month_names["decembre"] = "12"
        expressions = [
            ['(((l|d)(a|e|es))|en|au|du)\s*' + days + '?\s*(\d{1,2})\s*' + months, [5, 6]],
        ]
        for expression in expressions:
            matchs = re.findall(expression[0], new_text)
            if matchs:
                for match in matchs:
                    empty = False
                    for index in expression[1]:
                        if match[index] == "":
                            empty = True
                    if not empty:
                        result.append(year + "-" + month_names[match[expression[1][1]]] + "-" + match[expression[1][0]])
            new_text = re.sub(expression[0], " ", new_text)

        expressions = [
            ['((l(a|e|es))|en)?\s*debut\s*d(u|e|es)\s*mois', ["1", "10"]],
            ['((l(a|e|es))|en)?\s*milieu\s*d(u|e|es)\s*mois', ["10", "20"]],
            ['((l(a|e|es))|en)?\s*fin\s*d(u|e|es)\s*mois', ["20", "30"]],
            ['premiere quinzaine', ["1", "15"]],
            ['deuxiemme quinzaine', ["15", "30"]],
            ['premiere decade', ["1", "10"]],
            ['premiere décade', ["1", "10"]],
            ['1ere decade', ["1", "10"]],
            ['1ere décade', ["1", "10"]],
            ['deuxieme decade', ["10", "20"]],
            ['troisieme decade', ["20", "30"]],

        ]
        for expression in expressions:
            matchs = re.findall(expression[0], new_text)
            if matchs:
                for match in matchs:
                    result.append(
                        year + "-" + month + "-" + expression[1][0] + " " + year + "-" + month + "-" + expression[1][1])
            new_text = re.sub(expression[0], " ", new_text)

        expressions = [
            ['entre\s*(les?)?\s*(\d{1,2})(er)?\s*et\s*(les?)?\s*(\d{1,2})(er)?', [1, 4]],
            ['du\s*(\d{1,2})(er)?\s*au\s*(\d{1,2})(er)?', [0, 2]],
        ]
        for expression in expressions:
            matchs = re.findall(expression[0], new_text)
            if matchs:
                for match in matchs:
                    empty = False
                    for index in expression[1]:
                        if match[index] == "":
                            empty = True
                    if not empty:
                        result.append(
                            year + "-" + month + "-" + match[expression[1][0]] + " " + year + "-" + month + "-" + match[
                                expression[1][1]])
            new_text = re.sub(expression[0], " ", new_text)

        expressions = [
            ['(l|d)es?\s*' + days + '?\s*(\d{1,2})(er)?(\s*(et|,)\s*(\d{1,2})(er)?)*', [2, 6]]
        ]
        for expression in expressions:
            matchs = re.findall(expression[0], new_text)
            if matchs:
                for match in matchs:
                    for index in expression[1]:
                        if len(match) > index:
                            if match[index] != "":
                                result.append(year + "-" + month + "-" + match[index])
            new_text = re.sub(expression[0], " ", new_text)

        new_text = re.sub("\s+", " ", new_text)
        new_text = new_text.strip()

        return (result, new_text)
