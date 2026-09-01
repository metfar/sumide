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
"""Geany-inspired centralized preferences dialog for sumIDE.""";
from copy import deepcopy;

from sumtui.widgets import Button, CheckBox, Dialog, HBox, Label, ListView, TextInput, VBox;

from .config import save_config;
from .profiles import all_profiles;


class PreferencesDialog:
    def __init__(self, host):
        self.host = host;
        self.data = deepcopy(getattr(host, "sumide_config", {}));
        self.entries = {};
        self.page_box = VBox(Label(""));
        sections = [
            ("General", "general"),
            ("Editor / Features", "editor_features"),
            ("Editor / Indentation", "editor_indent"),
            ("Editor / Modelines", "editor_modelines"),
            ("Files", "files"),
            ("Templates", "templates"),
            ("Keybindings", "keybindings"),
            ("Terminal", "terminal"),
            ("Languages", "languages"),
        ];
        self.sections = ListView(sections, title="Section", on_change=self._section_changed);
        self.sections.selected = 0;
        content = HBox(self.sections, self.page_box, sizes=[24, None]);
        buttons = HBox(
            Button("Apply", on_press=self.apply, height=3),
            Button("Cancel", on_press=self.close, height=3),
            Button("OK", on_press=self.ok, default=True, height=3),
            ratios=[1, 1, 1],
        );
        self.body = VBox(content, buttons, sizes=[None, 3]);
        self.dialog = Dialog(self.body, title="sumIDE Preferences", width=94, height=30, on_cancel=self.close, shadow=True);
        self._show_page("general");

    @staticmethod
    def _text_row(label, entry):
        return HBox(Label(label), entry, sizes=[28, None]);

    def _set_page(self, title, widgets):
        page = VBox(Label(title), *widgets, sizes=[1] + [1] * len(widgets));
        self.page_box.items[0].widget = page;
        page.set_theme(self.host.app.theme);
        self.host.app.invalidate();
        return page;

    def _entry(self, key, value):
        entry = TextInput(str(value));
        self.entries[key] = entry;
        return entry;

    def _check(self, key, label, value):
        box = CheckBox(label, checked=bool(value));
        self.entries[key] = box;
        return box;

    def _show_page(self, section):
        self.entries = {};
        editor = self.data.setdefault("editor", {});
        if section == "general":
            general = self.data.setdefault("general", {});
            self._set_page("General / Startup", [
                self._text_row("Default language", self._entry("general.default_language", general.get("default_language", "python"))),
                self._check("general.restore_session", "Restore files from last session", general.get("restore_session", True)),
                self._check("general.confirm_exit", "Confirm exit", general.get("confirm_exit", False)),
            ]);
        elif section == "editor_features":
            self._set_page("Editor / Features", [
                self._check("editor.syntax_highlighting", "Syntax highlighting", editor.get("syntax_highlighting", True)),
                self._check("editor.show_spaces", "Show spaces", editor.get("show_spaces", False)),
                self._check("editor.show_tabs", "Show TAB characters", editor.get("show_tabs", False)),
                self._check("editor.show_line_endings", "Show line endings", editor.get("show_line_endings", False)),
                self._check("editor.show_control_chars", "Show control characters", editor.get("show_control_chars", False)),
                self._text_row("Line wrapping (-1 auto, 0 off)", self._entry("editor.line_wrapping", editor.get("line_wrapping", -1))),
                self._text_row("Hard line breaking (0 off)", self._entry("editor.line_breaking", editor.get("line_breaking", 0))),
                Label("Alt+W deletes forward; Ctrl+Alt+W deletes backward. Window menu: Alt+I."),
            ]);
        elif section == "editor_indent":
            self._set_page("Editor / Indentation", [
                self._text_row("Tab width", self._entry("editor.tab_width", editor.get("tab_width", 4))),
                self._text_row("Indent / shift width", self._entry("editor.indent_width", editor.get("indent_width", 4))),
                self._text_row("Soft tab width", self._entry("editor.soft_tab_width", editor.get("soft_tab_width", 4))),
                self._check("editor.expand_tabs", "Insert spaces instead of literal TAB", editor.get("expand_tabs", True)),
                self._check("editor.shiftround", "Round block indentation to shift width", editor.get("shiftround", False)),
                Label("Defaults are 4 columns; HTML defaults to 2 spaces."),
            ]);
        elif section == "editor_modelines":
            self._set_page("Editor / Modelines", [
                self._check("editor.read_vim_modelines", "Read safe Vim modelines", editor.get("read_vim_modelines", True)),
                self._text_row("First/last lines to inspect", self._entry("editor.modeline_lines", editor.get("modeline_lines", 5))),
                Label("Whitelist: ts, sw, sts, et/noet, sr/nosr, syntax/ft, ff, fenc."),
            ]);
        elif section == "files":
            files = self.data.setdefault("files", {});
            self._set_page("Files", [
                self._text_row("Default encoding", self._entry("files.encoding", files.get("encoding", "utf-8"))),
                self._text_row("Default EOL", self._entry("files.eol", files.get("eol", "LF"))),
                self._check("files.ensure_final_newline", "Ensure newline at file end", files.get("ensure_final_newline", True)),
                self._check("files.consistent_line_endings", "Ensure consistent line endings", files.get("consistent_line_endings", True)),
                self._check("files.strip_trailing_whitespace", "Strip trailing spaces/tabs on save", files.get("strip_trailing_whitespace", False)),
                self._check("files.replace_tabs_on_save", "Replace TABs with spaces on save", files.get("replace_tabs_on_save", False)),
            ]);
        elif section == "templates":
            templates = self.data.setdefault("templates", {});
            self._set_page("Templates", [
                self._text_row("Developer", self._entry("templates.author", templates.get("author", ""))),
                self._text_row("Mail address", self._entry("templates.email", templates.get("email", ""))),
                self._text_row("Company", self._entry("templates.company", templates.get("company", ""))),
                self._text_row("Initial version", self._entry("templates.initial_version", templates.get("initial_version", "1.0"))),
                Label("User templates: ~/.config/sumide/templates/<language>/*.tpl"),
            ]);
        elif section == "keybindings":
            self._set_page("Keybindings", [
                Label("Keyboard shortcuts are centralized here conceptually and remain editable."),
                Button("Open shortcut editor...", on_press=lambda *_: self.host.shortcuts_dialog(), height=3),
            ]);
        elif section == "terminal":
            terminal = self.data.setdefault("terminal", {});
            self._set_page("Terminal", [
                self._text_row("Shell", self._entry("terminal.shell", terminal.get("shell", "/bin/bash"))),
                self._text_row("Scrollback lines", self._entry("terminal.scrollback", terminal.get("scrollback", 500))),
            ]);
        elif section == "languages":
            labels = ["{}: tab={} indent={} spaces={}".format(profile.label, profile.tab_width, profile.indent_width, "yes" if profile.expand_tabs else "no") for profile in all_profiles()];
            self._set_page("Languages", [Label("Language profiles provide defaults; project/modeline/session values may override them."), *[Label(line) for line in labels]]);
        return True;

    def _section_changed(self, value, _row=None):
        self._collect();
        return self._show_page(str(value));

    def _write_key(self, dotted, value):
        group, key = dotted.split(".", 1);
        bucket = self.data.setdefault(group, {});
        bucket[key] = value;
        return value;

    def _collect(self):
        integer_keys = {"editor.tab_width", "editor.indent_width", "editor.soft_tab_width", "editor.line_wrapping", "editor.line_breaking", "editor.modeline_lines", "terminal.scrollback"};
        for key, widget in self.entries.items():
            value = widget.value;
            if key in integer_keys:
                try: value = int(value);
                except (TypeError, ValueError): continue;
            self._write_key(key, value);
        return self.data;

    def apply(self, *_args):
        self._collect();
        target = save_config(self.data, getattr(self.host, "sumide_config_path", None));
        self.host.sumide_config = deepcopy(self.data);
        editor = self.data.get("editor", {});
        editors = [state.get("editor") for state in getattr(self.host, "_code_buffers", {}).values()] or [getattr(self.host, "editor", None)];
        for target_editor in [item for item in editors if item is not None]:
            try: target_editor.tab_size = max(1, int(editor.get("tab_width", target_editor.tab_size)));
            except (TypeError, ValueError): pass;
            try: target_editor.indent_size = max(1, int(editor.get("indent_width", target_editor.indent_size)));
            except (TypeError, ValueError): pass;
            try: target_editor.soft_tab_size = max(1, int(editor.get("soft_tab_width", target_editor.soft_tab_size)));
            except (TypeError, ValueError): pass;
            target_editor.expand_tabs = bool(editor.get("expand_tabs", target_editor.expand_tabs));
            target_editor.shift_round = bool(editor.get("shiftround", target_editor.shift_round));
            target_editor.line_wrapping = int(editor.get("line_wrapping", target_editor.line_wrapping));
            target_editor.line_breaking = max(0, int(editor.get("line_breaking", target_editor.line_breaking)));
            target_editor.syntax_highlighting = bool(editor.get("syntax_highlighting", target_editor.syntax_highlighting));
            target_editor.configure_visibility(
                spaces=bool(editor.get("show_spaces", target_editor.show_spaces)),
                tabs=bool(editor.get("show_tabs", target_editor.show_tabs)),
                line_endings=bool(editor.get("show_line_endings", target_editor.show_line_endings)),
                controls=bool(editor.get("show_control_chars", target_editor.show_control_chars)),
            );
        self.host._update_status("Preferences saved: {}".format(target));
        self.host.app.invalidate();
        return True;

    def close(self, *_args):
        self.host.app.pop_modal();
        self.host.app.focus.set(self.host.editor);
        self.host.app.invalidate();
        return True;

    def ok(self, *_args):
        self.apply();
        return self.close();

    def show(self):
        self.host.app.push_modal(self.dialog);
        self.host.app.focus.set(self.sections);
        self.host.app.invalidate();
        return True;


def open_preferences(host):
    return PreferencesDialog(host).show();
