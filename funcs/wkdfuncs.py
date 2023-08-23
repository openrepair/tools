import os
import requests


class wikidataBaseApI(object):

    token = None
    urlbase = None

    def __init__(self):

        if 'WIKIDATA_TOKEN' in os.environ:
            self.token = os.environ['WIKIDATA_TOKEN']
        else:
            print('ERROR! WIKI OAUTH TOKEN NOT FOUND!')
            exit()

    def get_headers(self, oauth=True):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ORDS Tools/1.0'
        }
        if oauth:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return headers

    def fetch(self, url, payload):
        headers = self.get_headers()
        try:
            return requests.request("GET", url, headers=headers, params=payload)
        except Exception as error:
            print("Exception: {}".format(error))
        return False


class wikidataRestApi(wikidataBaseApI):

    def __init__(self):
        super().__init__()

        if 'WIKIDATA_URL_RESTAPI' in os.environ:
            self.urlbase = os.environ['WIKIDATA_URL_RESTAPI']
        else:
            print('ERROR! REST API BASE URL NOT FOUND!')
            exit()

    def fetch_fields(self, key):
        try:
            payload = {
                '_fields': 'type,labels,descriptions,aliases,statements,sitelinks'}
            url = "{}/entities/items/{}".format(self.urlbase, key)
            return self.fetch(url, payload)
        except Exception as error:
            print("Exception: {}".format(error))
        return False

    def fetch_statement(self, ikey, skey):
        payload = {'property': '{}'.format(skey)}
        url = "{}/entities/items/{}/statements".format(self.urlbase, ikey)
        return self.fetch(url, payload)


# https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
# https://query.wikidata.org/querybuilder/?uselang=en
class wikidataSparqlAPI(wikidataBaseApI):

    def __init__(self):
        super().__init__()

        if 'WIKIDATA_URL_SPARQL' in os.environ:
            self.urlbase = os.environ['WIKIDATA_URL_SPARQL']
        else:
            print('ERROR! SPARQL API BASE URL NOT FOUND!')
            exit()

    def fetch_subclasses(self, wdkey):
        try:
            qry = """
            SELECT DISTINCT ?item
            WHERE {{
            {{ ?item wdt:P279? wd:{0} . }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """.format(wdkey)
            payload = {'query': qry, 'format': 'json'}
            response = self.fetch(self.urlbase, payload)
        except Exception as error:
            print("Exception: {}".format(error))
        finally:
            return response

    def foo(self):
        pass
        """SELECT ?category ?categoryLabel
        WHERE {
        ?category wdt:P31 wd:Q4167836 ; # Select items that are instances of categories
                    rdfs:label ?categoryLabel . # Retrieve the category's label

        FILTER(lang(?categoryLabel) = "en" && CONTAINS(lcase(?categoryLabel), "electrical"))
        }"""
