# -*- encoding: utf-8 -*-
# (C) Copyright 2008 Tarek Ziadé <tarek@ziade.org>
"""
Mail output plugin.
"""
from email.MIMEText import MIMEText
from smtplib import SMTP
from datetime import datetime
from ConfigParser import ConfigParser
import logging

DEFAULT_BODY_TMPL = u"""\
Atomisator has triggered an alert. Check out for:

%(entries)s
"""

DEFAULT_ENTRY_TMPL = u"""\
  * %(title)s: %(link)s
"""

class Mail(object):
    """Will send an alert by mail

    Arguments:
        - config file

    Config file contains::

        [email]
        tos =
        subject =
        from =
        body_template =
        entry_template =
        smtp_server =
        smtp_port =

    With:
    - tos: emails to send the alert to, separated by commas
    - subject (optional)
    - from mail (optional)
    - path to a template file for the body (optional)
    - path to a template file for the entry (optional)
    - smtp server (optional)
    - smtp port (optional)
    """

    def __call__(self, entries, args):
        # do not send a mail on empty entries
        if len(entries) == 0:
            return

        config = ConfigParser()
        config.read([args[0]])
        values = {'tos': config.get('email', 'tos').split(',')}

        optionals = (('subject', 'Atomisator alert'),
                     ('from', 'admin@atomisator'),
                     ('body_template', DEFAULT_BODY_TMPL),
                     ('entry_template', DEFAULT_ENTRY_TMPL),
                     ('smtp_server', 'localhost'),
                     ('smtp_port', '25')
                     )

        for name, default in optionals:
            if config.has_option('email', name):
                values[name] = config.get('email', name)
                if name in ('body_template', 'entry_template'):
                    values[name] = open(values[name]).read()
            else:
                values[name] = default

        # XXX not keeping entries with no diff
        # this should be its own plugin so email plugin stay generic
        entries = [entry for entry in entries if entry.diff not in ('', None)]

        # lines
        # should be generic
        lines = [values['entry_template'] % {'title': entry.title,
                                             'link': entry.link,
                                             'diff': entry.diff}
                 for entry in entries]

        lines = [line for line in lines if line.strip() != 'None']

        # we don't mail an empty mail
        if ''.join(lines).strip() == '':
            return

        # mail content
        text = values['body_template'] % \
                {'entries': u'\n'.join(lines)}

        # stored in utf8 by default
        text = text.encode('utf8', 'ignore')

        # a mail is built, using MimeText
        msg = MIMEText(text)
        msg['Subject'] = values['subject']
        msg['To'] = ','.join(values['tos'])
        msg['From'] = values['from']
        msg['Date'] = datetime.now().isoformat()
        msg.set_charset('utf8')
        msg = msg.as_string()

        # let's send it
        s = SMTP(values['smtp_server'], int(values['smtp_port']))
        try:
            s.sendmail(values['from'], values['tos'], msg)
            logging.info('Mail sent to %s' % ','.join(values['tos']))
        finally:
            s.close()

