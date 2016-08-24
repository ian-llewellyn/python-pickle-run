#!/bin/env python3
# -*- coding: utf-8 -*-
"""pickle_run.py

A script to demonstrate how execution can be delegated from one object to
another.

In this script, there are three ways in which the code can be 'remotely'
executed: a) func() is called as a method of a passed in class, b) func() is
called as a method of self (the executing 'remote' class), c) func() is called
in the global namespace. See commented out lines in loc_ex() method.

The daemon flag is used by the decorator() function to establish if delegation
is required.
"""
import pickle

def get_name():
    """get_name()

    Placed here to test global function calls.
    """
    return 'Gladys'

class Peep(object):
    def __init__(self, name, daemon):
        self.name = name
        self.daemon = daemon

    def rem_ex(self, func, target_obj, *args, **kwargs):
        """rem_ex()

        Called by the 'client' class. Calls loc_ex() on the 'daemon' class.
        """
        stream = pickle.dumps({
            'func': func,
            'context': target_obj, # or self if the calling class has important
                                   # state. Note: the daemon flag would cause
                                   # infinite recursion. This could be overcome
                                   # by overriding self.daemon with target_obj.
                                   # daemon (but on a copy of self that's passed
                                   # forward).
            'args': args,
            'kwargs': kwargs
        })

        return target_obj.loc_ex(stream)

    def loc_ex(self, stream):
        """loc_ex()

        Called by rem_ex() in the 'client' class. This may be an intermediary
        class. If daemon is not True, @decorator.inner() will delegate further.
        """
        proto = pickle.loads(stream)

        # Have func run in origin_obj's class namespace
        #ret = eval("proto['context']." + proto['func'] + \
        #    "(*proto['args'], **proto['kwargs'])")

        # Have func run in target_obj's class namespace
        ret = eval("self." + proto['func'] + \
            "(*proto['args'], **proto['kwargs'])")

        # Have func run in global namespace (by target_obj
        # (is that even relevant?))
        #ret = eval(proto['func'] + "(*proto['args'], **proto['kwargs'])")
        return ret

    def decorator(func):
        def inner(self, *args, **kwargs):
            if self.daemon is True:
                return func(self, *args, **kwargs)
            return self.rem_ex(func.__name__, self.daemon, *args, **kwargs)
        return inner

    @decorator
    def get_name(self):
        return self.name

if __name__ == '__main__':
    a = Peep('Alice', daemon=True)
    b = Peep('Bob', daemon=a)
    d = Peep('Doreen', daemon=b)

    c = b.rem_ex('get_name', d)
    #c = d.get_name()
    print(c)
