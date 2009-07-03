from models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic import list_detail

def index(request):
    states = State.objects.order_by('name').all()

    return render_to_response('fiftystates/index.html',
                              {'states': states})

def state_index(request, state):
    state = get_object_or_404(State, abbreviation=state)

    recent_bills = state.bill_set.all()[:20]

    new_bills_feed_url = urllib.quote("/feeds/new_bills/%s" % (
            state.abbreviation))

    return render_to_response(
        'fiftystates/state_index.html',
        {'state': state,
         'recent_bills': recent_bills,
         'new_bills_feed_url': new_bills_feed_url})

def bill(request, state, session, chamber, bill_id):
    try:
        bill = Bill.objects.select_related('state', 'session').get(
            state__abbreviation=state,
            session__name=session,
            chamber=chamber,
            bill_id=bill_id)
    except Bill.DoesNotExist:
        raise Http404

    actions = bill.action_set.all()
    sponsors = bill.sponsor_set.select_related('legislator').order_by('legislator__full_name')
    versions = bill.version_set.all().order_by('-id')
    votes = bill.vote_set.all()

    actions_feed_url = urllib.quote("/feeds/actions/%s/%s/%s/%s" % (
            bill.state.abbreviation, bill.session.name,
            bill.chamber, bill.bill_id))
    sponsors_feed_url = urllib.quote(
        "/feeds/bill_sponsors/%s/%s/%s/%s" % (
            bill.state.abbreviation, bill.session.name,
            bill.chamber, bill.bill_id))

    return render_to_response('fiftystates/bill.html',
                              {'state': bill.state,
                               'bill': bill,
                               'actions': actions,
                               'sponsors': sponsors,
                               'versions': versions,
                               'votes': votes,
                               'actions_feed_url': actions_feed_url,
                               'sponsors_feed_url': sponsors_feed_url})

def legislator(request, state, id):
    try:
        legislator = Legislator.objects.select_related(
            'state').get(state__abbreviation=state, pk=id)
    except Legislator.DoesNotExist:
        raise Http404

    roles = legislator.role_set.order_by('-session__start_year').all()
    votes = legislator.specificvote_set.select_related('vote').order_by('-vote__date').all()[:10]
    sponsorships = legislator.sponsor_set.select_related('bill').order_by('-id').all()[:10]

    sponsorships_feed_url = urllib.quote(
        "/feeds/sponsorships/%s/%s" % (
            legislator.state.abbreviation, legislator.pk))

    return render_to_response(
        'fiftystates/legislator.html',
        {'state': legislator.state,
         'legislator': legislator,
         'roles': roles,
         'sponsorships': sponsorships,
         'votes': votes,
         'sponsorships_feed_url': sponsorships_feed_url})

def district(request, state, chamber, name):
    state = get_object_or_404(State, abbreviation=state)
    roles = Role.objects.select_related('legislator').filter(
        state=state,
        chamber=chamber,
        district=name).order_by('-session__start_year')

    if len(roles) == 0:
        raise Http404

    chamber_name = roles[0].chamber_name
    title = roles[0].title

    return render_to_response('fiftystates/district.html',
                              {'state': state,
                               'district': name,
                               'chamber_name': chamber_name,
                               'title': title,
                               'roles': roles})

def legislators_index(request, state, chamber):
    state = get_object_or_404(State, abbreviation=state)
    session = state.current_session

    roles = Role.objects.select_related('legislator').filter(
        state=state, session=session, chamber=chamber).order_by(
        'legislator__full_name')
    if len(roles) == 0:
        raise Http404

    chamber_name = roles[0].chamber_name
    title = roles[0].title

    return render_to_response('fiftystates/legislators_index.html',
                              {'state': state,
                               'session': session,
                               'chamber_name': chamber_name,
                               'title': title,
                               'roles': roles})

def bills_index(request, state):
    state = get_object_or_404(State, abbreviation=state)

    upper_bills = state.bill_set.filter(
        session=state.current_session,
        chamber='upper')[:10]
    lower_bills = state.bill_set.filter(
        session=state.current_session,
        chamber='lower')[:10]
    upper_count = state.bill_set.filter(
        session=state.current_session,
        chamber='upper').count() - 10
    lower_count = state.bill_set.filter(
        session=state.current_session,
        chamber='lower').count() - 10

    return render_to_response('fiftystates/bills_index.html',
                              {'state': state,
                               'upper_bills': upper_bills,
                               'lower_bills': lower_bills,
                               'upper_count': upper_count,
                               'lower_count': lower_count})

def bills_chamber_index(request, state, chamber):
    state = get_object_or_404(State, abbreviation=state)
    chamber_name = state.chamber_name(chamber)

    return list_detail.object_list(
        request,
        queryset=state.bill_set.filter(chamber=chamber),
        template_name='fiftystates/bills_chamber_index.html',
        template_object_name='bill',
        paginate_by=30,
        extra_context={'state': state,
                       'chamber_name': chamber_name})
