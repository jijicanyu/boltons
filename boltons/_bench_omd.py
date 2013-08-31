# -*- coding: utf-8 -*-
import string
import sys
sys.path.append('/home/mahmoud/projects/lithoxyl/')

import time
import lithoxyl
from lithoxyl import sinks, logger

from dictutils import OMD, FastIterOrderedMultiDict
from werkzeug.datastructures import MultiDict, OrderedMultiDict as WOMD
from collections import OrderedDict as OD

q_sink = lithoxyl.sinks.QuantileSink()
log = lithoxyl.logger.BaseLogger('bench_stats', sinks=[q_sink])

try:
    profile
except NameError:
    times = 10
    size = 10000
    redun = 2
else:
    times = 1
    size = 10000
    redun = 10

_rng = range(size / redun) * redun
_unique_keys = set(_rng)
_bad_rng = range(size, size + size)
_pairs = zip(_rng, _rng)

_actions = ('setitem', 'iteritems', 'iterkeys', 'getitem', 'keyerror', 'pop')
_all_actions = ('init',) + _actions


def bench():
    for impl in (FastIterOrderedMultiDict, OMD, WOMD, MultiDict, OD, dict):
        q_sink = lithoxyl.sinks.QuantileSink()
        impl_name = '.'.join([impl.__module__, impl.__name__])
        log = lithoxyl.logger.BaseLogger(impl_name, sinks=[q_sink])
        print
        print '+ %s' % impl_name
        for _ in range(times):
            with log.info('total'):
                for _ in range(times):
                    with log.info('init'):
                        target_dict = impl(_pairs)
                    for action in _actions:
                        action_func = globals()['_do_' + action]
                        with log.info(action):
                            action_func(target_dict)
        for action in _all_actions:
            best_msecs = q_sink.qas[impl_name][action].min * 1000
            print '   - %s - %g ms' % (action, best_msecs)
        best_msecs = q_sink.qas[impl_name]['total'].min * 1000
        median_msecs = q_sink.qas[impl_name]['total'].median * 1000
        print ' > ran %d loops of %d items each, best time: %g ms, median time: %g ms' % (times, size, best_msecs, median_msecs)

    print
    return


def _do_setitem(target_dict):
    for k, i in enumerate(string.lowercase):
        target_dict[k] = i


def _do_iteritems(target_dict):
    [_ for _ in target_dict.iteritems()]


def _do_iterkeys(target_dict):
    [_ for _ in target_dict.iterkeys()]


def _do_getitem(target_dict):
    for k in _rng:
        target_dict[k]


def _do_keyerror(target_dict):
    for k in _bad_rng:
        try:
            target_dict[k]
        except KeyError:
            pass


def _do_pop(target_dict):
    for k in _unique_keys:
        target_dict.pop(k)
    assert not target_dict


if __name__ == '__main__':
    bench()
