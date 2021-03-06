# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six

from anvil import colorizer
from anvil import log as logging
from anvil import utils

LOG = logging.getLogger(__name__)


class Persona(object):

    def __init__(self, supports, components, **kargs):
        self.distro_support = supports or []
        self.source = kargs.get('source')
        self.wanted_components = components or []
        self.wanted_subsystems = kargs.get('subsystems') or {}
        self.component_options = kargs.get('options') or {}
        self.no_origins = kargs.get('no-origin') or []

    def verify(self, distro, origins_fn):
        # Filter out components that are disabled in origins file
        origins = utils.load_yaml(origins_fn)
        for c in self.wanted_components:
            if c not in origins:
                if c in self.no_origins:
                    LOG.debug("Automatically enabling component %s, not"
                              " present in origins file %s but present in"
                              " desired persona %s (origin not required).",
                              c, origins_fn, self.source)
                    origins[c] = {
                        'disabled': False,
                    }
                else:
                    LOG.warn("Automatically disabling %s, not present in"
                             " origin file but present in desired"
                             " persona (origin required).",
                             colorizer.quote(c, quote_color='red'))
                    origins[c] = {
                        'disabled': True,
                    }
        disabled_components = set(key
                                  for key, value in six.iteritems(origins)
                                  if value.get('disabled'))
        self.wanted_components = [c for c in self.wanted_components
                                  if c not in disabled_components]

        # Some sanity checks against the given distro/persona
        d_name = distro.name
        if d_name not in self.distro_support:
            raise RuntimeError("Persona does not support the loaded distro")
        for c in self.wanted_components:
            if not distro.known_component(c):
                raise RuntimeError("Persona provided component %s but its not supported by the loaded distro" % (c))


def load(fn):
    cls_kvs = utils.load_yaml(fn)
    cls_kvs['source'] = fn
    instance = Persona(**cls_kvs)
    return instance
