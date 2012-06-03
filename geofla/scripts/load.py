# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('/Users/fmassto/projects/mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import mysite.settings as settings

from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.utils import LayerMapping
from geofla.models import Canton, Commune, Department, Region

canton_mapping = {
        'code': 'CODE_CANT',
        'geom': 'MULTIPOLYGON',
        'code_chf': 'CODE_CHF',
        'nom_chf': 'NOM_CHF',
        'code_arr': 'CODE_ARR',
        'code_dept': 'CODE_DEPT',
        'code_reg': 'CODE_REG'}

commune_mapping = {
        'code': 'CODE_COMM',
        'insee_code': 'INSEE_COM',
        'name': 'NOM_COMM',
        'geom': 'MULTIPOLYGON'}

department_mapping = {
        'code': 'CODE_DEPT',
        'name': 'NOM_DEPT',
        'geom': 'MULTIPOLYGON'
        }

def load_adminzones():
    lm = LayerMapping(Canton, '/Users/fmassot/Downloads/GEOFLA_1-1_SHP_LAMB93_FR-ED111/CANTONS/CANTON.SHP', canton_mapping)
    lm.save(strict=True, verbose=True)

    lm = LayerMapping(Commune, '/Users/fmassot/Downloads/GEOFLA_1-1_SHP_LAMB93_FR-ED111/COMMUNES/COMMUNE.SHP', commune_mapping)
    lm.save(strict=True, verbose=True)

    lm = LayerMapping(Department, '/Users/fmassot/Downloads/GEOFLA_1-1_SHP_LAMB93_FR-ED111/DEPARTEMENTS/DEPARTEMENT.SHP', department_mapping)

    # no region at the moment
    #lm = LayerMapping(Region, '/Users/fmassot/Downloads/GEOFLA_1-1_SHP_LAMB93_FR-ED111/DEPARTEMENTS/DEPARTEMENT.SHP', department_mapping)

def add_paris_and_marseille_commune():
    arr_paris = Commune.objects.filter(name__contains="ARRONDISSEMENT").filter(name__contains="PARIS").values_list('geom', flat=True) 
    paris_geom = arr_paris[0]
    for poly in arr_paris[1:]:
       paris_geom = paris_geom.union(poly)

    paris = Commune(name="PARIS", insee_code="75056", geom=MultiPolygon(paris_geom), code="056", state="")
    paris.save()

    arr_marseille = Commune.objects.filter(name__contains="ARRONDISSEMENT").filter(name__contains="MARSEILLE").values_list('geom', flat=True) 

    marseille_geom = arr_marseille[0]
    for poly in arr_marseille[1:]:
        marseille_geom = marseille_geom.union(poly)

    marseille = Commune(name="MARSEILLE", insee_code="13055", geom=MultiPolygon(marseille_geom), code="055", state="")
    marseille.save()


def add_commune(name, insee_code):
    arrs = Commune.objects.filter(name__contains="ARRONDISSEMENT").filter(name__contains=name).values_list('geom', flat=True) 

    geom = arrs[0]
    for poly in arrs[1:]:
        geom = geom.union(poly)

    city = Commune(name=name, insee_code=insee_code, geom=MultiPolygon(geom), code=insee_code[2:], state="")
    city.save()

if __name__ == '__main__':
    add_commune("LYON", "69123")
    add_commune("MARSEILLE", "13055")
    add_commune("PARIS", "75056")

    #load_adminzones()





