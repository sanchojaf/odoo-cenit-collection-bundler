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


def get_params_template(parameters):
    tpl = "\"{parameter}\":'{key}',\n"
    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)
    return rc

def get_model_fields_template(parameters):
    tpl = "{key} = fields.Char('{label}')\n"
    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)
    return rc

def get_model_getters_template(parameters):
    tpl = "    def get_default_{key}(self, cr, uid, ids, context=None):\n" \
          "        {key} = self.pool.get('ir.config_parameter').get_param(\n" \
          "            cr, uid,\n" \
          "            'odoo_cenit.{{name}}.{key}, default=None,\n" \
          "            context=context\n" \
          "        )\n" \
          "        return {{{{'{key}': {key} or ''}}}}\n" \
          "    \n"
    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)
    return rc

def get_model_setters_template(parameters):
    tpl = "    def set_{key}(self, cr, uid, ids, context=None):\n" \
          "        config_parameters = self.pool.get('ir.config_parameter')\n" \
          "        for record in self.browse(cr, uid, ids, context=context):" \
          "            config_parameters.set_param (\n" \
          "                cr, uid,\n" \
          "                'odoo_cenit.{{name}}.{key}, record.{key} or '',\n" \
          "                context=context\n" \
          "            )\n" \
          "    \n"
    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)
    return rc


def get_view_fields_template(parameters):
    tpl = "<field name='{key}' placeholder='Your {label}' />\n"
    rc = ''
    for parameter in parameters:
        rc += tpl.format(**parameter)
    return rc


def create_odoo_addon(collection, directory):
    tmp_dir = tempfile.mkdtemp()
    print "Processing collection in ", tmp_dir

    # print collection.get('name')
    # print collection.get('summary')
    # print collection.get('shared_version')
    # print collection.get('pull_parameters', [])

    data = {
        'name': collection.get('name'),
        'summary': collection.get('summary'),
        'shared_version': collection.get('shared_version'),
        'pull_parameters': '',
        'model_fields': '',
        'model_getters': '',
        'model_setters': '',
        'view_fields': '',
        'wizard': 'view/wizard.xml'
    }

    pull_parameters = collection.get('pull_parameters', [])

    params = get_params_template(pull_parameters)
    data.update({'pull_parameters': params})
    if not params:
        data.update({'wizard':  ''})
    else:
        model_fields = get_model_fields_template(pull_parameters)
        data.update({'model_fields': model_fields})
        model_getters = get_model_getters_template(pull_parameters).format(
            **collection
        )
        data.update({'model_getters': model_getters})
        model_setters = get_model_setters_template(pull_parameters).format(
            **collection
        )
        data.update({'model_setters': model_setters})
        view_fields = get_view_fields_template(pull_parameters)
        data.update({'view_fields': view_fields})

    print data
    print

    os.removedirs(tmp_dir)


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