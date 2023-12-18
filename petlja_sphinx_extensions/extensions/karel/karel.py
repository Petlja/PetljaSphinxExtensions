#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'petlja'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
import json
import os

def add_i18n_js(app, supported_langs, *i18n_resources):
    app.add_js_file('jquery_i18n/CLDRPluralRuleParser.js')
    app.add_js_file('jquery_i18n/jquery.i18n.js')
    app.add_js_file('jquery_i18n/jquery.i18n.messagestore.js')
    app.add_js_file('jquery_i18n/jquery.i18n.fallbacks.js')
    app.add_js_file('jquery_i18n/jquery.i18n.language.js')
    app.add_js_file('jquery_i18n/jquery.i18n.parser.js')
    app.add_js_file('jquery_i18n/jquery.i18n.emitter.js')
    app.add_js_file('jquery_i18n/jquery.i18n.emitter.bidi.js')
    for res in i18n_resources:
            app.add_js_file(res + ".en.js")
            if app.config.language in ['sr_RS','sr@latn']: 
                app.config.language = {'sr_RS': 'sr-Cyrl', 'sr@latn': 'sr-Latn'}[app.config.language]
            if app.config.language and app.config.language != "en":
                app.add_js_file(res + "." + app.config.language + ".js")

# Adds CSS and JavaScript for the CodeMirror text editor
def add_codemirror_css_and_js(app, *mods):
    app.add_css_file('codemirror.css')
    app.add_js_file('codemirror.js')
    for mod in mods:
        app.add_js_file(mod + '.js')

# Adds JavaScript for the Sculpt in-browser implementation of Python
def add_skulpt_js(app):
        app.add_js_file('skulpt.min.js')
        app.add_js_file('skulpt-stdlib.js')

def setup(app):
    app.add_directive('karel', KarelDirective)

    # add_i18n_js(app, {"en","sr-Cyrl"},"codemirror-i18n")
    add_codemirror_css_and_js(app,'python')
    add_skulpt_js(app)

    app.add_css_file('karel.css')

    app.add_js_file('https://code.jquery.com/jquery-3.7.1.slim.js"')
    app.add_js_file('https://cdnjs.cloudflare.com/ajax/libs/jquery-modal/0.9.1/jquery.modal.min.js"')
    app.add_js_file('karelCorner.js')
    app.add_js_file('karelRobot.js')
    app.add_js_file('karelWorld.js')
    app.add_js_file('karelChat.js')
    app.add_js_file('karelRobotDrawer.js')
    app.add_js_file('karelUI.js')
    app.add_js_file('karel.js')
    add_i18n_js(app, {"en","sr-Cyrl,sr"},"karel-i18n")

    app.add_node(KarelNode, html=(visit_karel_node, depart_karel_node))

    app.connect('doctree-resolved', process_karel_nodes)
    app.connect('env-purge-doc', purge_karel_nodes)


TEMPLATE_START = """
<div data-childcomponent="%(divid)s" class="karel_section course-box course-box-problem">
    <div class="course-content">
        <p>
"""

TEMPLATE_END = """
    <div data-component="karel" id="%(divid)s" class="karel_section">
        <div class="karel_actions col-md-12 mb-2"><button class="btn btn-success run-button">Покрени програм</button>
        <button class="btn btn-default reset-button">Врати на почетак</button>
        <button class="btn btn-default blockly-button" style="display: %(blockly)s;">Blockly</button></div>
        <div style="overflow: hidden;" class="karel_actions col-md-12" >
            <section class="col-md-12">
                <article>
                    <textarea class="codeArea" id="%(divid)s" name="code" rows="10" style="width: 100%%;height:300px"></textarea>
                    <textarea class="configArea" style="display:none"><!--x %(initialcode)s x--></textarea>
                </article>
            </section>
            <section class="col-md-12">
                <article>
                    <canvas class="world" style="border-style: solid; border-width: 2px; border-color: inherit;" width="300" height="300">
                        <p>Please try loading this page in HTML5 enabled web browsers. All the latest versions of famous browsers such as Internet explorer, Chrome, Firefox, Opera support HTML5.</p>
                    </canvas>
                </article>
            </section>
        </div>
    </div>
    <p class="karel_caption karel_caption_text"> (%(divid)s)</p>
</p></div></div>

"""

class KarelNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(KarelNode, self).__init__()
        self.karel_components = content


def visit_karel_node(self, node):
    node.delimiter = "_start__{}_".format(node.karel_components['divid'])

    self.body.append(node.delimiter)

    res = TEMPLATE_START % node.karel_components
    self.body.append(res)


def depart_karel_node(self, node):
    res = TEMPLATE_END % node.karel_components
    self.body.append(res)
    self.body.remove(node.delimiter)

def process_karel_nodes(app, env, docname):
    pass


def purge_karel_nodes(app, env, docname):
    pass


class KarelDirective(Directive):
    """
.. karel::
    :blockly: -- use blocky
    """
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {
        'blockly': directives.flag
    }
    def run(self):
        """
        generate html to include Karel box.
        :param self:
        :return:
        """

        env = self.state.document.settings.env
        # keep track of how many activecodes we have....
        # could be used to automatically make a unique id for them.
        if not hasattr(env, 'karelcounter'):
            env.activecodecounter = 0
        env.activecodecounter += 1
        self.options['name'] = self.arguments[0].strip()
        self.options['divid'] = self.arguments[0]

        if not self.options['divid']:
            raise Exception("No divid for ..karel karel.py")

        if 'blockly' in self.options:
            self.options['blockly'] = "inline-block"
        else:
            self.options['blockly'] = "none"

        explain_text = None
        if self.content:
            if '~~~~' in self.content:
                idx = self.content.index('~~~~')
                explain_text = self.content[:idx]
                self.content = self.content[idx+1:]
            source = "\n".join(self.content)
        else:
            source = '\n'

        self.options['initialcode'] = source.replace("<", "&lt;")
        str = source.replace("\n", "*nline*")
        str0 = str.replace("\"", "*doubleq*")
        str1 = str0.replace("(", "*open*")
        str2 = str1.replace(")", "*close*")
        str3 = str2.replace("'", "*singleq*")
        self.options['argu'] = str3

        knode = KarelNode(self.options)
        self.add_name(knode)    # make this divid available as a target for :ref:

        return [knode]
