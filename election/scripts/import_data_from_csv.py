# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('/Users/fmassto/projects/mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import mysite.settings as settings

import datetime
import xlrd

from django.db import transaction
from geofla.models import Commune, RemovedCommuneError, NotYetImportedCommuneError
from election.models import Person, PoliticalParty, Politician, ElectionResultsByCommune, ElectionType, ElectionResultsByCommuneByPolitician, Election, ElectionResultsByCirconscription, ElectionResultsByCirconscriptionByPolitician

#
# NOTE: DOM/TOM results are not yet imported because communes/departement are not defined in geofla models
#

#FOR PRESIDENTIAL ELECTION
POLITICIAN_PARTY = {
    u'SARKOZY': 'UMP',
    u'JOLY': 'ECO',
    u'MÉLENCHON': 'FDG',
    u'POUTOU': 'NPA',
    u'ARTHAUD': 'FO',
    u'BAYROU': 'MOD',
    u'HOLLANDE': 'SOC',
    u'LE PEN': 'FN',
    u'NIHOUS': 'CPNT',
    u'LAGUILLER': 'LO',
    u'VOYNET': 'ECO',
    u'BUFFER': 'PC',
    u'ROYAL': 'SOC',
    u'BESANCENOT': 'LCR',
}

def get_or_create_election(election_date, type_name, tour):
    # create election
    election_type, is_created = ElectionType.objects.get_or_create(name=type_name, tour=tour)
    election, is_created = Election.objects.get_or_create(date=election_date, type=election_type)
    election.save()
    return election

#
# LEGISLATIVE 2007
#

def import_election_2007_legislative(filepath, date, tour, start_row=1):
    election = get_or_create_election(date, 'L', tour)
    with_circonscription = True

    election_mapping = {'registered': 6, 'abstention': 7, 'vote': 9, 'white_or_null': 11, 'valid_vote': 14, 'circonscription': 2}
    commune_mapping = {'commune_code': 4, 'dept_code': 0}
    first_politician_mapping = {'gender': 18,
                                'lastname': 19,
                                'firstname': 20,
                                'party': 21,
                                'vote': 22,
                                'pct_vote': 23}
    col_nb_per_politician = 8

    info_processor = InfoProcessor(commune_mapping, election_mapping, first_politician_mapping, col_nb_per_politician)

    results_builder = ResultBuilder(election, with_circonscription)

    import_data(filepath, excel_row_iterator, info_processor, results_builder, start_row=start_row)

def import_election_2007_legislative_first_tour():
    #filepath = "/Users/fmassot/Downloads/Legislatives 2007 Communes_test.xls"
    filepath = "/Users/fmassot/Downloads/Legislatives 2007 Communes.csv"
    election_date = datetime.datetime(2007,6,10)
    import_election_2007_legislative(filepath, election_date, '1')

def import_election_2007_legislative_second_tour():
    filepath = "/Users/fmassot/Downloads/Leg 07 Com tour 2.csv"
    election_date = datetime.datetime(2007,6,17)
    import_election_2007_legislative(filepath, election_date, '2')


#
# PRESIDENTIAL 2012
#

def import_election_2012_presidential(filepath, date, tour, start_row=1):
    election = get_or_create_election(date, 'P', tour)
    with_circonscription = False

    election_mapping = {'registered': 5, 'abstention': 6, 'vote': 8, 'white_or_null': 10, 'valid_vote': 13}
    commune_mapping = {'commune_code': 3, 'dept_code': 1}
    first_politician_mapping = {'gender': 16,
                                'lastname': 17,
                                'firstname': 18,
                                'vote': 19,
                                'pct_vote': 21}
    col_nb_per_politician = 6

    info_processor = InfoProcessor(commune_mapping, election_mapping, first_politician_mapping, col_nb_per_politician)

    results_builder = ResultBuilder(election, with_circonscription)

    import_data(filepath, excel_row_iterator, info_processor, results_builder, start_row=start_row)

def import_election_2012_presidential_first_tour():
    filepath = "/Users/fmassot/Downloads/b42cded1bcaa5ff6eb1ed40ab4c503d3.csv"
    election_date = datetime.datetime(2012,4,22)
    import_election_2012_presidential(filepath, election_date, '1', start_row=1)

def import_election_2012_presidential_second_tour():
    filepath = "/Users/fmassot/Downloads/b2e5066291a248cad4c2155d8dd05957.csv"
    election_date = datetime.datetime(2012,5,6)
    import_election_2012_presidential(filepath, election_date, '2', start_row=10297)


#
# PRESIDENTIAL 2007
#

def import_election_2007_presidential(filepath, date, tour, start_row=1):
    election = get_or_create_election(date, 'P', tour)
    with_circonscription = False

    election_mapping = {'registered': 4, 'abstention': 5, 'vote': 7, 'white_or_null': 9, 'valid_vote': 12}
    commune_mapping = {'commune_code': 2, 'dept_code': 0}
    first_politician_mapping = {'gender': 15,
                                'lastname': 16,
                                'firstname': 17,
                                'vote': 18,
                                'pct_vote': 20}
    col_nb_per_politician = 6

    info_processor = InfoProcessor(commune_mapping, election_mapping, first_politician_mapping, col_nb_per_politician)

    results_builder = ResultBuilder(election, with_circonscription)

    import_data(filepath, excel_row_iterator, info_processor, results_builder, start_row=start_row)

