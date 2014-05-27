import types
import inspect


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
    >>> t.clble = t
    >>> mb.clble(20)
    (10, 20, 3)

    """

    def __init__(self, obj, **kwargs):
        """
        """
        self._obj = obj
        self._kwargs = kwargs

    def __getattribute__(self, item):
        original_obj = super(MagicBind, self).__getattribute__('_obj')

        try:
            original_attribute = getattr(original_obj, item)
        except AttributeError:
            original_attribute = super(MagicBind, self).__getattribute__(item)

        callable_method = super(MagicBind, self).__getattribute__('__call__')

        if isinstance(original_attribute, types.MethodType):
            self._clble = original_attribute
            return callable_method
        else:
            return original_attribute

    def __call__(self, *args, **kwargs):
        overwrite_dict = (super(MagicBind, self).__getattribute__('_kwargs'))

        arguments_dict = dict(overwrite_dict)
        arguments_dict.update(kwargs)

        original_callable = super(MagicBind, self).__getattribute__('_clble')
        ok_args, ok_kwargs = merge_args(original_callable, overwrite_dict, args, )
        return original_callable(*args, **arguments_dict)


def merge_args(argspec, overwriting, args, kwargs):
    """Return a tuple (vargs, kw), where `vargs` represents a list of values,
        and kwargs a dictionary, to be unpacked when calling the callable
        with the provided argspec
    """
    vargs = []
    kw = {}

    for argnum, argname in enumerate(argspec[0]):
        if argname in overwriting:
            vargs.append(overwriting[argname])
        else:
            vargs.append(args.pop())

    pass


class Asdf(object):
    def asdf(self, x, y, z, *args, **kwargs):
        return "asdf", x, y, z

    @classmethod
    def cls_asdf(cls, x, y, z, t, *args, **kwargs):
        return "classmethod", x, y, z, t, args, kwargs

    @staticmethod
    def static_asdf(x, y, z, t, *args, **kwargs):
        return "lol static", x, y, z, t, args, kwargs


a = Asdf()
m1 = MagicBind(a, x=9)
m1.asdf(6, z=8)
# if __name__ == '__main__':
#     import doctest
#
#     doctest.testmod()