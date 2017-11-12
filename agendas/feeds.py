from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from actstream import actor_stream
from models import Agenda # AgendaVote, AgendaMember, AgendaBill

# TODO: merge with mks.feeds
class ActionStreamFeed(Feed):
    '''
    A generic automatically generated feed. The feed accepts one optional url parameter *verbs* that
    contains a comma-sperated list of verbs to be included in the feed
    '''

    def get_object (self, request, object_id):
        verbs = request.GET.get('verbs', False)
        self.verbs = verbs.split(',') if verbs else False
        return get_object_or_404(self.REPRESENTED_MODEL, pk=object_id)

    def link(self, agenda):
        return agenda.get_absolute_url()
  
    def items(self, obj):
        #raise BaseException(type(obj))
        stream = actor_stream(obj)
        if stream:
            if self.verbs:
                stream = stream.filter(verb__in = self.verbs)
            return (item for item in stream[:20] if item.target) # remove items with None target, or invalid target
        return []

    def item_title(self, item):
        title = _(item.verb)
        if item.description:
            title += u' %s' % _(item.description)
        return title

    def item_description(self, item):
        target = item.target
        return target

    def item_link(self, item):
        target = item.target

        try:
            return getattr(target, 'url')
        except:
            return target.get_absolute_url()


class AgendaActivityFeed(ActionStreamFeed):
    REPRESENTED_MODEL = Agenda
    
    # Receives an object reference previously prd
    def title(self, agenda):
        return _('Agenda feed for %s') % (agenda,)
    
    def description(self, agenda):
        return _('Actions of %s, including votes, attended committees and posted articles') % (agenda,)
    
    # Action.objects.stream_for_model
