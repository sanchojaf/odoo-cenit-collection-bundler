#!/usr/bin/env python2
__author__ = 'dhbahr@gmail.com'

import os
import sys
import tempfile
import argparse
import simplejson


MAIN_DESCRIPTION = "This is a tool for automating the creation of " \
                   "odoo-integration addons from a Cenit shared_collections."
SOURCE_HELP = "Source file containing json description of the shared collection"
FIXED_HELP = "Fix to the specific version of the collection"
DIR_HELP = "Specify an output directory for the resulting addon"


tpl_paths = [
    'models/__init__.py.tpl',
    'models/config.py.tpl',
    'security/ir.model.access.csv.tpl',
    'view/config.xml.tpl',
    'view/wizard.xml.tpl',
    '__init__.py.tpl',
    '__openerp__.py.tpl',
]

def i(depth, string):
    tab = " " * 4
    return tab*depth + string

tpl_strs = {
    'params':
        i(1, "\"{parameter}\":'{key}',\n"),
    'model_fields':
        i(1, "{key} = fields.Char('{label}')\n"),
    'model_getters':
        i(1, "def get_default_{key}(self, cr, uid, ids, context=None):\n") +
        i(2, "{key} = self.pool.get('ir.config_parameter').get_param(\n") +
        i(3, "cr, uid,\n") +
        i(3, "'odoo_cenit.{{name}}.{key}', default=None,\n") +
        i(3, "context=context\n") +
        i(2, ")\n") +
        i(2, "return {{{{'{key}': {key} or ''}}}}\n") +
        i(1, "\n"),
    'model_setters':
        i(1, "def set_{key}(self, cr, uid, ids, context=None):\n") +
        i(2, "config_parameters = self.pool.get('ir.config_parameter')\n") +
        i(2, "for record in self.browse(cr, uid, ids, context=context):\n") +
        i(3, "config_parameters.set_param (\n") +
        i(4, "cr, uid,\n") +
        i(4, "'odoo_cenit.{{name}}.{key}, record.{key} or '',\n") +
        i(4, "context=context\n") +
        i(3, ")\n") +
        i(1, "\n"),
    'view_fields':
        i(7, "<field name='{key}' placeholder='Your {label}' />\n")
}

def get_parser():
    parser = argparse.ArgumentParser(description=MAIN_DESCRIPTION)

    parser.add_argument("source", help=SOURCE_HELP)

    parser.add_argument("-f", "--fixed-version",
                        action="store_true", help=FIXED_HELP)
    parser.add_argument("-d", "--directory", default="~", help=DIR_HELP)

    return parser

def get_source_json(source):
    with open(source) as source_file:
        contents = source_file.read()
        return simplejson.loads(contents)


# def get_params_template(parameters):
#     tpl = "    \"{parameter}\":'{key}',\n"
#     rc = ''
#     for parameter in parameters:
#         rc += tpl.format(**parameter)
#     return rc
#
# def get_model_fields_template(parameters):
#     tpl = "    {key} = fields.Char('{label}')\n"
#     rc = ''
#     for parameter in parameters:
#         rc += tpl.format(**parameter)
#     return rc
#
# def get_model_getters_template(parameters):
#     tpl = "    def get_default_{key}(self, cr, uid, ids, context=None):\n" \
#           "        {key} = self.pool.get('ir.config_parameter').get_param(\n" \
#           "            cr, uid,\n" \
#           "            'odoo_cenit.{{name}}.{key}, default=None,\n" \
#           "            context=context\n" \
#           "        )\n" \
#           "        return {{{{'{key}': {key} or ''}}}}\n" \
#           "    \n"
#     rc = ''
#     for parameter in parameters:
#         rc += tpl.format(**parameter)
#     return rc
#
# def get_model_setters_template(parameters):
#     tpl = "    def set_{key}(self, cr, uid, ids, context=None):\n" \
#           "        config_parameters = self.pool.get('ir.config_parameter')\n" \
#           "        for record in self.browse(cr, uid, ids, context=context):\n" \
#           "            config_parameters.set_param (\n" \
#           "                cr, uid,\n" \
#           "                'odoo_cenit.{{name}}.{key}, record.{key} or '',\n" \
#           "                context=context\n" \
#           "            )\n" \
#           "    \n"
#     rc = ''
#     for parameter in parameters:
#         rc += tpl.format(**parameter)
#     return rc
#
# def get_view_fields_template(parameters):
#     tpl = "<field name='{key}' placeholder='Your {label}' />\n"
#     rc = ''
#     for parameter in parameters:
#         rc += tpl.format(**parameter)
#
#     return rc[:-1]


def get_template(tpl_name, parameters):
    tpl = tpl_strs.get(tpl_name)

    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)

    return rc[:-1]

def create_odoo_addon(collection, directory):
    tmp_dir = tempfile.mkdtemp()
    print "Processing collection", collection.get('name'), "in ", tmp_dir

    data = {
        'name': collection.get('name'),
        'summary': collection.get('summary'),
        'shared_version': collection.get('shared_version'),
        'pull_parameters': '',
        'model_fields': '',
        'model_getters': '',
        'model_setters': '',
        'view_fields': '',
        'config': "'view/config.xml',",
        'wizard': "'view/wizard.xml',"
    }

    pull_parameters = collection.get('pull_parameters', [])

    params = get_template('params', pull_parameters)

    if not params:
        data.update({'wizard':  ''})
        data.update({'config':  ''})
    else:
        data.update({'pull_parameters': params})

        model_fields = get_template('model_fields', pull_parameters)
        data.update({'model_fields': model_fields})

        model_getters = get_template('model_getters', pull_parameters).format(
            **collection
        )
        data.update({'model_getters': model_getters})

        model_setters = get_template('model_setters', pull_parameters).format(
            **collection
        )
        data.update({'model_setters': model_setters})

        view_fields = get_template('view_fields', pull_parameters)
        data.update({'view_fields': view_fields})

    for path in tpl_paths:
        content = ''
        if not params and path.startswith('view'):
            continue
        tpl_path = os.path.expanduser(os.path.join('./tpl', path))
        print "Reading", tpl_path, '...'
        with open(tpl_path) as tpl_file:
            tpl = tpl_file.read()
            content = tpl.format(**data)

        target_path = os.path.join(tmp_dir, path[:-4])
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        with open(target_path, 'w') as target_file:
            target_file.write(content)

    final = os.path.join(output_dir, 'cenit_'+collection.get('name'))
    # TODO use shutil or something pro-er
    command = "mv {source} {target}".format(source=tmp_dir, target=final)
    os.system(command)

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    output_dir = os.path.expandvars(args.directory)

    if not (os.path.exists(output_dir)):
        try:
            os.mkdir(output_dir)
        except Exception as e:
            print e
            sys.exit(1)

    collections = get_source_json(args.source)
    for collection in collections:
        create_odoo_addon(collection, output_dir)