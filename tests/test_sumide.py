#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
import tempfile;
from pathlib import Path;

from sumide.app import ScriptIDE;
from sumide.config import defaults, load_config, save_config;
from sumide.profiles import canonical_language, get_profile, language_from_path;
from sumide.templates import TemplateManager;
from sumtui.modeline import parse_vim_modeline, scan_vim_modelines;


def test_profiles_cover_requested_languages():
    for language in ("basic", "xbase", "python", "r", "bash", "c", "cpp", "php", "ruby", "html"):
        assert get_profile(language).id == language;
    assert canonical_language("cxx") == "cpp";
    assert canonical_language("c++") == "cpp";
    assert language_from_path("hello.cxx") == "cpp";
    assert get_profile("html").indent_width == 2;
    assert get_profile("python").indent_width == 4;


def test_safe_vim_modeline_subset():
    parsed = parse_vim_modeline("# vim: syntax=sh ts=4 sw=4 sts=4 sr noet");
    assert parsed["syntax"] == "bash";
    assert parsed["tabstop"] == 4;
    assert parsed["shiftwidth"] == 4;
    assert parsed["softtabstop"] == 4;
    assert parsed["shiftround"] is True;
    assert parsed["expandtab"] is False;
    assert "source" not in parsed;
    combined = scan_vim_modelines("# vim: ts=4 sw=4 et\nbody\n# vim: ft=python", 5);
    assert combined["tabstop"] == 4;
    assert combined["syntax"] == "python";


def test_python_template_uses_project_header_and_variables():
    manager = TemplateManager({"author": "William Martinez Bas", "email": "metfar@gmail.com"});
    text = manager.render("python", filename="demo.py");
    assert text.startswith("#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n#pylint:disable=W0301");
    assert "#  demo.py" in text;
    assert "William Martinez Bas <metfar@gmail.com>" in text;
    assert "sys.exit(main(sys.argv[1:]));" in text;


def test_config_is_one_central_document():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "config.json";
        data = defaults();
        data["editor"]["tab_width"] = 5;
        save_config(data, path);
        loaded = load_config(path);
        assert loaded["editor"]["tab_width"] == 5;
        assert loaded["languages"]["html"]["indent_width"] == 2;


def test_script_ide_detects_languages_and_new_template_menu():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory);
        config = root / "sumide.json";
        source = root / "hello.php";
        source.write_text("<?php\necho 'hi';\n", encoding="utf-8");
        ide = ScriptIDE(source, sumide_config_path=config);
        assert ide.language == "php";
        file_menu = next(menu for menu in ide._menus() if menu.title == "File");
        assert file_menu.items[0].label == "New";
        labels = [item.label for item in file_menu.items[0].submenu.items if getattr(item, "label", "")];
        assert "BASIC" in labels;
        assert "C++" in labels;
        assert "PHP" in labels;
        assert "Ruby" in labels;
        options = next(menu for menu in ide._menus() if menu.title == "Options");
        assert any(getattr(item, "label", "") == "Preferences..." for item in options.items);


def test_html_new_template_uses_two_space_profile():
    with tempfile.TemporaryDirectory() as directory:
        ide = ScriptIDE(None, language="html", sumide_config_path=Path(directory) / "config.json");
        assert ide.editor.tab_size == 2;
        assert ide.editor.indent_size == 2;
        assert ide.new_from_template("html");
        assert ide.editor.tab_size == 2;
        assert "<!doctype html>" in ide.editor.text;


def test_editor_visibility_is_persisted_with_central_preferences():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "config.json";
        ide = ScriptIDE(None, language="python", sumide_config_path=path);
        ide.editor.show_spaces = True;
        ide.editor.show_tabs = True;
        ide.editor.show_line_endings = True;
        ide.editor.show_control_chars = True;
        assert ide.save_config();
        restored = ScriptIDE(None, language="python", sumide_config_path=path);
        assert restored.editor.show_spaces is True;
        assert restored.editor.show_tabs is True;
        assert restored.editor.show_line_endings is True;
        assert restored.editor.show_control_chars is True;


def test_language_backends_attach_to_the_common_shell_when_installed():
    from sumide.app import _ide_class_for;
    from sumbasic.ide import SumBasicIDE;
    from sumx.editor_app import SumXEditorApp;
    assert _ide_class_for("basic") is SumBasicIDE;
    assert _ide_class_for("xbase") is SumXEditorApp;
    assert _ide_class_for("python") is ScriptIDE;


def test_every_language_profile_has_a_default_template():
    from sumide.profiles import language_choices;
    manager = TemplateManager({"author": "William Martinez Bas", "email": "metfar@gmail.com"});
    for language in language_choices():
        rendered = manager.render(language, filename="demo" + get_profile(language).extensions[0]);
        assert rendered.strip();
