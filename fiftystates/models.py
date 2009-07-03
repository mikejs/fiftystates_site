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

    @property
    def current_session(self):
        # This should be provided by the state parsers...
        session = self.session_set.order_by('-start_year')[0]
        if session.parent:
            return session.parent
        return session

    def chamber_name(self, chamber):
        if chamber == 'upper':
            return self.upper_chamber_name
        else:
            return self.lower_chamber_name

class Session(models.Model):
    state = models.ForeignKey(State)
    parent = models.ForeignKey('self', blank=True, null=True)
    name = models.CharField(max_length=50, db_index=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s: %s" % (self.state.name, self.name)

class Legislator(models.Model):
    state = models.ForeignKey(State)
    full_name = models.CharField(max_length=50, db_index=True)
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
    chamber = models.CharField(max_length=5, db_index=True)
    district = models.CharField(max_length=20, db_index=True)
    session = models.ForeignKey(Session)

    @property
    def title(self):
        if self.chamber == 'upper':
            return self.state.upper_chamber_title
        else:
            return self.state.lower_chamber_title

    @property
    def chamber_name(self):
        if self.chamber == 'upper':
            return self.state.upper_chamber_name
        else:
            return self.state.lower_chamber_name

    @property
    def term(self):
        start_year = self.session.start_year
        end_year = self.session.end_year

        if start_year != end_year:
            return "%d-%d" % (start_year, end_year)
        else:
            return str(start_year)

class Bill(models.Model):
    state = models.ForeignKey(State)
    session = models.ForeignKey(Session)
    chamber = models.CharField(max_length=5, db_index=True)
    bill_id = models.CharField(max_length=30, db_index=True)
    official_title = models.TextField()
    short_title = models.TextField(blank=True)
    last_action = models.DateTimeField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

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
    type = models.CharField(max_length=30, db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)

class Version(models.Model):
    bill = models.ForeignKey(Bill)
    name = models.CharField(max_length=150, db_index=True)
    url = models.URLField(db_index=True)

class Action(models.Model):
    bill = models.ForeignKey(Bill)
    date = models.DateTimeField(db_index=True)
    actor = models.CharField(max_length=50, db_index=True)
    action = models.CharField(max_length=150, db_index=True)

    class Meta:
        ordering = ('-date',)

class Vote(models.Model):
    bill = models.ForeignKey(Bill)
    date = models.DateTimeField(db_index=True)
    motion = models.TextField()
    passed = models.BooleanField()
    yes_count = models.PositiveIntegerField(blank=True, null=True)
    no_count = models.PositiveIntegerField(blank=True, null=True)
    other_count = models.PositiveIntegerField(blank=True, null=True)

class SpecificVote(models.Model):
    vote = models.ForeignKey(Vote)
    legislator = models.ForeignKey(Legislator)
    type = models.CharField(max_length=10, db_index=True)
