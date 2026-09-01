#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
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
"""Small adapter for language-owned help corpora.

sumIDE owns the help user interface, while each language package owns its
actual reference material.  A help module implements ``index_markdown()``,
``topic_names()`` and ``find_topic(name)``.  Topics expose ``name``,
``category``, ``summary``, ``example`` and ``markdown()``.
""";
from importlib import import_module;


class LanguageHelpUnavailable(RuntimeError):
    pass;


class ModuleHelpProvider:
    def __init__(self, language, label, module_name):
        self.language = str(language);
        self.label = str(label);
        self.module_name = str(module_name);
        self.module = import_module(self.module_name);
        for name in ("index_markdown", "topic_names", "find_topic"):
            if not callable(getattr(self.module, name, None)):
                raise LanguageHelpUnavailable("{} does not provide {}()".format(self.module_name, name));

    @property
    def title(self):
        return "{} Help".format(self.label);

    def index_markdown(self):
        return str(self.module.index_markdown());

    def topic_names(self):
        return tuple(self.module.topic_names());

    def find_topic(self, name):
        return self.module.find_topic(name);


def load_language_help(profile):
    if profile is None or not getattr(profile, "help_module", ""):
        return None;
    try:
        return ModuleHelpProvider(profile.id, profile.label, profile.help_module);
    except (ImportError, AttributeError, LanguageHelpUnavailable) as exc:
        raise LanguageHelpUnavailable("{} help is unavailable: {}".format(profile.label, exc)) from exc;
