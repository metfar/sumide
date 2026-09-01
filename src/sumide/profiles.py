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
"""Language profiles for sumIDE.""";
from dataclasses import dataclass;
from pathlib import Path;


@dataclass(frozen=True)
class LanguageProfile:
    id: str;
    label: str;
    extensions: tuple;
    tab_width: int = 4;
    indent_width: int = 4;
    expand_tabs: bool = True;
    template: str = "default";
    syntax: str = "text";
    runner: tuple = ();
    aliases: tuple = ();
    help_module: str = "";


_PROFILES = {
    "bash": LanguageProfile("bash", "Bash", (".sh", ".bash"), syntax="bash", runner=("bash", "{source}"), aliases=("sh", "shell")),
    "basic": LanguageProfile("basic", "BASIC", (".bas", ".basic"), syntax="basic", runner=("python-module", "sumbasic", "--run", "{source}"), aliases=("sumbasic",), help_module="sumbasic.helpdb"),
    "c": LanguageProfile("c", "C", (".c", ".h"), syntax="c"),
    "cpp": LanguageProfile("cpp", "C++", (".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"), syntax="cpp", aliases=("cxx", "c++", "cc")),
    "html": LanguageProfile("html", "HTML", (".html", ".htm"), tab_width=2, indent_width=2, syntax="html"),
    "javascript": LanguageProfile("javascript", "JavaScript", (".js", ".mjs", ".cjs"), syntax="javascript", runner=("node", "{source}"), aliases=("js",)),
    "php": LanguageProfile("php", "PHP", (".php", ".phtml"), syntax="php", runner=("php", "{source}")),
    "python": LanguageProfile("python", "Python", (".py", ".pyw"), syntax="python", runner=("python", "{source}"), aliases=("py", "python3")),
    "r": LanguageProfile("r", "R", (".r", ".R"), syntax="r", runner=("Rscript", "--vanilla", "{source}"), aliases=("rscript",)),
    "ruby": LanguageProfile("ruby", "Ruby", (".rb", ".ruby"), syntax="ruby", runner=("ruby", "{source}"), aliases=("rb",)),
    "xbase": LanguageProfile("xbase", "xBase", (".prg", ".ch"), syntax="xbase", runner=("python-module", "sumx", "--run", "{source}"), aliases=("sumx", "dbase"), help_module="sumx.helpdb"),
};

_ALIASES = {};
for _profile in _PROFILES.values():
    _ALIASES[_profile.id] = _profile.id;
    for _alias in _profile.aliases:
        _ALIASES[str(_alias).lower()] = _profile.id;


def canonical_language(value):
    key = str(value or "auto").strip().lower();
    if key in ("", "auto", "text", "plain"):
        return "auto";
    return _ALIASES.get(key, key);


def get_profile(value):
    key = canonical_language(value);
    if key == "auto":
        return None;
    if key not in _PROFILES:
        raise ValueError("Unknown sumIDE language profile: {}".format(value));
    return _PROFILES[key];


def language_choices():
    return tuple(sorted(_PROFILES));


def all_profiles():
    return tuple(_PROFILES[key] for key in sorted(_PROFILES));


def language_from_path(path, fallback="python"):
    name = str(path or "");
    suffix = Path(name).suffix;
    suffix_lower = suffix.lower();
    for profile in _PROFILES.values():
        if suffix in profile.extensions or suffix_lower in tuple(str(item).lower() for item in profile.extensions):
            return profile.id;
    return canonical_language(fallback) if canonical_language(fallback) != "auto" else "python";
