from models import *
from feeds import *
from django.conf.urls.defaults import *
from django.views.generic import list_detail

feeds = {
    'new_bills' : NewBills,
    'actions': Actions,
    'bill_sponsors': BillSponsors,
    'sponsorships': Sponsorships,
    }

state_info = {
    'queryset': State.objects.all(),
    'template_name': 'fiftystates/index.html',
    'template_object_name': 'state',
    }

urlpatterns = patterns('fiftystates.views',
    (r'^$', 'index'),
    (r'^(?P<state>[a-zA-Z]{2,2})/$', 'state_index'),
    (r'^(?P<state>[a-zA-Z]{2,2})/bill/(?P<session>.+)/(?P<chamber>upper|lower)/(?P<bill_id>.+)/$', 'bill'),
    (r'^(?P<state>[a-zA-Z]{2,2})/legislator/(?P<id>\d+)/', 'legislator'),
    (r'^(?P<state>[a-zA-Z]{2,2})/district/(?P<chamber>upper|lower)/(?P<name>.+)/$', 'district'),
    (r'^(?P<state>[a-zA-Z]{2,2})/bills/(?P<chamber>upper|lower)/$', 'bills_chamber_index'),
    (r'^(?P<state>[a-zA-Z]{2,2})/bills/$', 'bills_index'),
    (r'^(?P<state>[a-zA-Z]{2,2})/legislators/(?P<chamber>upper|lower)/$', 'legislators_index'),
    #(r'^(?P<state>[a-zA-Z]{2,2})/search', 'search'),
)

urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)
