# -*- coding: utf-8 -*-

from exceptions import Exception
import mysite.settings as settings
from django.contrib.gis.db import models


#TODO: remove these errors from this module
class ChangedCommuneError(Exception):
    def __init__(self, old_insee_code, new_insee_code):
        message = "Insee code of this commune was change from %s to %s"%(old_insee_code, new_insee_code)
        Exception.__init__(self, message)

class RemovedCommuneError(Exception):
    def __init__(self, insee_code, year):
        message = "The commune with insee code %s was removed in %s"%(insee_code, year)
        Exception.__init__(self, message)

class NotYetImportedCommuneError(Exception):
    def __init__(self, insee_code):
        message = "This commune with insee code %s has not been imported yet"%(insee_code)
        Exception.__init__(self, message)

class Canton(models.Model):
    code = models.IntegerField() #not unique
    code_chf = models.CharField(max_length=3)
    nom_chf = models.CharField(max_length=200)
    code_arr = models.CharField(max_length=2)
    code_dept = models.CharField(max_length=2) #two numbers
    code_reg = models.CharField(max_length=2)

    geom = models.MultiPolygonField(srid=settings.SRID)
    objects = models.GeoManager()

    def __unicode__(self):
        return unicode(self.code)

class Department(models.Model):
    name = models.CharField(max_length=200) #set to unique ?
    code = models.CharField(max_length=3, unique=True) 

    geom = models.MultiPolygonField(srid=settings.SRID, unique=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return unicode(self.code)

class Region(models.Model):
    name = models.CharField(max_length=200)

class Commune(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=5) #insee code per department, make a foreign key to department
    insee_code = models.CharField(max_length=5, unique=True)
    state = models.CharField(max_length=200) #add documentation, not obvious

    geom = models.MultiPolygonField(srid=settings.SRID, unique=True)
    objects = models.GeoManager()

    @classmethod
    def get_insee_code(kls, insee_code):
        """
        TODO: remove this crappy code and define correctly commune available at a given moement, make the link between communes which have insee code changes
        """
        if insee_code == "26383":
            #insee code seems to have change recently for this commune
            insee_code = "26020"
        elif insee_code == "55227":
            #same as above
            insee_code = "54602"
        elif insee_code =="88034":
            #same as above
            insee_code = "88106"
        elif insee_code in ["59540", "59248"]:
            #attached to dunkerque in 2010
            raise RemovedCommuneError(insee_code, 2010)
        elif insee_code in ["21551", "61022", "81107"]:
            #these communes were removed in 2009/2010/2007
            raise RemovedCommuneError(insee_code, 2010)
        elif insee_code in ["01003"]:
            raise RemovedCommuneError(insee_code, 1974)
        elif insee_code in ["52033", "52124", "52266", "52278", "52465"]:
            #communes added in 2012
            raise NotYetImportedCommuneError(insee_code)
        elif insee_code[:2] in ["ZA", "ZB", "ZC", "ZD", "ZM", "ZN", "ZP", "ZS", "ZW", "ZX", "ZZ"]:
            #DOM/TOM results are not imported
            raise NotYetImportedCommuneError(insee_code)
        return insee_code


def get_commune(dept_code, commune_code):
    try:
        insee_code = '%02d%03d'%(dept_code, commune_code)
    except TypeError:
        #the dept_code is a string not an integer: for corse, DOM/TOM
        insee_code = '%s%03d'%(dept_code, commune_code)
    real_insee_code = Commune.get_insee_code(insee_code)
    return Commune.objects.get(insee_code=real_insee_code)
 

