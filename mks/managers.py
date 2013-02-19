import difflib
from django.core.cache import cache
from django.db import models


class KnessetManager(models.Manager):
    """This is a manager for Knesset class"""

    def __init__(self):
        super(KnessetManager, self).__init__()
        self._current_knesset = None

    def current_knesset(self):
        if self._current_knesset is None:
            self._current_knesset = self.get_query_set().order_by('-number')[0]
        return self._current_knesset


class BetterManager(models.Manager):
    def __init__(self):
        super(BetterManager, self).__init__()
        self._names = []

    def find(self, name):
        ''' looks for a member with a name that resembles 'name'
            the returned array is ordered by similiarity
        '''
        names = cache.get('%s_names' % self.model.__name__)
        if not names:
            names = self.values_list('name', flat=True)
            cache.set('%s_names' % self.model.__name__, names)
        possible_names = difflib.get_close_matches(
            name, names, cutoff=0.5, n=5)
        qs = self.filter(name__in=possible_names)
        # used to establish size, overwritten later
        ret = range(qs.count())
        for m in qs:
            if m.name == name:
                return [m]
            ret[possible_names.index(m.name)] = m
        return ret


class CurrentKnessetMembersManager(models.Manager):
    "Adds the ability to filter on current knesset"

    def get_query_set(self):
        from mks.models import Knesset
        qs = super(CurrentKnessetMembersManager, self).get_query_set()
        qs = qs.filter(current_party__knesset=Knesset.objects.current_knesset())
        return qs