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
"""Central sumIDE configuration.""";
import json;
import os;
import shutil;
import sys;
from pathlib import Path;


SCHEMA_VERSION = 1;


def default_config_path():
    base = os.environ.get("XDG_CONFIG_HOME");
    if base:
        return Path(base).expanduser() / "sumide" / "config.json";
    return Path("~/.config/sumide/config.json").expanduser();


def defaults():
    return {
        "schema_version": SCHEMA_VERSION,
        "general": {"default_language": "python", "restore_session": True, "confirm_exit": False, "theme": "ZX"},
        "editor": {
            "tab_width": 4,
            "indent_width": 4,
            "soft_tab_width": 4,
            "expand_tabs": True,
            "shiftround": False,
            "line_wrapping": -1,
            "line_breaking": 0,
            "syntax_highlighting": True,
            "show_spaces": False,
            "show_tabs": False,
            "show_line_endings": False,
            "show_control_chars": False,
            "read_vim_modelines": True,
            "modeline_lines": 5,
        },
        "files": {
            "encoding": "utf-8",
            "eol": "LF",
            "ensure_final_newline": True,
            "consistent_line_endings": True,
            "strip_trailing_whitespace": False,
            "replace_tabs_on_save": False,
        },
        "templates": {
            "author": "William Martinez Bas",
            "email": "metfar@gmail.com",
            "company": "",
            "initial_version": "1.0",
        },
        "keybindings": {},
        "terminal": {"shell": os.environ.get("SHELL", "/bin/bash"), "scrollback": 500},
        "languages": {
            "html": {"tab_width": 2, "indent_width": 2, "soft_tab_width": 2, "expand_tabs": True},
            "python": {"runtime": "python", "executable": ""},
            "r": {"runtime": "sumR", "executable": ""},
        },
    };


def _merge(base, override):
    result = dict(base);
    for key, value in dict(override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value);
        else:
            result[key] = value;
    return result;


def load_config(path=None):
    target = Path(path).expanduser() if path else default_config_path();
    data = {};
    try:
        data = json.loads(target.read_text(encoding="utf-8"));
    except (OSError, ValueError, TypeError):
        data = {};
    return _merge(defaults(), data if isinstance(data, dict) else {});


def save_config(data, path=None):
    target = Path(path).expanduser() if path else default_config_path();
    target.parent.mkdir(parents=True, exist_ok=True);
    payload = _merge(defaults(), data or {});
    payload["schema_version"] = SCHEMA_VERSION;
    temporary = target.with_name(target.name + ".tmp");
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8");
    temporary.replace(target);
    return target;


def detect_initial_python():
    return shutil.which("python") or shutil.which("python3") or sys.executable;

def resolve_language_runner(config, language):
    languages=dict((config or {}).get("languages", {}) or {});
    key=str(language).lower(); settings=dict(languages.get(key,{}) or {});
    if key == "python":
        runtime=str(settings.get("runtime","python") or "python");
        if runtime.lower()=="sumpy": return [shutil.which("sumPY") or shutil.which("sumpy") or "sumPY"];
        executable=str(settings.get("executable","") or "").strip() or detect_initial_python(); return [executable];
    if key == "r":
        runtime=str(settings.get("runtime","sumR") or "sumR");
        if runtime.lower()=="rscript": return [str(settings.get("executable","") or shutil.which("Rscript") or "Rscript"), "--vanilla"];
        return [str(settings.get("executable","") or shutil.which("sumR") or shutil.which("sumr") or "sumR")];
    return [];
