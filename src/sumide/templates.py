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
"""Template discovery and expansion for File -> New.""";
from datetime import datetime;
import os;
from pathlib import Path;
import re;


_TOKEN_RE = re.compile(r"\$\{([A-Z0-9_]+)\}|<([A-Za-z0-9_]+)>");


def user_template_root():
    base = os.environ.get("XDG_CONFIG_HOME");
    if base:
        return Path(base).expanduser() / "sumide" / "templates";
    return Path("~/.config/sumide/templates").expanduser();


class TemplateManager:
    def __init__(self, config=None, packaged_root=None, user_root=None):
        self.config = dict(config or {});
        self.packaged_root = Path(packaged_root) if packaged_root else Path(__file__).with_name("templates");
        self.user_root = Path(user_root).expanduser() if user_root else user_template_root();

    def path_for(self, language, name="default"):
        relative = Path(str(language)) / (str(name) + ".tpl");
        custom = self.user_root / relative;
        if custom.exists():
            return custom;
        packaged = self.packaged_root / relative;
        if packaged.exists():
            return packaged;
        raise FileNotFoundError("No template {} for {}".format(name, language));

    def available(self, language):
        names = set();
        for root in (self.packaged_root, self.user_root):
            folder = root / str(language);
            if folder.exists():
                names.update(path.stem for path in folder.glob("*.tpl"));
        return tuple(sorted(names));

    def context(self, filename=None, language=None, extra=None):
        now = datetime.now().astimezone();
        filename = str(filename or "Untitled");
        path = Path(filename);
        data = {
            "FILE": filename,
            "FILENAME": path.name,
            "BASENAME": path.stem,
            "EXTENSION": path.suffix,
            "AUTHOR": str(self.config.get("author", "William Martinez Bas")),
            "EMAIL": str(self.config.get("email", "metfar@gmail.com")),
            "COMPANY": str(self.config.get("company", "")),
            "VERSION": str(self.config.get("initial_version", "1.0")),
            "YEAR": now.strftime("%Y"),
            "DATE": now.strftime("%Y-%m-%d"),
            "DATETIME": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "LANGUAGE": str(language or "text"),
            "CURSOR": "",
        };
        data.update({str(key).upper(): str(value) for key, value in dict(extra or {}).items()});
        return data;

    def render(self, language, name="default", filename=None, extra=None):
        source = self.path_for(language, name).read_text(encoding="utf-8");
        context = self.context(filename=filename, language=language, extra=extra);
        def replace(match):
            key = (match.group(1) or match.group(2) or "").upper();
            return context.get(key, match.group(0));
        return _TOKEN_RE.sub(replace, source);
