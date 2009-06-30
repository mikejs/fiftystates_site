from models import *
import urllib
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

class NewBills(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return State.objects.get(abbreviation__iexact=bits[0])

    def title(self, obj):
        return "Fifty State Project: Recent bills for %s" % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Bills recently added for the state of %s" % obj.name

    def items(self, obj):
        return obj.bill_set.order_by('-date_added')[:10]

    def item_pubdate(self, item):
        return item.date_added

class Actions(Feed):
    def get_object(self, bits):
        if len(bits) != 4:
            raise ObjectDoesNotExist
        return Bill.objects.get(state__abbreviation__iexact=bits[0],
                                session__name=bits[1],
                                chamber=bits[2],
                                bill_id=bits[3])

    def title(self, obj):
        return "Fifty State Project: Recent actions for %s" % obj.bill_id

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url() + "#actions"

    def description(self, obj):
        return "Actions recently performed on %s: %s" % (
            obj.bill_id, obj.title)

    def items(self, obj):
        return obj.action_set.order_by('-date')[:10]

    def item_pubdate(self, item):
        return item.date

    def item_link(self, item):
        return urllib.quote(item.bill.get_absolute_url() + "#action%d" % item.pk)

class BillSponsors(Feed):
    title_template = "feeds/sponsors_title.html"
    description_template = "feeds/sponsors_description.html"
    
    def get_object(self, bits):
        if len(bits) != 4:
            raise ObjectDoesNotExist
        return Bill.objects.get(state__abbreviation__iexact=bits[0],
                                session__name=bits[1],
                                chamber=bits[2],
                                bill_id=bits[3])
    def title(self, obj):
        return "Fifty State Project: Sponsors of %s" % obj.bill_id

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url() + "#sponsors"

    def description(self, obj):
        return "Sponsors of %s: %s" % (obj.bill_id, obj.title)

    def items(self, obj):
        return map(lambda s: {'bill': obj, 'sponsor': s},
                   obj.sponsor_set.order_by('-date_added')[:10])

    def item_pubdate(self, item):
        return item['sponsor'].date_added

    def item_link(self, item):
        return urllib.quote(item['bill'].get_absolute_url() + "#sponsor%d" % item['sponsor'].legislator.pk)

class Sponsorships(Feed):
    title_template = "feeds/sponsors_title.html"
    description_template = "feeds/sponsors_description.html"
    
    def get_object(self, bits):
        if len(bits) != 2:
            raise ObjectDoesNotExist
        return Legislator.objects.get(pk=bits[1])

    def title(self, obj):
        return "Fifty State Project: Bills sponsored by %s" % obj.full_name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Bills sponsored by %s" % obj.full_name

    def items(self, obj):
        return map(lambda s: {'bill': s.bill, 'sponsor': s},
                   obj.sponsor_set.order_by('-date_added')[:10])

    def item_pubdate(self, item):
        return item['sponsor'].date_added

    def item_link(self, item):
        return urllib.quote(item['bill'].get_absolute_url() + "#sponsor%d" % item['sponsor'].legislator.pk)
