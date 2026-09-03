#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
from sumide.config import defaults, detect_initial_python, resolve_language_runner;

def test_python_initial_resolution():
    assert detect_initial_python();
    assert resolve_language_runner(defaults(), "python")[0];

def test_r_defaults_to_sumr():
    command=resolve_language_runner(defaults(), "r");
    assert command[0].endswith("sumR") or command[0].endswith("sumr");

def test_rscript_is_selectable():
    config=defaults(); config["languages"]["r"]={"runtime":"Rscript","executable":"/opt/R/bin/Rscript"};
    assert resolve_language_runner(config,"r")[:2]==["/opt/R/bin/Rscript","--vanilla"];

def test_specific_python_is_selectable():
    config=defaults(); config["languages"]["python"]={"runtime":"python","executable":"/tmp/venv/bin/python"};
    assert resolve_language_runner(config,"python")==["/tmp/venv/bin/python"];
