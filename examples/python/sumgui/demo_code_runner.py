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

import contextlib;
import io;
import os;
import sys;
import math;
import pygame;
import traceback;

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if ROOT not in sys.path:
    sys.path.insert(0, ROOT);

from sumgui.easy import alert, button, label, start, terminal, textarea, window;

CODE = '''print("Hello from SumGUI terminal")
for i in range(5):
    print("line", i)

# Try exceptions too:
# raise ValueError("Example error")
''';


def main():
    fs=30;
    window("SumGUI code runner", width=720, height=700, base_width=720, base_height=700, font_size=fs, theme="dark");
    label("Code editor + terminal", 20, 15, 580, 50, bold=True);
    label("Run executes the editor text with stdout/stderr captured below.", 20, 42, 660, 24, font_size=fs);

    editor = textarea(
        20,
        70,
        660,
        300,
        text=CODE,
        accepts_tab=True,
        tab_size=4,
        syntax="python",
        show_v_scrollbar=True,
        show_h_scrollbar=True,
        font_size=fs,
    );

    term = terminal(
        20,
        430,
        660,
        235,
        text="$ Ready. Press RUN to execute code.",
        font_size=fs,
        show_v_scrollbar=True,
        show_h_scrollbar=True,
    );

    def run_code():
        stdout = io.StringIO();
        stderr = io.StringIO();
        code = editor.text();
        term.clear();
        term.append("$ python <editor>", color="prompt");
        namespace = {
            "__name__": "__sumgui_user_code__",
            "alert": alert,
        };
        try:
            with contextlib.redirect_stdout(stdout):
                with contextlib.redirect_stderr(stderr):
                    exec(compile(code, "<sumgui-editor>", "exec"), namespace, namespace);
        except Exception:
            stderr.write(traceback.format_exc());
        out_text = stdout.getvalue().rstrip("\n");
        err_text = stderr.getvalue().rstrip("\n");
        if out_text:
            term.append(out_text, color="stdout");
        if err_text:
            term.append(err_text, color="stderr");
        if not out_text and not err_text:
            term.append("Program finished with no output.", color="info");
        term.append("$ done", color="success");

    def clear_terminal():
        term.clear();
        term.append("$ cleared", color="prompt");

    button("RUN", 20, 382, 120, 38, do=run_code, font_size=fs);
    button("CLEAR", 155, 382, 190, 38, do=clear_terminal, font_size=fs);
    button("ABOUT", 360, 382, 120, 38, do=lambda: alert("This is a tiny SumGUI code runner demo.", "About"), font_size=fs);
    start();


if __name__ == "__main__":
    main();
