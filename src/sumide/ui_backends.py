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

import importlib.util;

from sumtui import TUI_BACKEND;


DEFAULT_UI_BACKEND = "tui";


def gui_available():
    return importlib.util.find_spec("sumgui") is not None and importlib.util.find_spec("pygame") is not None;


def available_backend_names():
    names = ["tui"];
    if gui_available():
        names.append("gui");
    return tuple(names);


def backend_capabilities(name="tui"):
    key = str(name or DEFAULT_UI_BACKEND).strip().lower();
    if key == "tui":
        return TUI_BACKEND;
    if key == "gui":
        if not gui_available():
            raise RuntimeError("sumGUI/Pygame backend is not installed");
        from sumgui import GUI_BACKEND;
        return GUI_BACKEND;
    raise ValueError("Unknown Sum UI backend: {}".format(name));
