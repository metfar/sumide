from pathlib import Path
import tempfile

from sumide.app import ScriptIDE


def test_direct_xbase_output_is_routed_to_output_pane_not_command_pane():
    with tempfile.TemporaryDirectory() as directory:
        ide = ScriptIDE(None, language="xbase", sumide_config_path=Path(directory) / "config.json")
        ide.output_view.set_text("")
        ide.command_view.clear()
        ide._direct_output = "Hello from xBase\n"
        ide._direct_error = None
        ide._direct_done = True
        ide._finish_direct()
        assert "Hello from xBase" in ide.output_view.text
        assert not any("Hello from xBase" in str(item) for item in ide.command_view.output)


def test_direct_xbase_errors_are_routed_to_output_pane():
    with tempfile.TemporaryDirectory() as directory:
        ide = ScriptIDE(None, language="xbase", sumide_config_path=Path(directory) / "config.json")
        ide.output_view.set_text("")
        ide.command_view.clear()
        ide._direct_output = ""
        ide._direct_error = RuntimeError("boom")
        ide._direct_done = True
        ide._finish_direct()
        assert "Error: boom" in ide.output_view.text
        assert not any("boom" in str(item) for item in ide.command_view.output)


def test_python_direct_repl_output_stays_in_command_pane():
    with tempfile.TemporaryDirectory() as directory:
        ide = ScriptIDE(None, language="python", sumide_config_path=Path(directory) / "config.json")
        ide.app.running = False
        ide._submit_direct("x = 41", ide.command_view)
        ide._submit_direct("x + 1", ide.command_view)
        assert any(line == "42" for line, _role in ide.command_view.output)
