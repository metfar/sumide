# sumIDE 0.2.9

`sumIDE` is the common multi-language IDE for the Sum ecosystem. It is built on `sumTUI`, but it is a separate project: `sumTUI` owns reusable terminal UI/editor primitives and `sumIDE` owns IDE behavior, language profiles, templates, preferences, build/run integration and project-oriented features.

## Origin

`sumIDE` was extracted in September 2026 from the IDE/editor work that had accumulated in `sumTUI`, `sumX` and `sumBASIC`. This repository intentionally keeps that lineage in `CHANGELOG.md`; version `0.2.0` began the extracted line and the changelog keeps the earlier editor/IDE history; the package version is not a claim that the IDE work started from zero.

## Language profiles

Initial profiles are: Bash, BASIC, C, C++ (`cxx`, with `cpp`/`c++` aliases), HTML, JavaScript, PHP, Python, R, Ruby and xBase.

Examples:

```bash
sumide program.py
sumide --language=basic program.bas
sumide --language=cxx hello.cpp
sumphp index.php
sumruby tool.rb
```

`sumBASIC` and `sumX` keep their runtime/compile command-line modes, but their source-editor entry paths delegate to this common IDE. When those runtime packages are installed, `sumIDE --language=basic` and `sumIDE --language=xbase` load their language-specific in-process backends while keeping the common sumIDE shell. The historical commands `sumbasic program.bas` and `sumx program.prg` therefore act as compatibility launchers into the same IDE rather than maintaining separate editor implementations.


## Workspace layout

A fresh IDE session opens all three common work areas: **Code** across the top, with **Output** below on the left and **Command** below on the right. All three are normal `WorkspaceWindow` instances: they can be activated, moved, resized, maximized, hidden and reopened. Running the current buffer with **F5 / Run** always shows and activates Output, even when it had previously been closed.

The default layout uses the `sumide-v2` workspace namespace so older saved layouts from the pre-split IDE do not accidentally hide the new Output/Command arrangement.

## Programming examples

Language-level sample programs belong to sumIDE rather than sumTUI. The source distribution includes `examples/hello.*` files for the supported profiles plus launcher examples under `examples/launchers/`. sumTUI keeps only examples that demonstrate the toolkit itself (widgets, `sumedit`, `suminput`, `sumdialog`, themes, and related TUI facilities).

The `examples/charts/` directory demonstrates the language-neutral `sum.chart/1` contract from Python, R, Bash, C, C++, JavaScript, PHP, Ruby, sumBASIC and sumX, plus an HTML/document example. Executable producers write the same JSON schema, so their output can be sent unchanged to either backend:

```bash
python examples/charts/chart.py | sumchart --backend=tui
python examples/charts/chart.py | sumchart --backend=gui
```

The same two commands work with the output of the other language examples. This is the reference pattern for future sumC, sumCPP, sumASM, sumPY and sumR bindings: languages produce shared contracts; renderers remain backend-specific.

The `examples/python/sumgui/` tree also carries the graphical sumGUI demos as ordinary Python examples. The originals may remain with sumGUI as toolkit smoke/development demos, but the IDE-facing copies are classified under Python rather than inventing a “sumGUI language”.

## Context-sensitive language help

`F1` follows the active source buffer. BASIC buffers load the help corpus provided by `sumbasic`; xBase buffers load the help corpus provided by `sumx`. The language package owns its reference text while sumIDE owns the common explorer UI, so adding another native Sum language does not require duplicating the help window.

The explorer provides topic navigation, F3 search, and **F6 / Ctrl+C** to copy the current functional example. **Ctrl+F1** always opens the generic editor help. If the active language has no bundled reference provider, F1 falls back to editor help.

## Preferences

`Options -> Preferences...` opens a centralized, sectioned dialog inspired by the organizational model of editors such as Geany. The 0.2.1 release includes General, Editor/Features, Editor/Indentation, Editor/Modelines, Files, Templates, Keybindings, Terminal and Languages pages.

The persistent configuration lives under `~/.config/sumide/config.json` (or `$XDG_CONFIG_HOME/sumide/config.json`). JSON is an implementation detail; users should normally change settings through Preferences. Editor visibility (spaces, TABs, EOLs and control characters), indentation, modelines, file policy, templates and shortcuts are persisted from the same configuration surface.

Indentation defaults are four columns. HTML defaults to two spaces. Vim modelines may safely override indentation/syntax/file metadata using the documented whitelist.

## File -> New templates

`File -> New` offers language-specific templates instead of forcing every new source buffer to be empty. Packaged templates live under `sumide/templates`; user overrides live under `~/.config/sumide/templates/<language>/`.

Template variables include `${FILENAME}`, `${BASENAME}`, `${EXTENSION}`, `${AUTHOR}`, `${EMAIL}`, `${COMPANY}`, `${VERSION}`, `${YEAR}`, `${DATE}`, `${DATETIME}`, `${LANGUAGE}` and `${CURSOR}`.

The default Python template follows the Sum project GPL header and semicolon style.

## Editing behavior inherited from sumTUI

The editor engine provides `Alt+W` forward word/whitespace deletion, `Ctrl+Alt+W` backward deletion, block `Tab`/`Shift+Tab`, whole-document tabs/spaces conversion, configurable indentation widths, and safe Vim modelines. The Window menu mnemonic is `Alt+I` so `Alt+W` stays an editing command.

## License

GPL-2.0-or-later.


### Source lifecycle

The common File menu owns source-buffer lifecycle: New, Open, Save, Save As, and Close. Language launchers such as `sumx` may start with the Command window focused while keeping source programs available as normal sumIDE code windows.

### Language help browser

Language-owned help opens in the common sumIDE browser.  Both the topic list and the rendered Markdown pane have scrollbars. **F2** opens the Topic Map from either side of the help browser, **F3** searches, and **F6 / Ctrl+C** copies the current functional example. The help provider follows the active buffer language.

## TUI and GUI are the same IDE

The backend is selected at runtime:

```bash
sumide
sumide --gui
```

Both forms create the same IDE application, buffers, windows, menus, editor/highlighter, help system, preferences, keybindings and theme. The TUI remains terminal-first and supports both keyboard and mouse; the GUI backend provides graphical keyboard/mouse/touch presentation of the same state.


## Graphical image export

When sumIDE is running through `--gui`, **File -> Export graphical window as PNG...** exports the current graphical application window. This uses the common Sum application backend; it is not a separate GUI-only application implementation.

## r17 examples

The packaged example library now includes the r17 BASIC DISPLAY/page-buffering, cursor-position and BGI-style drawing examples together with Python `sumui.bgi`, `sumui.conio` and stdio/conio demonstrations. The compact-font SumGUI report dashboard remains synchronized with the toolkit source example.

<p align=center><b>- oOo -<b></p>
