# -*- coding: utf-8 -*-

import mysite.settings as settings
from django.contrib.gis.db import models


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

ELECTION_TYPES = (
    ('L', 'Legislative'),
    ('P', 'Presidential'),
)

TOUR_TYPES = (
    ( '1', 'First tour'),
    ( '2', 'Second tour'),
)


class Person(models.Model):
    lastname = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200) 
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        unique_together = ('lastname', 'firstname', 'gender',)

class PoliticalParty(models.Model):
    acronym = models.CharField(max_length=10, unique=True)
    #name = models.CharField(max_length=200)
    # add a description, begin date and end date

class Politician(models.Model):
    person = models.ForeignKey("Person")
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    party = models.ForeignKey("PoliticalParty")

class ElectionType(models.Model):
    name = models.CharField(max_length=1, choices=ELECTION_TYPES)
    tour = models.CharField(max_length=1, choices=TOUR_TYPES)

class Election(models.Model):
    type = models.ForeignKey("ElectionType")
    date = models.DateField()
    class Meta:
        unique_together = ('type', 'date',)

class ElectionResultsByCommune(models.Model):
    election = models.ForeignKey("Election")
    commune = models.ForeignKey("geofla.Commune")

    registered = models.PositiveIntegerField()
    abstention = models.PositiveIntegerField()
    vote = models.PositiveIntegerField()
    white_or_null = models.PositiveIntegerField()
    valid_vote = models.PositiveIntegerField()

    class Meta:
        unique_together = ('election', 'commune',)

class ElectionResultsByCirconscription(models.Model):
    """
    TODO: remove circonscription from this model and create a Circonscription model
    defined by the commune and the circonscription number. But before doing that, make
    sure that a circonscription can be defined uniquely by these two variables. 
    For the moment, not a high priority because we don't have geometries of circoncription
    """
    election = models.ForeignKey("Election")
    commune = models.ForeignKey("geofla.Commune")

    registered = models.PositiveIntegerField()
    abstention = models.PositiveIntegerField()
    vote = models.PositiveIntegerField()
    white_or_null = models.PositiveIntegerField()
    valid_vote = models.PositiveIntegerField()
    circonscription = models.PositiveIntegerField()

    class Meta:
        unique_together = ('election', 'commune', 'circonscription')

class ElectionResultsByCommuneByPolitician(models.Model):
    election = models.ForeignKey("Election")
    commune = models.ForeignKey("geofla.Commune")
    politician = models.ForeignKey("Politician")

    vote = models.PositiveIntegerField()
    pct_vote = models.DecimalField(max_digits=5, decimal_places=2) #valid vote

    class Meta:
        unique_together = ('election', 'commune', 'politician',)
    
class ElectionResultsByCirconscriptionByPolitician(models.Model):
    election = models.ForeignKey("Election")
    commune = models.ForeignKey("geofla.Commune")
    politician = models.ForeignKey("Politician")
    circonscription = models.PositiveIntegerField()

    vote = models.PositiveIntegerField()
    pct_vote = models.DecimalField(max_digits=5, decimal_places=2) #valid vote

    class Meta:
        unique_together = ('election', 'commune', 'politician', 'circonscription')
