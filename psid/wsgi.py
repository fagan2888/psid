from decorator import decorator
from pkg_resources import resource_filename, Requirement
from selector import Selector, ByMethod
from static import Shock
from webob import Request
from wsgiref import util
import re

ALL_CAPS = re.compile(r'^[A-Z]+$')


def shock_wrap(package_name, dirname, **kw):
    resource = Requirement.parse(package_name)
    return Shock(resource_filename(resource, dirname), **kw)


@decorator
def bymethod_extraction(func, *args, **kw):
    methods = args[2]
    args = list(args)
    if not kw or hasattr(methods, '__getitem__'):
        kw = {}
        if not issubclass(methods.__class__, ByMethod) :
            raise ValueError("Must provide http_methods, method_dict *or* an instance of ByMethod class")
        http_methods = [(x, getattr(methods, x)) for x in dir(methods) if ALL_CAPS.match(x)]
        http_method_dict = dict(http_methods)
        args[2] = http_method_dict
    return func(*args, **kw)


class PSIDSelector(Selector):
    """ for custom handlers"""

    add = bymethod_extraction(Selector.add)


# shameless Yaro rip off wrapper  using WebOb
class WebObYaro(object):
    
    def __init__(self, app, extra_props=None):
        """Take the thing to wrap."""
        self.app = app
        self.extra_props = extra_props
        if self.extra_props:
            import pdb;pdb.set_trace()

    def __call__(self, environ, start_response):
        """Create Request, call thing, unwrap results and respond."""
        req = Request(environ)
        res = self.app(req, start_response)

        if isinstance(res, basestring):
            return [res]

        if isiterable(res):
            return res

        return res(environ, start_response)
    
##         req.save_to_environ()
##         import pdb;pdb.set_trace()
##         if body is None:
##             body = req.res.body
##         if not req.start_response_called:
##             req.start_response(req.res.status, req.res._headers, req.exc_info)
##             req.start_response_called = True
##         if isinstance(body, str):
##             return [body]
##         elif isiterable(body):
##             return body
##         else:
##             return util.FileWrapper(body)


class OWebObYaro(WebObYaro):
    
   def __call__(self, instance, environ, start_response):
        """Create Request, call thing, unwrap results and respond."""
        req = Request(environ, start_response)
        body = self.app(instance, req)
        #req.save_to_environ()
        if body is None:
            body = req.res.body
        if not req.start_response_called:
            req.start_response(req.res.status, req.res._headers, req.exc_info)
            req.start_response_called = True
        if isinstance(body, str):
            return [body]
        elif isiterable(body):
            return body
        else:
            return util.FileWrapper(body)    


def isiterable(it):
    # from Yaro
    """Return True if 'it' is iterable else return False."""
    try:
        iter(it)
    except:
        return False
    else:
        return True




