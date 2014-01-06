# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team and Gun.io

import os
import re
import time
import tempfile
import cProfile

from django.conf import settings

words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]

class ProfileMiddleware(object):
    """Profiles the page using cProfile, displays the result as a graph
    (using gprof2dot and graphviz)

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser:

    http://yoursite.com/yourview/?prof

    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    Based of http://gun.io/blog/fast-as-fuck-django-part-1-using-a-profiler/
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG or request.user.is_superuser) and 'prof' in request.GET:
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_request(self, request):
        if (settings.DEBUG or request.user.is_superuser) and 'prof' in request.GET: 
            self.prof = cProfile.Profile()
            self.prof.enable()
            self.start = time.time()

    def process_response(self, request, response):
        if (settings.DEBUG or request.user.is_superuser) and 'prof' in request.GET:
            print("request took %.02fms" % ((time.time() - self.start)*1000))

            import subprocess
            self.prof.disable()

            _, f = tempfile.mkstemp()
            self.prof.dump_stats(f)
            gprof2dot = subprocess.Popen(['gprof2dot', '-f', 'pstats', f], stdout=subprocess.PIPE)

            _, pngtmp = tempfile.mkstemp()
            dot = subprocess.Popen(['dot', '-Tpng', '-o', pngtmp], stdin=gprof2dot.stdout)
            dot.communicate()

            response.content_type = "image/png"
            img = open(pngtmp).read()
            from django.http import HttpResponse
            os.unlink(f)
            os.unlink(pngtmp)
            return HttpResponse(img, content_type="image/png")

        return response
