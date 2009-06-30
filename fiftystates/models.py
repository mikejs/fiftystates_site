from django.db import models
import urllib

class State(models.Model):
    name = models.CharField(max_length=25)
    abbreviation = models.CharField(max_length=2)
    legislature_name = models.CharField(max_length=50)
    upper_chamber_name = models.CharField(max_length=50)
    lower_chamber_name = models.CharField(max_length=50)
    upper_chamber_title = models.CharField(max_length=50)
    lower_chamber_title = models.CharField(max_length=50)
    upper_chamber_term = models.PositiveIntegerField()
    lower_chamber_term = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return urllib.quote('/%s/' % self.abbreviation)

class Session(models.Model):
    state = models.ForeignKey(State)
    parent = models.ForeignKey('self', blank=True, null=True)
    name = models.CharField(max_length=50)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s: %s" % (self.state.name, self.name)

class Legislator(models.Model):
    state = models.ForeignKey(State)
    full_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=15)
    middle_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=15)
    suffix = models.CharField(max_length=5, blank=True)
    party = models.CharField(max_length=20, blank=True)

    def get_absolute_url(self):
        return urllib.quote("/%s/legislator/%s/" % (
                self.state.abbreviation,
                self.id))

    def __unicode__(self):
        return "%s %s" % (self.state.name, self.full_name)
    
class Role(models.Model):
    legislator = models.ForeignKey(Legislator)
    state = models.ForeignKey(State)
    chamber = models.CharField(max_length=5)
    district = models.CharField(max_length=20)
    session = models.ForeignKey(Session)

class Bill(models.Model):
    state = models.ForeignKey(State)
    session = models.ForeignKey(Session)
    chamber = models.CharField(max_length=5)
    bill_id = models.CharField(max_length=15)
    official_title = models.TextField()
    short_title = models.TextField(blank=True)
    last_action = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-last_action',)
    
    @property
    def title(self):
        return self.short_title or self.official_title
    
    def __unicode__(self):
        return "%s %s" % (self.session, self.bill_id)

    def get_absolute_url(self):
        return urllib.quote("/%s/bill/%s/%s/%s/" % (
                self.state.abbreviation,
                self.session.name,
                self.chamber,
                self.bill_id))

class Sponsor(models.Model):
    bill = models.ForeignKey(Bill)
    legislator = models.ForeignKey(Legislator)
    type = models.CharField(max_length=15)

class Version(models.Model):
    bill = models.ForeignKey(Bill)
    name = models.TextField()
    url = models.URLField()

class Action(models.Model):
    bill = models.ForeignKey(Bill)
    date = models.DateTimeField()
    actor = models.CharField(max_length=15)
    action = models.TextField()

    class Meta:
        ordering = ('-date',)

class Vote(models.Model):
    bill = models.ForeignKey(Bill)
    date = models.DateField()
    motion = models.TextField()
    passed = models.BooleanField()
    yes_count = models.PositiveIntegerField(blank=True, null=True)
    no_count = models.PositiveIntegerField(blank=True, null=True)
    other_count = models.PositiveIntegerField(blank=True, null=True)

class SpecificVote(models.Model):
    vote = models.ForeignKey(Vote)
    legislator = models.ForeignKey(Legislator)
    type = models.CharField(max_length=10)
