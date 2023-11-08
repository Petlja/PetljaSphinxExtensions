__author__ = 'petlja'

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.fileutil import copy_asset
from pkg_resources import resource_filename


def setup(app):
    app.add_css_file('py-code.css')
    app.add_js_file('py-code.js')
    app.connect('env-updated', copy_workers)
    app.add_directive('py-code', PyCodeDirective)
    app.add_node(PyCodeNode, html=(visit_pycode_node, depart_pycode_node))

def copy_workers(app, env):
    static_files = resource_filename('petlja_sphinx_extensions', 'extensions/py_code/js/workers')
    if app.builder.name == 'petlja_builder':
        copy_asset(static_files, app.builder.rootdir)
    else:
        copy_asset(static_files, app.builder.outdir)



TEMPLATE_START = '''
  <py-code id="%(divid)s">
    %(py_packages)s
    <textarea>
%(code)s
      </textarea>
    '''


TEMPLATE_END = '''
    </py-code>
    '''


class PyCodeNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(PyCodeNode, self).__init__()
        self.note = content


def visit_pycode_node(self, node):
    node.delimiter = "_start__{}_".format("info")
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.note
    self.body.append(res)


def depart_pycode_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class PyCodeDirective(Directive):
    required_arguments = 1
    optional_arguments = 1
    has_content = True
    option_spec = {}
    option_spec.update({
        'packages': directives.unchanged,
    })


    def run(self):
        """
        generate html to include note box.
        :param self:
        :return:
        """
        self.options['divid'] = self.arguments[0]
        self.options['code'] = "\n".join(self.content)
        self.options['py_packages'] = ""

        if 'packages' in self.options:
            for package in self.options['packages'].split(','):
                self.options['py_packages'] += "<python-package>" + package + "</python-package>" + "\n"


        innode = PyCodeNode(self.options)

        return [innode]
    
