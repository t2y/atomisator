from Cheetah.Template import Template
import Cheetah.Filters

import os
from io import StringIO

tmpl = os.path.join(os.path.dirname(__file__), 'rss2.tmpl')

class Generator(object):

    def __call__(self, entries, args, size=50):
        """Generates items."""
        filename = args[0]
        link = args[1]
        title = args[2]
        description = ' '.join(args[3:])

        entries = entries[:size]

        class Encode(Cheetah.Filters.Filter):
            def filter(self, val, **kw):
                if 'encoding' in kw:
                    encoding = kw['encoding']
                else:
                    encoding = 'utf8'
                if isinstance(val, str):
                    val = val.encode(encoding)
                else:
                    val = str(val)
                return val

        
        data = {'entries': entries, 
                'channel': {'title': title, 'description': description,
                            'link': link}}
        template = Template(open(tmpl).read(), searchList=[data], filter=Encode)

        content = str(template)
        f = open(filename, 'w')
        try:
            f.write(content)
        finally:
            f.close()

