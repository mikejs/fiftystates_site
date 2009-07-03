from django.core.management.base import BaseCommand
from fiftystates_site.fiftystates.models import *
import sys, os, re, glob, datetime
try:
    import json
except:
    import simplejson as json

class Command(BaseCommand):
    def get_leg(self, session_name, chamber, district):
        key = (session_name, chamber, district)

        if key in self.leg_cache:
            return self.leg_cache[key]
        else:
            leg = Legislator.objects.get(
                state=self.state,
                role__session__name=session_name,
                role__chamber=chamber,
                role__district=district)
            self.leg_cache[key] = leg
            return leg

    def handle(self, *args, **options):
        assert len(args) >= 2

        data_dir = args[0]
        sub_dirs = map(lambda s: os.path.join(data_dir, s),
                       args[1:])

        for dir in sub_dirs:
            with open(os.path.join(dir, 'state_metadata.json')) as f:
                metadata = json.load(f)

            self.leg_cache = {}

            (self.state, c) = State.objects.get_or_create(
                abbreviation__iexact=metadata['state'],
                defaults={
                    'upper_chamber_term': metadata['upper_term'],
                    'lower_chamber_term': metadata['lower_term'],
                    'upper_chamber_title': metadata['upper_title'],
                    'lower_chamber_title': metadata['lower_title'],
                    'abbreviation': metadata['state'],
                    'name': metadata['state_name'],
                    'upper_chamber_name': metadata['upper_chamber_name'],
                    'lower_chamber_name': metadata['lower_chamber_name'],
                    'legislature_name': metadata['legislature_name']})

            for (session_name, details) in metadata['session_details'].items():
                (session, c) = self.state.session_set.get_or_create(
                    name=session_name,
                    defaults={'start_year': details['years'][0],
                              'end_year': details['years'][-1]})

                for sub in details['sub_sessions']:
                    self.state.session_set.get_or_create(
                        name=sub,
                        defaults={'start_year': session.start_year,
                                  'end_year': session.end_year,
                                  'parent': session})

            for name in glob.iglob(os.path.join(
                    dir, 'legislators', '*.json')):
                with open(name) as f:
                    self.import_legislator(json.load(f))

            for name in glob.iglob(os.path.join(
                    dir, 'bills', '*.json')):
                with open(name) as f:
                    self.import_bill(json.load(f))

    def import_bill(self, data):
        session = self.state.session_set.get(name=data['session'])

        (bill, created) = Bill.objects.get_or_create(
            bill_id=data['bill_id'],
            session=session,
            chamber=data['chamber'],
            state=self.state,
            defaults={'short_title': data.get('short_title', ''),
                      'official_title': data['title']})

        print "Importing %s" % bill

        actions = list(bill.action_set.values('date', 'action',
                                              'actor'))
        for action in data['actions']:
            action['date'] = datetime.datetime.fromtimestamp(action['date'])
            if action not in actions:
                bill.action_set.add(Action(
                        date=action['date'],
                        actor=action['actor'],
                        action=action['action']))

            if (not bill.last_action) or action['date'] > bill.last_action:
                bill.last_action = action['date']

        bill.save()

        versions = list(bill.version_set.values('url', 'name'))
        for version in data['versions']:
            if not version['url']:
                continue

            if version not in versions:
                bill.version_set.add(Version(name=version['name'],
                                             url=version['url']))

        for sponsor in data['sponsors']:
            if not sponsor['leg_id']:
                continue

            leg = self.get_leg(*sponsor['leg_id'])

            if Sponsor.objects.filter(
                bill=bill, legislator=leg,
                type=sponsor['type']).count() == 0:

                Sponsor.objects.create(bill=bill, legislator=leg,
                               type=sponsor['type'])

        votes = list(bill.vote_set.values('date', 'motion'))
        for vote in data['votes']:
            date = datetime.datetime.fromtimestamp(vote['date'])

            if {'date': date, 'motion': vote['motion']} not in votes:
                gen_vote = bill.vote_set.create(
                    date=date, motion=vote['motion'],
                    yes_count=vote['yes_count'],
                    no_count=vote['no_count'],
                    other_count=vote['other_count'],
                    passed=vote['passed'])

                for yes in vote['yes_votes']:
                    if yes['leg_id']:
                        leg = self.get_leg(*yes['leg_id'])
                        gen_vote.specificvote_set.add(
                            SpecificVote(
                                legislator=leg,
                                type='yes'))
                for no in vote['no_votes']:
                    if no['leg_id']:
                        leg = self.get_leg(*no['leg_id'])
                        gen_vote.specificvote_set.add(
                            SpecificVote(
                                legislator=leg,
                                type='no'))
                for other in vote['other_votes']:
                    if other['leg_id']:
                        leg = self.get_leg(*other['leg_id'])
                        gen_vote.specificvote_set.add(
                            SpecificVote(
                                legislator=leg,
                                type='other'))

    def import_legislator(self, data):
        # Try to find an existing legislator to merge with:
        (leg, created) = Legislator.objects.get_or_create(
            state=self.state, full_name=data['full_name'],
            defaults={'first_name': data['first_name'],
                      'last_name': data['last_name'],
                      'middle_name': data['middle_name'],
                      'suffix': data.get('suffix', '') or '',
                      'party': data['party']})

        session = self.state.session_set.get(name=data['session'])

        leg.role_set.get_or_create(state=self.state,
                                   chamber=data['chamber'],
                                   district=data['district'],
                                   session=session)
