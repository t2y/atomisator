# -*- coding: utf-8 -*-
"""Recipe trac"""
import os
from os.path import join
import sys
import subprocess
import ConfigParser
import shutil

import pkg_resources
import zc.buildout
import zc.recipe.egg

from trac.admin.console import TracAdmin
from trac.ticket.model import *

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['executable'] = sys.executable

    def install(self):
        """Installer"""

        # Utility function to interpreted boolean option value
        getBool = lambda s: s.strip().lower() == 'true'

        options = self.options
        # adding trac-admin and tracd into bin
        entry_points = [('trac-admin', 'trac.admin.console', 'run'),
                        ('tracd', 'trac.web.standalone', 'main')]

        zc.buildout.easy_install.scripts(
                entry_points, pkg_resources.working_set,
                options['executable'], options['bin-directory']
                )

        # now generating the trac instance, if required
        location = options['location']
        project_name = options.get('project-name', 'My project')
        project_url = options.get('project-url', 'http://example.com')
        db = 'sqlite:%s' % join('db', 'trac.db')
        repos_type = options['repos-type']
        repos_path = options['repos-path']
        if not os.path.exists(location):
            os.mkdir(location)

        trac_admin = join(options['bin-directory'], 'trac-admin')

        trac = TracAdmin(location)

        if not trac.env_check():
            trac.do_initenv('%s %s %s %s' % (project_name, db, repos_type, repos_path))

        # Upgrade Trac instance to keep it fresh
        env = trac.env_open()
        needs_upgrade = env.needs_upgrade()
        force_upgrade = getBool(options.get('force-instance-upgrade', 'False'))
        if needs_upgrade or force_upgrade:
            env.upgrade(backup=True)

        milestone_list = [m.name for m in Milestone.select(env)]
        comp_list = [c.name for c in Component.select(env)]

        # Remove Trac default example data
        clean_up = getBool(options.get('remove-examples', 'True'))
        if clean_up:
            # Remove default milestones
            for milestone in ('milestone1', 'milestone2', 'milestone3', 
                              'milestone4'):
                if milestone in milestone_list:
                    trac._do_milestone_remove(milestone)
            # Remove default components
            for comp in ('component1', 'component2'):
                if comp in comp_list:
                    trac._do_component_remove(comp)

        # Adding the 'future' roadmap
        if 'future' not in milestone_list:
            trac._do_milestone_add('future')

        # adding components
        components = options.get('components', '')
        components = [(comp.split()[0].strip(), comp.split()[1].strip(),)
                      for comp in components.split('\n')
                      if comp.strip() != '' and len(comp.split()) > 1]

        for comp, owner in components:
            if comp in comp_list:
                continue
            trac._do_component_add(comp, owner)

        trac_ini = join(location, 'conf', 'trac.ini')
        parser = ConfigParser.ConfigParser()
        parser.read([trac_ini])
        if 'components' not in parser.sections():
            parser.add_section('components')

        # force upgrade of informations used during initialization
        parser.set('project', 'name', project_name)
        parser.set('trac', 'repository_dir', repos_path)
        parser.set('trac', 'repository_type', repos_type)

        # Set project description
        project_descr = options.get('project-description', None)
        if project_descr:
            parser.set('project', 'descr', project_descr)
            parser.set('header_logo', 'alt', project_descr)

        # Set footer message
        parser.set('project', 'footer', options.get('footer-message', 'This Trac instance was generated by <a href="http://pypi.python.org/pypi/pbp.recipe.trac">pbp.recipe.trac</a>.'))

        # if 'hg' in the repository type, hook its plugin
        if repos_type == 'hg':
            parser.set('components', 'tracext.hg.*', 'enabled')

        buildbot_url = options.get('buildbot-url', None)
        if buildbot_url is not None:
            parser.set('components', 'navadd.*', 'enabled')
            if 'navadd' not in parser.sections():
                parser.add_section('navadd')
            parser.set('navadd', 'add_items', 'buildbot')
            parser.set('navadd', 'buildbot.target', 'mainnav')
            parser.set('navadd', 'buildbot.title', 'Buildbot')
            parser.set('navadd', 'buildbot.url', buildbot_url)

        # adding plugin for time estimation
        parser.set('components', 'timingandestimationplugin.*', 'enabled')

        # logo
        header_logo = options.get('header-logo', '')
        header_logo = os.path.realpath(header_logo)
        if os.path.exists(header_logo):
            shutil.copyfile(header_logo, join(location, 'htdocs', 'logo'))

        parser.set('header_logo', 'src', 'site/logo')
        parser.set('header_logo', 'link', project_url)

        # SMTP parameters
        for name in ('always-bcc', 'always-cc', 'default-domain', 'enabled',
                     'from', 'from-name', 'password', 'port', 'replyto',
                     'server', 'subject-prefix', 'user'):
            param_name = "smtp-%s" % name
            value = options.get(param_name, None)
            if value is None:
                continue
            parser.set('notification', name.replace('-', '_'), value)

        # setting up time tracking
        if 'ticket-custom' not in parser.sections():
            parser.add_section('ticket-custom')

        for field, value in (('totalhours', 'text'),
                             ('totalhours.value', '0'),
                             ('totalhours.label', 'Total Hours'),
                             ('hours', 'text'),
                             ('hours.value', '0'),
                             ('hours.label', 'Hours to Add'),
                             ('estimatedhours', 'text'),
                             ('estimatedhours.value', '0'),
                             ('estimatedhours.label', 'Estimated Hours')):
            parser.set('ticket-custom', field, value)

        # Apply custom parameters defined by the user
        custom_params = options.get('trac-ini-additional', None)
        if custom_params:
            param_list = [s.split('|') for s in [l.strip() for l in custom_params.split('\n')] if len(s) > 0]
            for param in param_list:
                if len(param) == 3:
                    parser.set(param[0].strip(), param[1].strip(), param[2].strip())

        parser.write(open(trac_ini, 'w'))

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    update = install