def import_election_2007_presidential_first_tour():
    filepath = "/Users/fmassot/Downloads/Presidentielle2007parcommunes.csv"
    election_date = datetime.datetime(2007,4,22)
    import_election_2007_presidential(filepath, election_date, '1', start_row=137)

def import_election_2007_presidential_second_tour():
    filepath = "/Users/fmassot/Downloads/Pres 07 communes T2.CSV"
    election_date = datetime.datetime(2007,5,6)
    import_election_2007_presidential(filepath, election_date, '2', start_row=10297)








def excel_row_iterator(filepath, start_row=1, end_row=None):
    wb = xlrd.open_workbook(filepath)
    sh = wb.sheets()[0]
    for i_r in range(start_row, end_row or sh.nrows):
        print "row: ", i_r
        yield sh.row(i_r)

def import_data(filepath, row_iterator, row_info_extractor, row_constructor, start_row=1, end_row=None):
    row_constructor(row_info_extractor(row_iterator(filepath, start_row=start_row)))



class InfoProcessor(object):
    """
    """
    def __init__(self, mapping_commune, mapping_election, mapping_politician, col_nb_by_politician):
        self.mapping_commune = mapping_commune
        self.mapping_election = mapping_election
        self.mapping_politician = mapping_politician
        self.col_nb_by_politician = col_nb_by_politician

    def __call__(self, rows):
        """
        Return a dict with relevant info
        TODO: 
            - remove dependency on excel: ".value" is crappy
        """
        for row in rows:
            row_info = {}
            row_info['election_info'] = dict( (k,row[v].value) for k,v in self.mapping_election.items() )
            row_info['commune'] = dict( (k,row[v].value) for k,v in self.mapping_commune.items() )
            row_info['politicians'] = [ politician for politician in self.politician_it(row) ]
            yield row_info

    def politician_it(self, row):
        politician_id = 0
        start_col = max(self.mapping_politician.values())
        while politician_id + start_col < len(row):
            politician_info = dict( (k, row[col_id + politician_id].value) for k, col_id in self.mapping_politician.items() )
            politician_info['pct_vote'] = "%0.2f"%politician_info['pct_vote']
            
            if '' in politician_info.values():
                break

            politician_id += self.col_nb_by_politician
            yield politician_info

class ResultBuilder(object):
    """
    """
    def __init__(self, election, with_circonscription):
        self.election = election
        if with_circonscription:
            self.zone_result_constructor = ElectionResultsByCirconscription
            self.politician_result_constructor = ElectionResultsByCirconscriptionByPolitician
        else:
            self.zone_result_constructor = ElectionResultsByCommune
            self.politician_result_constructor = ElectionResultsByCommuneByPolitician
        self.with_circonscription = with_circonscription

    @transaction.commit_manually
    def __call__(self, rows_info):
        for row_info in rows_info:
            try:
                try:
                    commune = commune_extractor(row_info['commune'])
                except (RemovedCommuneError, NotYetImportedCommuneError):
                    # in this case, we can't process the data
                    #print "Commune not yet imported, insee code: %s"%row_info['commune']['insee_code']
                    continue
                zone_result = self.zone_result_constructor(commune=commune, election=self.election, **row_info['election_info'])
                zone_result.save()

                for politician_info in row_info['politicians']:
                    # create politician
                    person, is_created = Person.objects.get_or_create(lastname=politician_info['lastname'], firstname=politician_info['firstname'], gender=politician_info['gender'])
                    person.save()
                    if politician_info.has_key('party'): 
                        acronym = politician_info['party']
                    elif POLITICIAN_PARTY.has_key(politician_info['lastname']):
                        acronym = POLITICIAN_PARTY[politician_info['lastname']]
                    else:
                        acronym = ''

                    party, is_created = PoliticalParty.objects.get_or_create(acronym=acronym)
                    party.save()
                    politician, is_created = Politician.objects.get_or_create(person=person, party=party)
                    # TODO: update end date of his/her political life
                    if not politician.start_date or politician.start_date.toordinal() > self.election.date.toordinal():
                        politician.start_date = self.election.date
                    politician.save()

                    politician_result = self.politician_result_constructor(commune=commune, election=self.election, vote=politician_info['vote'], pct_vote=politician_info['pct_vote'])
                    politician_result.politician = politician
                    if self.with_circonscription:
                        politician_result.circonscription = circonscription['election_info']['circonscription']
                    politician_result.save()

                transaction.commit()

            except Exception, e:
                transaction.rollback()
                raise

def commune_extractor(info_commune):
    try:
        insee_code = '%02d%03d'%(info_commune['dept_code'], info_commune['commune_code'])
    except TypeError:
        #the dept_code is a string not an integer: for corse, DOM/TOM
        insee_code = '%s%03d'%(info_commune['dept_code'], info_commune['commune_code'])
    real_insee_code = Commune.get_insee_code(insee_code)
    info_commune['insee_code'] = real_insee_code
    return Commune.objects.get(insee_code=insee_code)
      

if __name__ == '__main__':
    #ElectionResultsByCirconscription.objects.all().delete()
    #ElectionResultsByCirconscriptionByPolitician.objects.all().delete()
    #import_election_2007_legislative_first_tour()

    #import_election_2007_legislative_second_tour()

    #import_election_2007_legislative_first_tour()
    #import_election_2007_legislative_second_tour()

    #import_election_2012_presidential_second_tour()

    import_election_2007_presidential_second_tour()
