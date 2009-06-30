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
    #(r'^(?P<state>[a-zA-Z]{2,2})/search', 'search'),
)

urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)
