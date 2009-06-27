from django.core.management.base import BaseCommand
from fiftystates_site.fiftystates.models import *
import sys, os, re, glob, datetime
try:
    import json
except:
    import simplejson as json

class Command(BaseCommand):
    def handle(self, *args, **options):
        assert len(args) >= 2

        data_dir = args[0]
#        sub_dirs = glob.glob(os.path.join(data_dir, '*/'))
        sub_dirs = map(lambda s: os.path.join(data_dir, s),
                       args[1:])

        for dir in sub_dirs:
            with open(os.path.join(dir, 'state_metadata.json')) as f:
                metadata = json.load(f)

            try:
                state = State.objects.get(
                    abbreviation__iexact=metadata['state'])
            except State.DoesNotExist:
                state = State(abbreviation=metadata['state'])

            state.name = metadata['state_name']
            state.legislature_name = metadata['legislature_name']
            state.upper_chamber_name = metadata['upper_chamber_name']
            state.lower_chamber_name = metadata['lower_chamber_name']
            state.upper_chamber_title = metadata['upper_title']
            state.lower_chamber_title = metadata['lower_title']
            state.upper_chamber_term = metadata['upper_term']
            state.lower_chamber_term = metadata['lower_term']
            state.save()

            for (session_name, details) in metadata['session_details'].items():
                try:
                    session = state.session_set.get(
                        name=session_name)
                except:
                    session = Session(state=state, name=session_name)

                session.start_year = details['years'][0]
                session.end_year = details['years'][-1]
                session.save()

                for sub in details['sub_sessions']:
                    try:
                        sub_session = state.session_set.get(
                            name=sub)
                    except Session.DoesNotExist:
                        sub_session = Session(state=state,
                                              name=sub)

                    sub_session.parent = session
                    sub_session.start_year = session.start_year
                    sub_session.end_year = session.end_year
                    sub_session.save()

            for name in glob.glob(os.path.join(
                    dir, 'legislators', '*.json')):
                with open(name) as f:
                    data = json.load(f)

                self.import_legislator(data, state)

            for name in glob.glob(os.path.join(
                    dir, 'bills', '*.json')):
                with open(name) as f:
                    data = json.load(f)

                self.import_bill(data, state)

    def import_bill(self, data, state):
        session = state.session_set.get(name=data['session'])
        
        try:
            bill = state.bill_set.get(bill_id=data['bill_id'],
                                      session=session)
        except Bill.DoesNotExist:
            bill = Bill(state=state, bill_id=data['bill_id'],
                        session=session)

        bill.official_title = data['title']
        bill.chamber = data['chamber']
        bill.save()

        print "Importing %s" % bill

        for action in data['actions']:
            date = datetime.datetime.fromtimestamp(action['date'])
            bill.action_set.get_or_create(
                date=date,
                action=action['action'],
                actor=action['actor'])

            if (not bill.last_action) or date > bill.last_action:
                bill.last_action = date
                bill.save()

        for version in data['versions']:
            if not version['url']:
                continue

            bill.version_set.get_or_create(
                name=version['name'],
                url=version['url'])

        for sponsor in data['sponsors']:
            if not sponsor['leg_id']:
                continue

            session_name = sponsor['leg_id'][0]
            chamber = sponsor['leg_id'][1]
            district = sponsor['leg_id'][2]
            leg = Legislator.objects.get(
                role__state=state,
                role__session__name=session_name,
                role__chamber=chamber,
                role__district=district)
            Sponsor.objects.get_or_create(bill=bill,
                                          legislator=leg,
                                          type=sponsor['type'])
                                                  
    def import_legislator(self, data, state):
        # Try to find an existing legislator to merge with:
        try:
            leg = Legislator.objects.get(state=state,
                                         full_name=data['full_name'])
        except Legislator.DoesNotExist:
            leg = Legislator(state=state, full_name=data['full_name'])

        leg.first_name = data['first_name']
        leg.last_name = data['last_name']
        leg.middle_name = data['middle_name']
        leg.suffix = data.get('suffix', '') or ''
        leg.party = data['party']
        leg.save()

        session = state.session_set.get(name=data['session'])

        leg.role_set.get_or_create(state=state,
                                   chamber=data['chamber'],
                                   district=data['district'],
                                   session=session)

                    
                                         
