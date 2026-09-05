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
"""sumIDE multi-language source IDE built on the reusable sumTUI workspace.""";
import argparse;
import code;
import contextlib;
import io;
import os;
from pathlib import Path;
import queue;
import shlex;
import shutil;
import subprocess;
import sys;
import tempfile;
import threading;
import time;

from sumui import add_backend_arguments, backend_from_args;

from sumtui.document import TextDocument;
from sumtui.symbols import detect_language;
from sumtui.modeline import scan_vim_modelines;
from sumtui.widgets import Button, CommandWindow, CommandWindowPane, Dialog, FileDialog, FunctionAction, HBox, Label, ListView, ListViewPane, MarkdownView, MarkdownViewPane, Menu, MenuItem, Separator, StatusBar, TextEditor, TextInput, TextView, TextViewPane, VBox, Workspace, WorkspaceWindow;
from sumtui.clipboard import clipboard;
from sumtui.tools.edit import EditApp, _EditorHScroll, _EditorVScroll;

from . import __version__;
from .ui_backends import available_backend_names, backend_capabilities;
from .config import resolve_language_runner, load_config as load_ide_config, save_config as save_ide_config;
from .profiles import canonical_language, get_profile, language_choices, language_from_path;
from .templates import TemplateManager;
from .config import default_config_path;
from .preferences import open_preferences;
from .language_help import LanguageHelpUnavailable, load_language_help;


