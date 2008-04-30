from pbp.skels.base import var
from pbp.skels.base import get_var
from pbp.skels.base import BaseTemplate

class Recipe(BaseTemplate):
    _template_dir = 'templates/recipe'
    summary = "A recipe"
    required_templates = []
    use_cheetah = True

    vars = [
        var('title', 'Title (use a short question)', 'Title'),
        var('short_name', ('Short name use for filename '
                           '(leave blank to make it calculated)'), 
            default='recipe'),
        var('author', 'Author name', default='John Doe'),
        var('keywords', 'Space-separated keywords/tags', 'tag1 tag2')
    ]

class Package(BaseTemplate):
    _template_dir = 'templates/package'
    summary = "A namespaced package"
    required_templates = []
    use_cheetah = True

    vars = [
        var('namespace_package', 'Namespace package (like pbp)', 
             default='pbp'), 
        var('package', 'The package contained namespace package (like example)',
            default='example'),
        var('version', 'Version', default='0.1.0'),
        var('description', 'One-line description of the package'),
        var('long_description', 'Multi-line description (in reST)'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('keywords', 'Space-separated keywords/tags'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name', default='GPL'),
        var('zip_safe', 'True/False: if the package can be distributed '
            'as a .zip file', default=False),
        ]

    def check_vars(self, vars, command):
        if not command.options.no_interactive and \
           not hasattr(command, '_deleted_once'):
            del vars['package']
            command._deleted_once = True
        return super(Package, self).check_vars(vars, command)

