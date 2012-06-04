# -*- coding: utf-8 -*-

from django.db import transaction

from election.models import Person, PoliticalParty, Politician, ElectionResultsByCommune, ElectionType, ElectionResultsByCommuneByPolitician, Election, ElectionResultsByCirconscription, ElectionResultsByCirconscriptionByPolitician

from geofla.models import Commune, RemovedCommuneError, NotYetImportedCommuneError 

def get_or_create_election(election_date, type_name, tour):
    # create election
    election_type, is_created = ElectionType.objects.get_or_create(name=type_name, tour=tour)
    election, is_created = Election.objects.get_or_create(date=election_date, type=election_type)
    election.save()
    return election

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
                    commune = get_commune(row_info['commune']['dept_code'], row_info['commune']['dept_code'])
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


