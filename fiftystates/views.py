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

    return render_to_response('fiftystates/state_index.html',
                              {'state': state,
                               'recent_bills': recent_bills})

def bill(request, state, session, chamber, bill_id):
    bill = get_object_or_404(Bill,
                             state__abbreviation=state,
                             session__name=session,
                             chamber=chamber, bill_id=bill_id)

    return render_to_response('fiftystates/bill.html',
                              {'bill': bill})

def legislator(request, state, id):
    legislator = get_object_or_404(Legislator, pk=id)

    return render_to_response('fiftystates/legislator.html',
                              {'legislator': legislator})

