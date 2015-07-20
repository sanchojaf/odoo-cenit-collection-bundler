#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  config.py
#
#  Copyright 2015 D.H. Bahr <dhbahr@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import logging

from openerp import models, fields


_logger = logging.getLogger(__name__)

COLLECTION_NAME = "{name}"
COLLECTION_VERSION = "{shared_version}"
COLLECTION_PARAMS = {{
    {pull_parameters}
}}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.{name}.settings"
    _inherit = 'res.config.settings'

    {model_fields}

    {model_getters}

    {model_setters}

    def execute(self, cr, uid, ids, context=None):
        rc = super(CenitIntegrationSettings, self).execute(
            cr, uid, ids, context=context
        )

        if not context.get('install', False):
            return rc

        objs = self.browse(cr, uid, ids)
        if not objs:
            return rc
        obj = objs[0]

        installer = self.pool.get('cenit.collection.installer')
        data = installer.get_collection_data(
            cr, uid,
            COLLECTION_NAME,
            version = COLLECTION_VERSION,
            context = context
        )

        params = {{}}
        for p in data.get('params'):
            k = p.get('parameter')
            id_ = p.get('id')
            value = getattr(obj,
                COLLECTION_PARAMS.get(k)
            )
            params.update ({{
                id_: value
            }})

        installer.install_collection(
            cr, uid,
            data.get('id'),
            params = params,
            context = context
        )

        return rc
