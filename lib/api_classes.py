#
# TTG GLOBAL  - 10/29/2022  
#
import json
import requests

class CNEAPIBase(object):
    def __init__(self):
        self.url = None
        self.headers = None
        self.payload = None
        self.headers = None
        self.operation = None

class CNEResults(CNEAPIBase):
    def __init__(self):
        CNEAPIBase.__init__(self)
        self.data_response = None
        self.est = None
        self.mun = None
        self.par = None
        self.cod = None
        self.mes = None
        self.results = []

    def Build_url(self, base_url, format, elect_id, cargo, codigo_centro, mesa):
        self.est, self.mun, self.par, self.centro = CNEResults.split_codigo_centro(codigo_centro)
        self.cod = codigo_centro
        self.mes = mesa
        url = base_url + format.format(str(cargo), str(elect_id), str(self.est), str(self.mun), str(self.par), str(self.cod), str(self.mes))
        self.url = url

    def Build_headers(self, content_type, headers):
        self.headers = { content_type: headers }

    def Request(self):
            self.data_response  = requests.request(self.operation, self.url, headers=self.headers)
            if self.data_response.ok == True:
                res=json.loads(self.data_response.text)
                for d in res['data']:
                    dr = CNEDetailedResults()
                    dr.from_json(d)
                    self.results.append(dr)
            return self.data_response.ok

    def Request_results(self, wconfig, codigo_centro, mesa):
        #
        # empty the array
        # 
        self.results = []
        #
        # fill the object   
        #
        self.Build_url(wconfig['base_url'], wconfig['format_url'], wconfig['cod_event_id'], wconfig['cod_cargo'], codigo_centro, mesa)
        self.Build_headers(wconfig['content_type'], wconfig['headers'])
        self.operation = wconfig['operation']
        status = self.Request()
        if status == False:
            raise Exception("CNE Data Request failed. Message: HTTP %i - %s, Message %s" % (self.data_response.status_code, self.data_response.reason, self.data_response.text))

    @staticmethod
    def split_codigo_centro(codigo_centro):
        cc_str = str(codigo_centro)
        ln = len(cc_str)
        centro = int(cc_str[-3:])
        parroquia = int(cc_str[-5:-3])
        municipio = int(cc_str[-7:-5])
        if ln > 8:
            estado = int(cc_str[-9,-7])
        else:
            estado = int(cc_str[-8:-7])
        return estado, municipio, parroquia, centro


class CNEDetailedResults(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.total_votes = None
        self.parties = []

    def from_json(self, json):
        self.id = json['id']
        self.name = json['name']
        self.total_votes = json['votos']
        for p in json['partidos']:
            party = CNEDetailedParty(p['name'], p['votes'])
            self.parties.append(party)

class CNEDetailedParty (object):
    def __init__(self, name, votes):
        self.name = name
        self.votes = votes

    def from_json(self, json):
        self.name = json['name']
        self.votes = json['votes']