class _RSession:
    """Small persistent R process used by the direct command window.""";
    def __init__(self, executable=None):
        self.executable = executable or shutil.which("R");
        self.process = None;
        self.queue = queue.Queue();
        self.reader = None;
        self.counter = 0;
        self.lock = threading.Lock();

    @property
    def available(self):
        return bool(self.executable);

    @staticmethod
    def _quote(source):
        return str(source).replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n");

    def start(self):
        if self.process is not None and self.process.poll() is None:
            return self.process;
        if not self.executable:
            raise RuntimeError("R executable was not found in PATH");
        self.process = subprocess.Popen(
            [self.executable, "--vanilla", "--quiet", "--no-save", "--no-restore", "--slave"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        );
        def reader():
            for line in self.process.stdout:
                self.queue.put(line);
        self.reader = threading.Thread(target=reader, name="sumIDE-R-reader", daemon=True);
        self.reader.start();
        return self.process;

    def execute(self, source, timeout=30.0):
        with self.lock:
            process = self.start();
            self.counter += 1;
            marker = "__SUMIDE_R_DONE_{}__".format(self.counter);
            encoded = self._quote(source);
            command = (
                '.__sumide_expr <- try(parse(text="{}"), silent=TRUE); '
                'if (inherits(.__sumide_expr, "try-error")) {{ cat(as.character(.__sumide_expr), "\\n") }} '
                'else {{ for (.__sumide_e in .__sumide_expr) {{ .__sumide_v <- withVisible(eval(.__sumide_e, envir=.GlobalEnv)); if (.__sumide_v$visible) print(.__sumide_v$value) }} }}; '
                'cat("{}\\n"); flush.console()\n'
            ).format(encoded, marker);
            process.stdin.write(command);
            process.stdin.flush();
            lines = [];
            deadline = time.monotonic() + float(timeout);
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("R process exited with status {}".format(process.returncode));
                try:
                    line = self.queue.get(timeout=0.05);
                except queue.Empty:
                    continue;
                if line.rstrip("\r\n") == marker:
                    return "".join(lines);
                lines.append(line);
            raise TimeoutError("R direct command timed out");

    def close(self):
        process = self.process;
        self.process = None;
        if process is None:
            return False;
        try:
            if process.poll() is None:
                process.terminate();
                process.wait(timeout=1.0);
        except Exception:
            try: process.kill();
            except Exception: pass;
        return True;


class ScriptIDE(EditApp):
    """Common movable-window IDE for Python, R, Bash, C and C++ source files.""";
    def __init__(self, path=None, language="auto", theme=None, **kwargs):
        self.sumide_config_path = Path(kwargs.pop("sumide_config_path", default_config_path())).expanduser();
        self.sumide_config = load_ide_config(self.sumide_config_path);
        self.template_manager = TemplateManager(self.sumide_config.get("templates", {}));
        self._language_request = canonical_language(language);
        self.language = self._resolve_language(path, language);
        self._process = None;
        self._process_thread = None;
        self._process_queue = queue.Queue();
        self._process_done = False;
        self._process_returncode = None;
        self._process_mode = None;
        self._process_artifact_path = None;
        self._temp_path = None;
        self._temp_output_path = None;
        self._direct_thread = None;
        self._direct_done = False;
        self._direct_output = "";
        self._direct_error = None;
        self._python_console = code.InteractiveConsole({"__name__": "__console__"});
        self._code_buffers = {};
        self._code_counter = 0;
        self._r_session = _RSession();
        general_config = self.sumide_config.get("general", {});
        selected_theme = theme or general_config.get("theme");
        super().__init__(path=path, theme=selected_theme, config_path=self.sumide_config_path, **kwargs);
        self.app.title = "sumIDE";
        editor_config = self.sumide_config.get("editor", {});
        profile = get_profile(self.language);
        language_config = self.sumide_config.get("languages", {}).get(self.language, {});
        tab_width = language_config.get("tab_width", profile.tab_width if profile else editor_config.get("tab_width", 4));
        indent_width = language_config.get("indent_width", profile.indent_width if profile else editor_config.get("indent_width", tab_width));
        soft_width = language_config.get("soft_tab_width", editor_config.get("soft_tab_width", indent_width));
        try: self.editor.tab_size = max(1, int(tab_width));
        except (TypeError, ValueError): self.editor.tab_size = 4;
        try: self.editor.indent_size = max(1, int(indent_width));
        except (TypeError, ValueError): self.editor.indent_size = self.editor.tab_size;
        try: self.editor.soft_tab_size = max(1, int(soft_width));
        except (TypeError, ValueError): self.editor.soft_tab_size = self.editor.indent_size;
        self.editor.expand_tabs = bool(language_config.get("expand_tabs", profile.expand_tabs if profile else editor_config.get("expand_tabs", True)));
        self.editor.shift_round = bool(language_config.get("shiftround", editor_config.get("shiftround", False)));
        self.editor.line_wrapping = int(editor_config.get("line_wrapping", -1));
        self.editor.line_breaking = max(0, int(editor_config.get("line_breaking", 0)));
        self.editor.syntax_highlighting = bool(editor_config.get("syntax_highlighting", True));
        self.editor.configure_visibility(
            spaces=bool(editor_config.get("show_spaces", False)),
            tabs=bool(editor_config.get("show_tabs", False)),
            line_endings=bool(editor_config.get("show_line_endings", False)),
            controls=bool(editor_config.get("show_control_chars", False)),
        );
        if profile is not None:
            self.editor.configure_syntax(language=profile.syntax);
        self.ide_config = dict(self.config.get("ide", {})) if isinstance(self.config.get("ide", {}), dict) else {};
        self.output_view = TextView("Ready. F5 runs the current buffer.");
        self.command_view = CommandWindow(prompt=self._prompt(), on_submit=self._submit_direct);
        self.output_pane = TextViewPane(self.output_view);
        self.command_pane = CommandWindowPane(self.command_view);
        available_width = max(40, int(self.app.width));
        available_height = max(12, int(self.app.height) - 3);
        bottom_height = max(7, min(11, max(7, available_height // 3)));
        code_height = max(5, available_height - bottom_height);
        output_width = max(20, int(available_width * 0.62));
        command_width = max(12, available_width - output_width);
        if output_width + command_width > available_width:
            output_width = max(12, available_width - command_width);
        self.code_window = WorkspaceWindow(self.panel.child, title=self._code_title(), name="code", left=0, top=0, width=available_width, height=code_height, visible=True, content_style="viewer", persistent=True);
        self.output_window = WorkspaceWindow(self.output_pane, title="Output", name="output", left=0, top=code_height, width=output_width, height=bottom_height, visible=True, content_style="viewer", persistent=True);
        self.command_window = WorkspaceWindow(self.command_pane, title="Command", name="command", left=output_width, top=code_height, width=command_width, height=bottom_height, visible=True, content_style="command", persistent=True);
        self.workspace = Workspace(
            self.output_window,
            self.command_window,
            self.code_window,
            layout_id="sumide-v2",
            layout_path=self._workspace_layout_path(),
            viewport_width=available_width,
            viewport_height=available_height,
        );
        self._code_counter = 1;
        self._code_buffers[self.code_window] = {"document": self.document, "editor": self.editor, "vscroll": self.vscroll, "hscroll": self.hscroll, "language": self.language};
        self.workspace.on_activate = self._workspace_activated;
        self.desktop.body = VBox(self.workspace, self.status, self.bar, sizes=[None, 1, 1]);
        self.app.set_root(self.desktop);
        self.workspace.activate(self.code_window);
        self.app.add_idle(self._poll_execution);
        self.menu.menus = self._menus();
        self._update_status("{} IDE".format(self.language.upper()));

    @staticmethod
    def _resolve_language(path, language):
        requested = canonical_language(language);
        if requested != "auto":
            profile = get_profile(requested);
            return profile.id;
        detected = detect_language(filename=str(path or ""));
        try:
            detected = canonical_language(detected);
            if detected != "auto":
                return get_profile(detected).id;
        except ValueError:
            pass;
        return language_from_path(path, fallback="python");

    def _prompt(self):
        return {"python": ">>> ", "r": "R> ", "bash": "$ ", "c": "sh> ", "cpp": "sh> ", "ruby": "rb> ", "php": "php> ", "javascript": "js> ", "basic": "BASIC> ", "xbase": "xBase> "}.get(self.language, "> ");

    def _language_label(self):
        profile = get_profile(self.language);
        return profile.label if profile is not None else self.language;

    def _code_title(self):
        name = self.document.path.name if self.document.path is not None else "Untitled";
        return "Code - {} [{}]".format(name, self._language_label());

    def _code_title_for(self, document, language):
        name = document.path.name if document.path is not None else "Untitled";
        profile = get_profile(language);
        label = profile.label if profile is not None else language;
        return "Code - {} [{}]".format(name, label);

    def _document_language(self, document, fallback=None):
        if self._language_request not in ("", "auto"):
            return self._resolve_language(document.path, self._language_request);
        if document.path is None and fallback in language_choices():
            return fallback;
        return self._resolve_language(document.path, "auto");

    @staticmethod
    def _sync_markers_for(document, editor):
        if document.eol == "CRLF":
            editor.line_end_marker = "⏎";
        elif document.eol == "CR":
            editor.line_end_marker = "↩";
        else:
            editor.line_end_marker = "↵";
        markers = {"\n": "↵", "\r\n": "⏎", "\r": "↩"};
        editor.line_end_markers = [markers.get(value, "↵") for value in (document.line_endings or [])];
        return editor;

    def _make_code_editor(self, document, language=None):
        current = self.editor;
        language = language or self._document_language(document, fallback=self.language);
        profile = get_profile(language);
        editor_config = self.sumide_config.get("editor", {});
        language_config = self.sumide_config.get("languages", {}).get(language, {});
        tab_size = int(language_config.get("tab_width", profile.tab_width if profile else editor_config.get("tab_width", current.tab_size)));
        indent_size = int(language_config.get("indent_width", profile.indent_width if profile else editor_config.get("indent_width", tab_size)));
        soft_tab_size = int(language_config.get("soft_tab_width", editor_config.get("soft_tab_width", indent_size)));
        expand_tabs = bool(language_config.get("expand_tabs", profile.expand_tabs if profile else editor_config.get("expand_tabs", True)));
        shift_round = bool(language_config.get("shiftround", editor_config.get("shiftround", False)));
        syntax_language = profile.syntax if profile is not None else str(self.config.get("syntax_mode", "auto"));
        if bool(editor_config.get("read_vim_modelines", True)):
            modeline = scan_vim_modelines(document.text, editor_config.get("modeline_lines", 5));
            tab_size = int(modeline.get("tabstop", tab_size));
            indent_size = int(modeline.get("shiftwidth", indent_size));
            soft_tab_size = int(modeline.get("softtabstop", soft_tab_size));
            expand_tabs = bool(modeline.get("expandtab", expand_tabs));
            shift_round = bool(modeline.get("shiftround", shift_round));
            syntax_language = modeline.get("syntax", syntax_language);
            if "fileformat" in modeline:
                document.eol = str(modeline["fileformat"]);
                document.preferred_eol = document.eol;
            if "fileencoding" in modeline:
                document.encoding = str(modeline["fileencoding"]);
                document.encoding_label = str(modeline["fileencoding"]).upper();
        editor = TextEditor(
            document.text,
            tab_size=tab_size,
            indent_size=indent_size,
            soft_tab_size=soft_tab_size,
            expand_tabs=expand_tabs,
            shift_round=shift_round,
            line_numbers=True,
            on_change=self._editor_changed,
            on_cursor=self._cursor_changed,
            command_shortcuts=False,
            syntax_highlighting=current.syntax_highlighting,
            syntax_language=syntax_language,
            syntax_filename=document.path.name if document.path is not None else None,
            line_wrapping=current.line_wrapping,
            line_breaking=current.line_breaking,
        );
        editor.configure_visibility(
            spaces=current.show_spaces,
            tabs=current.show_tabs,
            line_endings=current.show_line_endings,
            controls=current.show_control_chars,
        );
        self._sync_markers_for(document, editor);
        vscroll = _EditorVScroll(editor);
        hscroll = _EditorHScroll(editor);
        child = VBox(HBox(editor, vscroll, sizes=[None, 1]), hscroll, sizes=[None, 1]);
        return editor, vscroll, hscroll, child;

    def _workspace_activated(self, window):
        state = self._code_buffers.get(window);
        if state is None:
            return False;
        self.document = state["document"];
        self.editor = state["editor"];
        self.vscroll = state["vscroll"];
        self.hscroll = state["hscroll"];
        self.language = state["language"];
        self.code_window = window;
        self._sync_markers_for(self.document, self.editor);
        window.title = self._code_title_for(self.document, self.language);
        if hasattr(self, "command_view"):
            self.command_view.set_prompt(self._prompt());
        if hasattr(self, "menu"):
            self.menu.menus = self._menus();
        self._update_status("Active {} source".format(self._language_label()));
        return True;

    def _add_code_document(self, document, language=None, activate=True, persistent=False):
        language = language or self._document_language(document, fallback=self.language);
        editor, vscroll, hscroll, child = self._make_code_editor(document, language=language);
        self._code_counter += 1;
        offset = (self._code_counter - 1) % 6;
        width = max(30, min(max(40, int(self.app.width)) - 2, int(max(40, int(self.app.width)) * 0.78)));
        height = max(9, min(max(12, int(self.app.height) - 3) - 1, int(max(12, int(self.app.height) - 3) * 0.72)));
        window = WorkspaceWindow(
            child,
            title=self._code_title_for(document, language),
            name="code:{}".format(self._code_counter),
            left=1 + offset * 2,
            top=offset,
            width=width,
            height=height,
            content_style="viewer",
            persistent=bool(persistent),
        );
        self._code_buffers[window] = {"document": document, "editor": editor, "vscroll": vscroll, "hscroll": hscroll, "language": language};
        self.workspace.add_window(window, activate=activate);
        if not activate:
            self.menu.menus = self._menus();
            self.app.invalidate();
        return window;

    def open_path(self, path, activate=True):
        document = TextDocument.load(Path(path).expanduser(), force_binary=self.force_binary) if Path(path).expanduser().exists() else TextDocument.empty(Path(path).expanduser());
        language = self._document_language(document, fallback=self.language);
        current = self._code_buffers.get(getattr(self, "code_window", None));
        if current is not None and self.code_window.persistent and self.document.path is None and not self.editor.modified and not self.editor.text:
            current["document"] = document;
            current["language"] = language;
            self.document = document;
            self.language = language;
            self.editor.set_text(document.text, modified=False);
            self.editor.configure_syntax(language=get_profile(language).syntax if get_profile(language) is not None else None, filename=document.path.name if document.path is not None else None);
            self._sync_markers_for(document, self.editor);
            self.code_window.title = self._code_title_for(document, language);
            self.command_view.set_prompt(self._prompt());
            self.menu.menus = self._menus();
            if activate:
                self.workspace.show(self.code_window);
                self.app.focus.set(self.editor);
            self._update_status("Loaded");
            self.app.invalidate();
            return self.code_window;
        return self._add_code_document(document, language=language, activate=activate, persistent=False);

    def _open_dialog_now(self):
        start = self.document.path.parent if self.document.path is not None else Path.cwd();
        def close():
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
        def accepted(path):
            try:
                close();
                self.open_path(path, activate=True);
            except Exception as exc:
                self._update_status("Open error: {}".format(exc));
        dialog = FileDialog(path=start, title="Open source file", on_accept=accepted, on_cancel=close, theme=self.app.theme);
        self.app.push_modal(dialog);
        self.app.invalidate();
        return True;

    def open_dialog(self):
        return self._open_dialog_now();

    def new_file(self):
        document = TextDocument.empty();
        return bool(self._add_code_document(document, language=self.language, activate=True, persistent=False));

    def _set_document(self, document):
        state = self._code_buffers.get(getattr(self, "code_window", None));
        if state is None:
            return super()._set_document(document);
        state["document"] = document;
        self.document = document;
        self.editor.set_text(document.text, modified=False);
        self.editor.configure_syntax(filename=document.path.name if document.path is not None else None);
        state["language"] = self._document_language(document, fallback=state.get("language"));
        self.language = state["language"];
        self._sync_markers_for(document, self.editor);
        self.code_window.title = self._code_title_for(document, self.language);
        self.command_view.set_prompt(self._prompt());
        self.menu.menus = self._menus();
        self.app.focus.set(self.editor);
        self._update_status("Loaded");
        return True;

    def save(self, on_saved=None):
        if self.document.path is None:
            return super().save(on_saved=on_saved);
        result = super().save(on_saved=None);
        if result:
            state = self._code_buffers.get(getattr(self, "code_window", None));
            if state is not None:
                state["document"] = self.document;
                state["language"] = self._document_language(self.document, fallback=state.get("language"));
                self.language = state["language"];
                self.code_window.title = self._code_title_for(self.document, self.language);
                self.command_view.set_prompt(self._prompt());
                self.menu.menus = self._menus();
            if on_saved is not None:
                return on_saved();
        return result;

    def _clear_persistent_code_document(self, target):
        state = self._code_buffers.get(target);
        if state is None:
            return False;
        language = state.get("language", self.language);
        document = TextDocument.empty();
        state["document"] = document;
        state["language"] = language;
        self.document = document;
        self.language = language;
        state["editor"].set_text("", modified=False);
        target.title = self._code_title_for(document, language);
        self.workspace.show(target);
        self._workspace_activated(target);
        self._update_status("Closed source document");
        self.app.invalidate();
        return True;

    def _close_code_window_now(self, target):
        state = self._code_buffers.get(target);
        if state is None:
            return self._close_workspace_window_now(target);
        if target.persistent:
            return self._clear_persistent_code_document(target);
        changed = self.workspace.remove_window(target);
        if changed:
            self._code_buffers.pop(target, None);
            self.menu.menus = self._menus();
            self._update_status("Closed source window");
            self.app.invalidate();
        return bool(changed);

    def close_workspace_window(self, window=None):
        target = window or self.workspace.active_window;
        if target is None:
            return False;
        state = self._code_buffers.get(target);
        if state is None:
            return super().close_workspace_window(target);
        self.workspace.show(target);
        self._workspace_activated(target);
        if state["editor"].modified:
            return self._confirm_unsaved(lambda: self._close_code_window_now(target));
        return self._close_code_window_now(target);

    def close_current_document(self):
        target = getattr(self, "code_window", None);
        if target is None or target not in self._code_buffers:
            self._update_status("No source document is active");
            return False;
        return self.close_workspace_window(target);

    def _confirm_all_unsaved(self, callback):
        dirty = [(window, state) for window, state in self._code_buffers.items() if state["editor"].modified];
        if not dirty:
            return callback();
        window, state = dirty[0];
        self.workspace.show(window);
        self._workspace_activated(window);
        def continue_after_choice():
            state["editor"].modified = False;
            return self._confirm_all_unsaved(callback);
        return self._confirm_unsaved(continue_after_choice);

    def quit(self):
        return self._confirm_all_unsaved(self._quit_now);

    def _register_keybindings(self):
        super()._register_keybindings();
        self.keys.set_bindings("help.editor", ["ctrl+f1"]);
        self.keys.register("help.context", "Language / editor help", ["f1"], context="editor", callback=self.context_help);
        self.keys.register("script.run", "Run / Stop", ["f5", "ctrl+r"], context="editor", callback=self.toggle_run);
        self.keys.register("script.compile", "Compile", ["ctrl+f6"], context="editor", callback=self.compile_program);
        self.keys.register("menu.run", "Run menu", ["alt+r"], context="editor", callback=lambda: self.open_menu(6));
        self.keys.register("menu.help", "Help menu", ["alt+h"], context="editor", callback=lambda: self.open_menu(7));
        return self.keys;

    def _make_function_bar(self):
        bar = super()._make_function_bar();
        context_key = self.keys.primary("help.context");
        if context_key:
            for action in bar.actions:
                if action.label == "Help":
                    action.key = context_key;
                    break;
        key = self.keys.primary("script.run");
        if key:
            bar.actions.insert(min(2, len(bar.actions)), FunctionAction(key, "Run/Stop", None));
        return bar;

    def _comparison_overrides(self, paths):
        wanted = {Path(path).expanduser().resolve() for path in paths};
        overrides = {};
        for state in self._code_buffers.values():
            document = state["document"];
            if document.path is None:
                continue;
            path = Path(document.path).expanduser().resolve();
            if path in wanted:
                overrides[path] = state["editor"].text;
        return overrides;

    def _comparison_finished(self, compare_app):
        saved = {Path(path).expanduser().resolve() for path in getattr(compare_app, "saved_paths", set())};
        if not saved:
            return True;
        changed = False;
        for window, state in list(self._code_buffers.items()):
            document = state["document"];
            if document.path is None:
                continue;
            path = Path(document.path).expanduser().resolve();
            if path not in saved:
                continue;
            try:
                loaded = TextDocument.load(path, force_binary=self.force_binary);
                state["document"] = loaded;
                state["editor"].set_text(loaded.text, modified=False);
                state["editor"].configure_syntax(filename=loaded.path.name if loaded.path is not None else None);
                state["language"] = self._document_language(loaded, fallback=state.get("language"));
                window.title = self._code_title_for(loaded, state["language"]);
                changed = True;
            except Exception as exc:
                self._update_status("Compare reload error: {}".format(exc));
        if getattr(self, "code_window", None) in self._code_buffers:
            self._workspace_activated(self.code_window);
        if changed:
            self._update_status("Reloaded files saved by sumdiff");
        return True;

    def _compare_open_buffer(self, window):
        current = self._code_buffers.get(self.code_window);
        other = self._code_buffers.get(window);
        if current is None or other is None:
            return False;
        if current["document"].path is None or other["document"].path is None or not Path(current["document"].path).expanduser().exists() or not Path(other["document"].path).expanduser().exists():
            self._update_status("Save both buffers before comparing them");
            return False;
        return self._launch_comparison([current["document"].path, other["document"].path], mode="compare");

    def _compare_open_buffer_menu(self):
        items = [];
        for window, state in self._code_buffers.items():
            if window is self.code_window:
                continue;
            document = state["document"];
            label = document.path.name if document.path is not None else "Untitled";
            items.append(MenuItem(label, lambda selected=window: self._compare_open_buffer(selected), enabled=document.path is not None and Path(document.path).expanduser().exists()));
        if not items:
            items.append(MenuItem("No other saved buffers", enabled=False));
        return Menu("Compare with open buffer", items);

    def compare_all_open_documents(self):
        states = [state for state in self._code_buffers.values() if state["document"].path is not None and Path(state["document"].path).expanduser().exists()];
        if len(states) < 2:
            self._update_status("Open at least two saved documents to compare");
            return False;
        paths = [state["document"].path for state in states];
        mode = "compare" if len(paths) == 2 else "parallel";
        return self._launch_comparison(paths, mode=mode);

    def _language_help_profile(self):
        return get_profile(self.language);

    def _language_help_provider(self):
        profile = self._language_help_profile();
        if profile is None or not getattr(profile, "help_module", ""):
            return None;
        return load_language_help(profile);

    def _show_language_help(self, provider):
        current = {"topic": None};
        viewer = MarkdownView(provider.index_markdown());
        names = list(provider.topic_names());

        def show_topic(value, _row=None):
            topic = provider.find_topic(value);
            if topic is None:
                return False;
            current["topic"] = topic;
            viewer.set_text(topic.markdown());
            self.app.invalidate();
            return True;

        topics = ListView([(name, name) for name in names], title="Topics", on_change=show_topic, on_activate=show_topic);

        def close(*_args):
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self._update_status();
            self.app.invalidate();
            return True;

        def copy_example(*_args):
            topic = current.get("topic");
            if topic is not None and getattr(topic, "example", ""):
                clipboard.copy_text(topic.example);
                hints.set("Example copied: {}".format(topic.name));
            elif viewer.copy_code_block(-1):
                hints.set("Code example copied");
            else:
                clipboard.copy_text(viewer.markdown);
                hints.set("Help text copied");
            self.app.invalidate();
            return True;

        def search(*_args):
            entry = TextInput("");
            search_status = StatusBar("Enter searches topic names and summaries; Esc closes");

            def search_close(*_values):
                self.app.pop_modal();
                self.app.focus.set(topics);
                self.app.invalidate();
                return True;

            def accepted(value=None, *_values):
                needle = str(entry.value if value is None else value).strip().casefold();
                if not needle:
                    return False;
                for index, name in enumerate(names):
                    topic = provider.find_topic(name);
                    haystack = "{} {} {}".format(name, getattr(topic, "category", ""), getattr(topic, "summary", "")).casefold();
                    if needle in haystack:
                        topics.select(index);
                        show_topic(name);
                        search_close();
                        return True;
                search_status.set("No help topic contains: {}".format(needle));
                self.app.invalidate();
                return False;

            entry.on_submit = accepted;
            body = VBox(Label("Search help:"), entry, search_status, HBox(Button("Find", on_press=accepted, default=True), Button("Cancel", on_press=search_close), ratios=[1, 1]), sizes=[1, 1, 1, None]);
            dialog = Dialog(body, title="{} Search".format(provider.label), width=70, height=10, on_cancel=search_close, shadow=True);
            self.app.push_modal(dialog);
            self.app.focus.set(entry);
            self.app.invalidate();
            return True;

        def topic_map(*_args):
            rows = [];
            current_index = 0;
            current_topic = current.get("topic");
            for index, name in enumerate(names):
                topic = provider.find_topic(name);
                category = getattr(topic, "category", "") if topic is not None else "";
                rows.append(("{} / {}".format(category, name) if category else name, name));
                if current_topic is not None and name == current_topic.name:
                    current_index = index;
            listing = ListView(rows, title="Category / Topic");
            listing.select(current_index);

            def map_close(*_values):
                self.app.pop_modal();
                self.app.focus.set(topics);
                self.app.invalidate();
                return True;

            def map_activate(*_values):
                name = listing.current_value;
                if name is None:
                    return False;
                for index, topic_name in enumerate(names):
                    if topic_name == name:
                        topics.select(index);
                        break;
                show_topic(name);
                return map_close();

            listing.on_activate = map_activate;
            listing_pane = ListViewPane(listing, theme=self.app.theme);
            map_status = StatusBar("Enter Go to topic  Esc Return to help");
            map_body = VBox(listing_pane, map_status, sizes=[None, 1]);
            map_dialog = Dialog(map_body, title="{} Topic Map".format(provider.label), width=72, height=min(28, max(12, len(rows) + 6)), on_cancel=map_close, shadow=True);
            self.app.push_modal(map_dialog);
            self.app.focus.set(listing);
            self.app.invalidate();
            return True;

        hints = StatusBar("F2 Topic Map  Tab Topic/Text  F3 Search  F6/Ctrl+C Copy Example  F11 Max/Restore  Esc Close");
        topics_pane = ListViewPane(topics, theme=self.app.theme);
        viewer_pane = MarkdownViewPane(view=viewer, theme=self.app.theme);
        body = HBox(topics_pane, viewer_pane, sizes=[28, None]);
        content = VBox(body, hints, sizes=[None, 1]);
        dialog = Dialog(content, title=provider.title, width=104, height=30, on_cancel=close, padding=(0, 1), maximizable=True);
        self.app.push_modal(dialog, bindings={"f2": topic_map, "f3": search, "f6": copy_example, "ctrl+c": copy_example});
        self.app.focus.set(topics);
        self._update_status("{} help".format(provider.label));
        self.app.invalidate();
        return True;

    def language_help(self):
        profile = self._language_help_profile();
        if profile is None:
            return self.help();
        if not getattr(profile, "help_module", ""):
            self._update_status("No bundled {} language reference; showing editor help".format(profile.label));
            return self.help();
        try:
            provider = self._language_help_provider();
        except LanguageHelpUnavailable as exc:
            self._update_status(str(exc));
            return self._show_text_dialog("{} Help".format(profile.label), str(exc) + "\n\nThe language package may not be installed in this environment.");
        if provider is None:
            return self.help();
        return self._show_language_help(provider);

    def context_help(self):
        return self.language_help();

    def _menus(self):
        menus = super()._menus();
        file_menu = next((menu for menu in menus if menu.title == "File"), None);
        if file_menu is not None:
            if file_menu.items:
                file_menu.items[0] = MenuItem("New", submenu=self._new_template_menu());
            save_as_index = next((index for index, item in enumerate(file_menu.items) if getattr(item, "label", "") == "Save As..."), 3);
            file_menu.items.insert(save_as_index + 1, MenuItem("Close", self.close_current_document, self._ks("window.close")));
            compare_index = next((index for index, item in enumerate(file_menu.items) if getattr(item, "label", "") == "Compare with..."), save_as_index + 3);
            file_menu.items.insert(compare_index + 1, MenuItem("Compare with open buffer", submenu=self._compare_open_buffer_menu()));
            file_menu.items.insert(compare_index + 2, MenuItem("Compare all open documents", self.compare_all_open_documents, enabled=len([state for state in self._code_buffers.values() if state["document"].path is not None and Path(state["document"].path).expanduser().exists()]) >= 2));
        run_items = [
            MenuItem("Run / Stop current buffer", self.toggle_run, self._ks("script.run")),
            MenuItem("Clear output", self.clear_output),
        ];
        if self.language in ("c", "cpp"):
            run_items.insert(1, MenuItem("Compile current buffer", self.compile_program, self._ks("script.compile")));
            run_items.insert(2, MenuItem("Build commands...", self.build_commands_dialog));
        run_menu = Menu("Run", run_items);
        options = next((menu for menu in menus if menu.title == "Options"), None);
        if options is not None:
            options.items.insert(0, MenuItem("Preferences...", self.preferences_dialog));
            options.items.insert(1, Separator());
            if self.language in ("c", "cpp"):
                options.items.insert(2, MenuItem("C/C++ build commands...", self.build_commands_dialog));
                options.items.insert(3, Separator());
        help_menu = next((menu for menu in menus if menu.title == "Help"), None);
        if help_menu is not None:
            profile = self._language_help_profile();
            if profile is not None and getattr(profile, "help_module", ""):
                help_menu.items = [
                    MenuItem("{} Help".format(profile.label), self.context_help, self._ks("help.context")),
                    MenuItem("Editor Help", self.help, self._ks("help.editor")),
                    Separator(),
                    MenuItem("About...", self.about),
                ];
            else:
                help_menu.items = [
                    MenuItem("Editor Help", self.context_help, self._ks("help.context")),
                    Separator(),
                    MenuItem("About...", self.about),
                ];
        help_index = next((index for index, menu in enumerate(menus) if menu.title == "Help"), len(menus));
        menus.insert(help_index, run_menu);
        return menus;

    def _new_template_menu(self):
        items = [MenuItem("Empty file", self.new_file)];
        items.append(Separator());
        for language in language_choices():
            profile = get_profile(language);
            items.append(MenuItem(profile.label, lambda selected=language: self.new_from_template(selected)));
        return Menu("New", items);

    def new_from_template(self, language, template="default"):
        profile = get_profile(language);
        filename = "Untitled{}".format(profile.extensions[0] if profile.extensions else "");
        try:
            text = self.template_manager.render(profile.id, template, filename=filename);
        except Exception as exc:
            self._update_status("Template error: {}".format(exc));
            return False;
        document = TextDocument.empty();
        document.text = text;
        document.final_newline = text.endswith("\n");
        window = self._add_code_document(document, language=profile.id, activate=True, persistent=False);
        state = self._code_buffers.get(window);
        if state is not None:
            state["editor"].set_text(text, modified=True);
            state["editor"].tab_size = int(self.sumide_config.get("languages", {}).get(profile.id, {}).get("tab_width", profile.tab_width));
            state["editor"].configure_syntax(language=profile.syntax);
        self._update_status("New {} document from template".format(profile.label));
        return True;

    def preferences_dialog(self):
        return open_preferences(self);

    def _menu_closed(self):
        if hasattr(self, "workspace") and self.workspace.active_window is not None:
            focus = self.workspace.active_window.primary_focus();
            if focus is not None:
                self.app.focus.set(focus);
                self.app.invalidate();
                return True;
        return super()._menu_closed();

    def clear_output(self):
        self.output_view.set_text("");
        self.app.invalidate();
        return True;

    def _append_output(self, text):
        piece = str(text);
        if self.output_view.text == "Ready. F5 runs the current buffer.":
            self.output_view.set_text("");
        self.output_view.append_text(piece);
        return True;

    def _temporary_source(self):
        profile = get_profile(self.language);
        suffix = profile.extensions[0] if profile and profile.extensions else ".txt";
        directory = self.document.path.parent if self.document.path is not None else Path.cwd();
        handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=suffix, prefix=".sumide-", dir=str(directory), delete=False);
        try:
            handle.write(self.editor.text);
            handle.flush();
            return Path(handle.name);
        finally:
            handle.close();

    def _runner_command(self, path):
        profile = get_profile(self.language);
        if profile is None or not profile.runner:
            raise RuntimeError("{} does not define a run command".format(self._language_label()));
        configured = resolve_language_runner(self.sumide_config, profile.id);
        if profile.id in ("python", "r") and configured:
            parts = configured + ["{source}"];
        else:
            parts = list(profile.runner);
        if parts and parts[0] == "python":
            parts[0] = sys.executable;
        elif parts and parts[0] == "python-module":
            if len(parts) < 2:
                raise RuntimeError("Invalid python-module runner for {}".format(profile.id));
            parts = [sys.executable, "-m", parts[1]] + parts[2:];
        elif parts:
            executable = shutil.which(parts[0]);
            if not executable:
                raise RuntimeError("{} was not found in PATH".format(parts[0]));
            parts[0] = executable;
        return [str(item).format(source=str(path)) for item in parts];

    def _build_defaults(self):
        c_compiler = "gcc" if os.name == "nt" else "cc";
        cpp_compiler = "g++" if os.name == "nt" else "c++";
        return {
            "c_compile": '{} -std=c17 -Wall -Wextra -O0 -g {{source}} -o {{output}}'.format(c_compiler),
            "c_run": '{output}',
            "cpp_compile": '{} -std=c++17 -Wall -Wextra -O0 -g {{source}} -o {{output}}'.format(cpp_compiler),
            "cpp_run": '{output}',
        };

    def _build_value(self, key):
        return str(self.ide_config.get(key, self._build_defaults()[key]));

    @staticmethod
    def _quote_build_path(value):
        return subprocess.list2cmdline([str(value)]) if os.name == "nt" else shlex.quote(str(value));

    def _expanded_build(self, template, source, output):
        return str(template).format(source=self._quote_build_path(source), output=self._quote_build_path(output));

    @staticmethod
    def _shell_command(command):
        if os.name == "nt":
            shell = os.environ.get("COMSPEC") or shutil.which("cmd.exe") or "cmd.exe";
            return [shell, "/c", str(command)];
        shell = shutil.which("sh") or "/bin/sh";
        return [shell, "-c", str(command)];

    @staticmethod
    def _executable_suffix():
        return ".exe" if os.name == "nt" else ".run";

    def compiled_output_path(self):
        suffix = self._executable_suffix();
        if self.document.path is not None:
            return self.document.path.with_suffix(suffix);
        return Path.cwd() / ("untitled" + suffix);

    def build_commands_dialog(self):
        defaults = self._build_defaults();
        entries = {key: TextInput(self._build_value(key)) for key in ("c_compile", "c_run", "cpp_compile", "cpp_run")};
        rows = [];
        labels = (("C compile", "c_compile"), ("C run", "c_run"), ("C++ compile", "cpp_compile"), ("C++ run", "cpp_run"));
        for label, key in labels:
            rows.append(HBox(Label(label), entries[key], sizes=[14, None]));
        def close(*_args):
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
            return True;
        def save_values(*_args):
            for key, entry in entries.items():
                value = str(entry.value).strip();
                self.ide_config[key] = value or defaults[key];
            close();
            self._update_status("Build commands updated; Options -> Save configuration persists them.");
            return True;
        body = VBox(*rows, HBox(Button("OK", on_press=save_values, default=True, height=3), Button("Cancel", on_press=close, height=3), ratios=[1, 1]), sizes=[1, 1, 1, 1, None]);
        self.app.push_modal(Dialog(body, title="C/C++ build commands", width=90, height=13, on_cancel=close, shadow=True));
        self.app.focus.set(entries["c_compile"] if self.language == "c" else entries["cpp_compile"]);
        self.app.invalidate();
        return True;

    def save_config(self):
        data = dict(self.sumide_config);
        general = dict(data.get("general", {}));
        general["theme"] = self.app.theme.name;
        data["general"] = general;
        editor = dict(data.get("editor", {}));
        editor.update({
            "tab_width": int(self.editor.tab_size),
            "indent_width": int(getattr(self.editor, "indent_size", self.editor.tab_size)),
            "soft_tab_width": int(getattr(self.editor, "soft_tab_size", self.editor.tab_size)),
            "expand_tabs": bool(getattr(self.editor, "expand_tabs", True)),
            "shiftround": bool(getattr(self.editor, "shift_round", False)),
            "line_wrapping": int(self.editor.line_wrapping),
            "line_breaking": int(self.editor.line_breaking),
            "syntax_highlighting": bool(self.editor.syntax_highlighting),
            "show_spaces": bool(self.editor.show_spaces),
            "show_tabs": bool(self.editor.show_tabs),
            "show_line_endings": bool(self.editor.show_line_endings),
            "show_control_chars": bool(self.editor.show_control_chars),
        });
        data["editor"] = editor;
        data["keybindings"] = self.keys.overrides();
        data["ide"] = dict(self.ide_config);
        try:
            target = save_ide_config(data, self.sumide_config_path);
            self.sumide_config = load_ide_config(target);
            self.config = self.sumide_config;
            self._update_status("Configuration saved: {}".format(target));
            return True;
        except OSError as exc:
            self._update_status("Config error: {}".format(exc));
            return False;

    def _start_process(self):
        path = self._temporary_source();
        cwd = str(self.document.path.parent if self.document.path is not None else Path.cwd());
        self._temp_path = path;
        self._temp_output_path = None;
        if self.language in ("c", "cpp"):
            output_path = Path(str(path) + self._executable_suffix());
            self._temp_output_path = output_path;
            prefix = "c" if self.language == "c" else "cpp";
            compile_command = self._expanded_build(self._build_value(prefix + "_compile"), path, output_path);
            run_command = self._expanded_build(self._build_value(prefix + "_run"), path, output_path);
            command = self._shell_command(compile_command + " && " + run_command);
        else:
            command = self._runner_command(path);
        self._process_done = False;
        self._process_returncode = None;
        self._process_mode = "run";
        self._process_artifact_path = None;
        self._process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        );
        def reader():
            try:
                for line in self._process.stdout:
                    self._process_queue.put(line);
            finally:
                self._process_returncode = self._process.wait();
                self._process_done = True;
        self._process_thread = threading.Thread(target=reader, name="sumIDE-run", daemon=True);
        self._process_thread.start();
        return True;

    def _start_compile_process(self):
        if self.language not in ("c", "cpp"):
            raise RuntimeError("Compile is available for C/C++ buffers");
        path = self._temporary_source();
        output_path = self.compiled_output_path();
        cwd = str(self.document.path.parent if self.document.path is not None else Path.cwd());
        self._temp_path = path;
        self._temp_output_path = None;
        self._process_artifact_path = output_path;
        prefix = "c" if self.language == "c" else "cpp";
        compile_command = self._expanded_build(self._build_value(prefix + "_compile"), path, output_path);
        command = self._shell_command(compile_command);
        self._process_done = False;
        self._process_returncode = None;
        self._process_mode = "compile";
        self._process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        );
        def reader():
            try:
                for line in self._process.stdout:
                    self._process_queue.put(line);
            finally:
                self._process_returncode = self._process.wait();
                self._process_done = True;
        self._process_thread = threading.Thread(target=reader, name="sumIDE-compile", daemon=True);
        self._process_thread.start();
        return True;

    def compile_program(self):
        if self.language not in ("c", "cpp"):
            self._update_status("Compile is only available for C/C++ buffers.");
            return False;
        if self._process is not None and self._process.poll() is None:
            self._update_status("A process is already running. F5 stops it.");
            return True;
        target = self.compiled_output_path();
        self.output_view.set_text("--- Compile {} -> {} ---\n".format(self.document.path.name if self.document.path is not None else "Untitled", target.name));
        self.workspace.show(self.output_window);
        try:
            self._start_compile_process();
            self._update_status("Compiling {} -> {}".format(self._language_label(), target));
        except Exception as exc:
            self._append_output("Error: {}\n".format(exc));
            self._cleanup_process();
            self._update_status("Compile failed");
        self.app.invalidate();
        return True;

    def run_program(self):
        if self._process is not None and self._process.poll() is None:
            self._update_status("Program already running. F5 stops it.");
            return True;
        self.output_view.set_text("--- Run {} ({}) ---\n".format(self.document.path.name if self.document.path is not None else "Untitled", self.language));
        self.workspace.show(self.output_window);
        try:
            self._start_process();
            self._update_status("Running {}. F5 stops; F6 switches windows.".format(self.language));
        except Exception as exc:
            self._append_output("Error: {}\n".format(exc));
            self._cleanup_process();
            self._update_status("Run failed");
        self.app.invalidate();
        return True;

    def stop_program(self):
        process = self._process;
        if process is None or process.poll() is not None:
            self._update_status("No program is running.");
            return True;
        try:
            process.terminate();
        except Exception:
            pass;
        self._update_status("Stopping program...");
        return True;

    def toggle_run(self):
        process = self._process;
        return self.stop_program() if process is not None and process.poll() is None else self.run_program();

    def _cleanup_process(self):
        path = self._temp_path;
        self._temp_path = None;
        process = self._process;
        if process is not None:
            try:
                if process.stdout is not None:
                    process.stdout.close();
            except Exception:
                pass;
        self._process = None;
        self._process_thread = None;
        self._process_done = False;
        self._process_mode = None;
        self._process_artifact_path = None;
        if path is not None:
            try: path.unlink();
            except OSError: pass;
        output_path = self._temp_output_path;
        self._temp_output_path = None;
        if output_path is not None:
            try: output_path.unlink();
            except OSError: pass;
        return True;

    def _python_direct(self, source):
        stream = io.StringIO();
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            more = self._python_console.push(source);
        return stream.getvalue(), more;

    def _run_shell_direct(self, command):
        completed = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", check=False);
        output = str(completed.stdout or "");
        if completed.returncode != 0:
            output += "[shell exit {}]\n".format(completed.returncode);
        return output;

    def _language_direct(self, source):
        commands = {
            "basic": [sys.executable, "-m", "sumbasic", "-c", str(source)],
            "xbase": [sys.executable, "-m", "sumx", "-c", str(source)],
            "ruby": [shutil.which("ruby") or "ruby", "-e", str(source)],
            "php": [shutil.which("php") or "php", "-r", str(source)],
            "javascript": [shutil.which("node") or "node", "-e", str(source)],
        };
        command = commands.get(self.language);
        if command is None:
            return self._run_shell_direct(source);
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", check=False);
        output = str(completed.stdout or "");
        if completed.returncode != 0:
            output += "[{} exit {}]\n".format(self.language, completed.returncode);
        return output;

    def _direct_worker(self, source):
        try:
            if source.lstrip().startswith("!"):
                output = self._run_shell_direct(source.lstrip()[1:]);
                more = False;
            elif self.language == "python":
                output, more = self._python_direct(source);
            elif self.language == "r":
                output = self._r_session.execute(source);
                more = False;
            else:
                output = self._language_direct(source);
                more = False;
            self._direct_output = output;
            if self.language == "python":
                self.command_view.set_prompt("... " if more else ">>> ");
        except Exception as exc:
            self._direct_error = exc;
        finally:
            self._direct_done = True;
        return None;

    def _submit_direct(self, line, window):
        source = str(line or "");
        if self._process is not None and self._process.poll() is None:
            window.write_error("A program is running; stop it before using direct mode.");
            return None;
        if self._direct_thread is not None and self._direct_thread.is_alive():
            window.write_error("A direct command is already running.");
            return None;
        self._direct_output = "";
        self._direct_error = None;
        self._direct_done = False;
        if not self.app.running:
            self._direct_worker(source);
            self._finish_direct();
            return None;
        self._direct_thread = threading.Thread(target=self._direct_worker, args=(source,), name="sumIDE-direct", daemon=True);
        self._direct_thread.start();
        self._update_status("Direct {} command running...".format(self.language));
        return None;

    def _finish_direct(self):
        # xBase direct commands use COMMAND as command entry/history only;
        # their observable stdout/stderr belongs in OUTPUT.  Other profiles
        # keep their established interactive-console behavior (notably the
        # Python REPL, whose expression results intentionally remain in
        # COMMAND).
        if self.language == "xbase":
            if self._direct_output:
                self._append_output(self._direct_output);
                self.workspace.show(self.output_window);
            if self._direct_error is not None:
                self._append_output("Error: {}\n".format(self._direct_error));
                self.workspace.show(self.output_window);
                self._update_status("Direct command error");
            else:
                self._update_status("Direct command complete");
        else:
            if self._direct_output:
                for line in self._direct_output.rstrip("\n").splitlines():
                    self.command_view.write(line, style="command");
            if self._direct_error is not None:
                self.command_view.write_error("Error: {}".format(self._direct_error));
                self._update_status("Direct command error");
            else:
                self._update_status("Direct command complete");
        self._direct_thread = None;
        self._direct_done = False;
        self.app.invalidate();
        return True;

    def _poll_execution(self):
        dirty = False;
        while True:
            try:
                piece = self._process_queue.get_nowait();
            except queue.Empty:
                break;
            self._append_output(piece);
            dirty = True;
        if self._process_done:
            code_value = self._process_returncode;
            mode = self._process_mode or "run";
            artifact = self._process_artifact_path;
            self._append_output("--- exit {} ---\n".format(code_value));
            if mode == "compile":
                if code_value == 0 and artifact is not None:
                    if os.name != "nt":
                        try: artifact.chmod(artifact.stat().st_mode | 0o111);
                        except OSError: pass;
                    self._append_output("--- executable: {} ---\n".format(artifact));
                    self._update_status("Compile complete: {}".format(artifact.name));
                else:
                    self._update_status("Compile failed (exit {})".format(code_value));
            else:
                self._update_status("Run complete" if code_value == 0 else "Run failed (exit {})".format(code_value));
            self._cleanup_process();
            dirty = True;
        if self._direct_done:
            self._finish_direct();
            dirty = True;
        return dirty;

    def _quit_now(self):
        self.stop_program();
        self._r_session.close();
        return super()._quit_now();


def _ide_class_for(language):
    """Return an optional language backend while keeping sumIDE dependency-light.""";
    language = canonical_language(language);
    if language == "basic":
        try:
            from sumbasic.ide import SumBasicIDE;
            return SumBasicIDE;
        except ImportError:
            return ScriptIDE;
    if language == "xbase":
        try:
            from sumx.editor_app import SumXEditorApp;
            return SumXEditorApp;
        except ImportError:
            return ScriptIDE;
    return ScriptIDE;


def _main(argv=None, forced_language=None, prog="sumide"):
    raw_argv = list(sys.argv[1:] if argv is None else argv);
    program_args = [];
    if "--" in raw_argv:
        separator = raw_argv.index("--");
        program_args = raw_argv[separator + 1:];
        raw_argv = raw_argv[:separator];
    parser = argparse.ArgumentParser(prog=prog, description="Multi-language IDE built with sumTUI");
    parser.add_argument("files", nargs="*", help="source files; different languages may be opened together in sumide");
    parser.add_argument("--language", default=canonical_language(forced_language or "auto"), help="language profile (auto, basic, xbase, python, r, bash, c, cxx/cpp, html, javascript, php, ruby)");
    parser.add_argument("--theme", default=None, help="Sum theme");
    parser.add_argument("--run", action="store_true", help="run the opened source after the IDE starts");
    add_backend_arguments(parser);
    parser.add_argument("--list-languages", action="store_true", help="list installed language profiles and exit");
    parser.add_argument("--list-ui-backends", action="store_true", help="list available Sum UI backends and exit");
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(__version__));
    args = parser.parse_args(raw_argv);
    language = canonical_language(forced_language or args.language);
    ui_backend = backend_from_args(args);
    if args.list_languages:
        for key in language_choices():
            profile = get_profile(key);
            print("{}\t{}".format(profile.id, profile.label));
        return 0;
    if args.list_ui_backends:
        for name in available_backend_names():
            caps = backend_capabilities(name);
            print("{}\t{}\tcharts={} graphics={}".format(caps.name, caps.family, int(caps.charts), int(caps.graphics)));
        return 0;
    if ui_backend == "tui" and (not sys.stdin.isatty() or not sys.stdout.isatty()):
        print("{} TUI mode requires an interactive terminal; use --gui for the graphical backend".format(prog), file=sys.stderr);
        return 2;
    try:
        files = list(args.files or []);
        if args.run and len(files) != 1:
            parser.error("--run requires exactly one source file");
        if program_args and not args.run:
            parser.error("arguments after -- require --run");
        first = files[0] if files else None;
        resolved_language = language;
        if resolved_language == "auto" and first is not None:
            resolved_language = canonical_language(language_from_path(first));
        # A single BASIC/xBase document gets its language runtime backend.
        # Mixed-language workspaces remain the generic ScriptIDE shell.
        backend_language = resolved_language if (len(files) <= 1 or forced_language is not None) else "auto";
        ide_class = _ide_class_for(backend_language);
        if ide_class is ScriptIDE:
            ide = ide_class(first, language=resolved_language, theme=args.theme);
        else:
            ide = ide_class(first, theme=args.theme);
        for source in files[1:]:
            ide.open_path(source, activate=False);
        if program_args:
            setter = getattr(ide, "set_program_args", None);
            if callable(setter):
                setter(program_args);
            else:
                ide.program_args = list(program_args);
        if args.run:
            fired = {"value": False};
            def autorun():
                if fired["value"]:
                    return False;
                fired["value"] = True;
                ide.app.remove_idle(autorun);
                ide.run_program();
                return True;
            ide.app.add_idle(autorun);
        return ide.run(backend=ui_backend);
    except Exception as exc:
        print("{}: {}".format(prog, exc), file=sys.stderr);
        return 1;


def main(argv=None):
    return _main(argv=argv, forced_language=None, prog="sumide");


def main_python(argv=None):
    return _main(argv=argv, forced_language="python", prog="sumpy");


def main_r(argv=None):
    return _main(argv=argv, forced_language="r", prog="sumr");


def main_bash(argv=None):
    return _main(argv=argv, forced_language="bash", prog="sumbash");


def main_c(argv=None):
    return _main(argv=argv, forced_language="c", prog="sumc");


def main_cpp(argv=None):
    return _main(argv=argv, forced_language="cpp", prog="sumcxx");


def main_basic(argv=None):
    return _main(argv=argv, forced_language="basic", prog="sumbasic");


def main_xbase(argv=None):
    return _main(argv=argv, forced_language="xbase", prog="sumx");


def main_php(argv=None):
    return _main(argv=argv, forced_language="php", prog="sumphp");


def main_ruby(argv=None):
    return _main(argv=argv, forced_language="ruby", prog="sumruby");


def main_javascript(argv=None):
    return _main(argv=argv, forced_language="javascript", prog="sumjs");


if __name__ == "__main__":
    raise SystemExit(main());
