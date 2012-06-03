# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('/Users/fmassto/projects/mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import mysite.settings as settings

import datetime
import xlrd

from election.models import Election
from election.utils import get_or_create_election, InfoProcessor, ResultBuilder

#
# NOTE: DOM/TOM results are not yet imported because communes/departement are not defined in geofla models
#

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
    import_election_2007_presidential(filepath, election_date, '2', start_row=137)


def excel_row_iterator(filepath, start_row=1, end_row=None):
    wb = xlrd.open_workbook(filepath)
    sh = wb.sheets()[0]
    for i_r in range(start_row, end_row or sh.nrows):
        print "row: ", i_r
        yield sh.row(i_r)

def import_data(filepath, row_iterator, row_info_extractor, row_constructor, start_row=1, end_row=None):
    row_constructor(row_info_extractor(row_iterator(filepath, start_row=start_row)))

if __name__ == '__main__':
    #import_election_2007_legislative_first_tour()
    #import_election_2007_legislative_second_tour()

    #import_election_2012_presidential_first_tour()
    #import_election_2012_presidential_second_tour()

    import_election_2007_presidential_first_tour()
    #import_election_2007_presidential_second_tour()
