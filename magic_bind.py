from copy import deepcopy
from itertools import chain
from types import FunctionType as Func, MethodType as Meth
from inspect import getargspec


class MagicBind(object):
    """ Wrapper around objects: calls all the wrapped object's methods
            with the arguments specified at initialization.

    A quick example of binding a requests session to an URL::

        from requests.sessions import Session
        my_session = Session()
        google_session = MagicBind(my_session, url='http://google.com')
        google_session.get()

    >>> class Test(object):
    ...     a = 100
    ...     def no_args(self):
    ...         return self
    ...     def two_positional(self, x, y):
    ...         return x, y
    ...     def three_positional(self, x, y, z):
    ...         return x, y, z
    ...     def sid_pox_defs_args_kwargs(self, x, y, z, a=98, b=43, d=-112,
    ...                                     e=-9, *owkargs, **ownkwargs):
    ...         return x,y,z,a,b,d,e,owkargs, ownkwargs
    ...     def defaults(self, x=1, y=2, z=3):
    ...         return x, y, z
    ...     def args_kwargs(self, x, y, *args, **kwargs):
    ...         return x, y, args, list(sorted(kwargs.items()))
    ...     def only_args_kwargs(self, *args, **kwargs):
    ...         return args, list(sorted(kwargs.items()))
    ...     @staticmethod
    ...     def static(x, y, z):
    ...         return x, y, z
    ...     def __call__(self, x, y, z=3):
    ...         return x, y, z

    >>> t = Test()
    >>> mb2 = MagicBind(t, x=221, z=5466, b=11111, a='first',
    ... d='second', third='thirsd')
    >>> mb2.sid_pox_defs_args_kwargs(-999, y=17, delta='del')
    (221, 17, 5466, 'first', 11111, 'second', -999, (), {'delta': 'del'})
    >>> mb = MagicBind(t, x=10)
    >>> mb.a
    100
    >>> mb.no_args() is t
    True
    >>> mb.two_positional(20)
    (10, 20)
    >>> mb.three_positional(20, 30)
    (10, 20, 30)
    >>> mb.defaults(20)
    (10, 20, 3)
    >>> mb.defaults()
    (10, 2, 3)
    >>> mb.defaults(y=20)
    (10, 20, 3)
    >>> mb.args_kwargs(20, 30, 40, z=50, w=60)
    (10, 20, (30, 40), [('w', 60), ('z', 50)])
    >>> mb.only_args_kwargs()
    ((), [])
    >>> mb.args_kwargs(20, 30, x=50, w=60) # doctest:+IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError:
    >>> mb.only_args_kwargs(20, 30, 40, z=50, w=60)
    ((20, 30, 40), [('w', 60), ('z', 50)])
    >>> mb.only_args_kwargs(10, 20, x=30, y=40)
    ((10, 20), [('x', 30), ('y', 40)])
    >>> mb.static(20, 30)
    (10, 20, 30)
    >>> mb(1, 2)
    (10, 1, 2)
    >>> t.clble = t
    >>> mb.clble(20)
    (10, 20, 3)"""
    def __init__(self, obj, *args, **kwargs):
        self._obj = obj
        self._kwargs = kwargs
        self._args = args

    def __getattribute__(self, item):
        original_obj = super(MagicBind, self).__getattribute__('_obj')

        try:
            original_attribute = getattr(original_obj, item)
        except AttributeError:
            original_attribute = super(MagicBind, self).__getattribute__(item)

        callable_method = super(MagicBind, self).__getattribute__('__call__')

        if isinstance(original_attribute, (Meth, Func)):
            self._clble = original_attribute
        elif callable(original_attribute):
            self._clble = original_attribute.__call__
        else:
            return original_attribute
        return callable_method

    def __call__(self, *args, **kwargs):
        ovw_kwargs = (super(MagicBind, self).__getattribute__('_kwargs'))
        ovw_args = super(MagicBind, self).__getattribute__('_args')
        orig_clble = super(MagicBind, self).__getattribute__('_clble')
        ok_args, ok_kwargs = (
            merge_args_better(orig_clble, ovw_args, ovw_kwargs, args, kwargs))
        return orig_clble(*ok_args, **ok_kwargs)


def merge_args_better(clble, prio_args, prio_kwargs, add_args, add_kwargs):
    ok_args = []
    ok_kwargs = {}
    prio_args = list(deepcopy(prio_args))
    prio_kwargs = deepcopy(prio_kwargs)
    add_args = list(add_args)

    begin_index = 0 if isinstance(clble, Func) else 1

    for argname in getargspec(clble)[0][begin_index:]:
        if argname in prio_kwargs:
            ok_args.append(prio_kwargs.pop(argname))
        elif argname in add_kwargs:
            ok_args.append(add_kwargs.pop(argname))
        elif prio_args:
            ok_args.append(prio_args.pop(0))
        elif add_args:
            ok_args.append(add_args.pop(0))

    ok_args.extend(chain(prio_args, add_args))
    if getargspec(clble)[2]:
        # also append prio_dict to transmit MagicBind initial arguments
        # as kws, if the underlying callable doesn't have args with that name
        ok_kwargs.update(add_kwargs)

    return ok_args, ok_kwargs


if __name__ == '__main__':
    import doctest

    doctest.testmod()