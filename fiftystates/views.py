from models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect

def index(request):
    states = State.objects.all()
    return render_to_response('fiftystates/index.html',
                              {'states': states})

def state_index(request, state):
    state = get_object_or_404(State, abbreviation=state)
    recent_bills = state.bill_set.all()[:5]

    new_bills_feed_url = urllib.quote("/feeds/new_bills/%s" % (
            state.abbreviation))

    return render_to_response(
        'fiftystates/state_index.html',
        {'state': state,
         'recent_bills': recent_bills,
         'new_bills_feed_url': new_bills_feed_url})

def bill(request, state, session, chamber, bill_id):
    bill = get_object_or_404(Bill,
                             state__abbreviation=state,
                             session__name=session,
                             chamber=chamber, bill_id=bill_id)

    actions_feed_url = urllib.quote("/feeds/actions/%s/%s/%s/%s" % (
            bill.state.abbreviation, bill.session.name,
            bill.chamber, bill.bill_id))
    sponsors_feed_url = urllib.quote(
        "/feeds/bill_sponsors/%s/%s/%s/%s" % (
            bill.state.abbreviation, bill.session.name,
            bill.chamber, bill.bill_id))

    return render_to_response('fiftystates/bill.html',
                              {'bill': bill,
                               'actions_feed_url': actions_feed_url,
                               'sponsors_feed_url': sponsors_feed_url})

def legislator(request, state, id):
    legislator = get_object_or_404(Legislator, pk=id)

    sponsorships_feed_url = urllib.quote(
        "/feeds/sponsorships/%s/%s" % (
            legislator.state.abbreviation, legislator.pk))

    return render_to_response(
        'fiftystates/legislator.html',
        {'legislator': legislator,
         'sponsorships_feed_url': sponsorships_feed_url})

