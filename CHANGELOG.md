# Changelog

## 0.2.6 - 2026-09-01

- Fixed sumX syntax highlighting in the xBase language profile: sumIDE now selects the dedicated `sumx` lexer instead of the generic Pygments FoxPro lexer.
- `#` comments are therefore highlighted atomically as comments, so keywords such as `THEN` and `AND` inside a comment no longer receive keyword/operator colours.
- The generic `xBase / FoxPro` syntax mode remains available in `sumedit` for classic FoxPro source.

## 0.2.5 - 2026-09-01

- Updated the common IDE dependency to sumTUI 0.7.5 so bounded input fields in language backends share the corrected logical-end overwrite/auto-advance policy.
- No language-specific field editing is implemented in sumIDE; the behavior remains owned by the common toolkit and selected by each backend/runtime.

## 0.2.4 - 2026-09-01

- Changed the fresh-workspace layout to Code across the top with Output below-left and Command below-right; all three are visible from startup and remain ordinary movable/resizable WorkspaceWindow instances.
- F5/Run now always reveals and activates Output before execution. Interactive language backends may temporarily activate Command when a program requests keyboard input.
- Moved generic programming `hello.*` samples and language launcher examples from sumTUI into sumIDE, matching the post-split ownership boundary.
- Uses a new `sumide-v2` workspace-layout namespace so old saved geometry cannot silently hide the newly standardized Output/Command layout.
- Retains automatic Markdown mapping through the common sumTUI editor layer rather than implementing it as an IDE-only feature.

## 0.2.3 - 2026-09-01

- Language help now shows scrollbars on both the topic list and the Markdown help pane.
- F2 inside language help opens a topic map and jumps directly to the selected help topic.
- Help remains routed by the active buffer language.

## 0.2.2 - 2026-09-01

- F1 in sumIDE is context-sensitive: BASIC/xBase buffers open the help corpus owned by the active language; Ctrl+F1 keeps the generic editor help.
- Help is resolved from the active buffer language rather than from the launcher used to start the IDE, so switching between supported language buffers also switches help context.
- Added a common language-help explorer with topic navigation, search, and F6/Ctrl+C example copying.
- Added an extensible `help_module` field to language profiles; language packages own their reference corpus while sumIDE owns presentation.

## 0.2.1 - 2026-09-01

- Added File -> Close for the active source document/window, completing New/Open/Save/Save As/Close source lifecycle management.
- Opening a source from the initial empty persistent code window now reuses that window instead of leaving an unnecessary blank buffer behind.
- Fixed the common source Open dialog import path.
- Supports language launchers that intentionally start with Command focused while retaining normal source windows.

## 0.2.0 - 2026-09-01

### First coordinated post-extraction release

- Promoted `sumIDE` from the extraction alpha to the common IDE layer used by the current Sum ecosystem. `sumTUI` remains the UI/editor toolkit; runtimes remain owned by their language projects.
- Preserved the project's ancestry in this changelog: the package is new, but the IDE descends from the multi-language IDE work in `sumTUI` and the language-specific editors in `sumX` and `sumBASIC`.
- Added centralized Preferences pages for General, Editor/Features, Editor/Indentation, Editor/Modelines, Files, Templates, Keybindings, Terminal and Languages. Persistent JSON is an implementation detail rather than the user-facing configuration interface.
- Added common language profiles for Bash, BASIC, C, C++, HTML, JavaScript, PHP, Python, R, Ruby and xBase, including `cxx`/`c++` aliases for the C++ profile.
- Added `File -> New -> <language>` templates with packaged defaults and user overrides, plus metadata variables for filename, author, e-mail, company, version, date/time, language and cursor placement.
- The Python default template uses the Sum GPL header and semicolon style.
- Standardized editor defaults at four columns; HTML defaults to two spaces. Eight-column tabs remain available only when explicitly configured or requested by a modeline.
- Inherited the current sumTUI editor behavior: `Alt+W`, `Ctrl+Alt+W`, block `Tab`/`Shift+Tab`, tabs/spaces conversion, safe Vim modelines and `Alt+I` for Window.
- Requires `sumTUI >= 0.7.0`.

## 0.1.0a1 - 2026-09-01

### Extraction into an independent project

- Created `sumIDE` as the independent IDE layer of the Sum ecosystem. The code is extracted from the multi-language IDE that previously lived in `sumTUI`, plus the language-specific editor frontends that had grown in `sumX` and `sumBASIC`.
- `sumTUI` remains the reusable terminal UI and text-editor toolkit and keeps `sumedit`; IDE concerns now belong here.
- `sumBASIC` delegates normal source editing to `sumIDE --language=basic` while preserving `--run`, `--check`, command and plain-runtime modes.
- `sumX` delegates positional `.prg` source editing to the xBase profile while retaining its interpreter, database runtime, `--run`, `--compile`, `--check` and command modes.

### Common language-profile architecture

- Added profile IDs for Bash, BASIC, C, C++ (`cpp`, with `cxx`/`c++` aliases), HTML, JavaScript, PHP, Python, R, Ruby and xBase.
- Added extension-based language detection and explicit `--language` forcing. An explicitly selected launcher/profile wins over filename detection.
- Added generic external runners for Python, R, Bash, JavaScript, PHP and Ruby, and Sum-runtime runners for BASIC and xBase. C/C++ keep configurable compile/run command templates.
- Added dedicated launchers including `sumpy`, `sumr`, `sumbash`, `sumc`, `sumcxx`, `sumphp`, `sumruby` and `sumjs`; `sumBASIC`/`sumX` packages remain responsible for their historically established command names.

### Preferences and templates

- Added a centralized Geany-inspired `Options -> Preferences...` dialog with General, Editor/Features, Editor/Indentation, Editor/Modelines, Files, Templates, Keybindings, Terminal and Languages sections.
- Added one central persistent sumIDE configuration under `$XDG_CONFIG_HOME/sumide/config.json` or `~/.config/sumide/config.json`; direct JSON editing is no longer the intended user interface.
- Added independent visual tab width, indentation/shift width, soft-tab width, expand-tabs and shift-round settings.
- The normal source-code default is four columns; HTML defaults to two spaces. Eight columns is supported only when explicitly configured/modelined, not as a modern default.
- Added safe Vim modeline support inherited from sumTUI: `ts`, `sw`, `sts`, `et/noet`, `sr/nosr`, `syntax/ft`, `ff`, and `fenc`. No arbitrary Vim command or expression is executed.
- Added `File -> New -> <language>` template creation for Bash, BASIC, C, C++, HTML, JavaScript, PHP, Python, R, Ruby and xBase.
- Added packaged defaults plus user overrides under `~/.config/sumide/templates/<language>/`.
- Added template variables for file metadata, author/email/company, version, date/time, language and cursor placement. The default Python template carries the Sum GPL header/style.

### Editing behavior carried forward

- `Alt+W` deletes forward through the next word/whitespace boundary and `Ctrl+Alt+W` deletes backward without crossing the line unexpectedly.
- The Window-menu accelerator is `Alt+I`, freeing `Alt+W` permanently for editing.
- `Tab`/`Shift+Tab` indent and unindent all selected lines, with the active language/modeline indentation width.
- Whole-document tabs-to-spaces and spaces-to-tabs conversion remains available.

## Historical lineage before the package split

The following work predates `sumIDE 0.1.0a1`. It was originally released inside the listed projects and is preserved here so the new repository does not erase its ancestry.

### sumTUI 0.6.1 - 2026

- Added `Alt+W` / `Ctrl+Alt+W` word-whitespace deletion, block indentation, tabs/spaces conversion and the `Alt+I` Window accelerator. These editor primitives remain in sumTUI and are consumed by sumIDE.

### sumTUI 0.6.0 - 2026

- Added optional `sumdiff` integration, live-buffer comparison and N-document compare/parallel-document handoff from the multi-source IDE.

### sumTUI 0.5.29 - 2026

- Added persistent workspace-window geometry, restore/reset support and the `sumide` layout namespace.

### sumTUI 0.5.27 - 2026

- Added F2 Program Map / document outline behavior, including Markdown outline/preview/export features shared by the editor family.

### sumTUI 0.5.24 - 2026

- Expanded the generic IDE to multiple simultaneously open source buffers with mixed Python, R, Bash, C and C++ language profiles.
- Added per-active-buffer run/build behavior and persistent C/C++ compile output.

### sumTUI 0.5.22 - 2026

- Standardized editor/IDE shortcuts, Program Map, save/exit confirmation, Output/Command scrolling and added Bash/C/C++ to the earlier Python/R IDE.

### sumTUI 0.5.20 - 2026

- Introduced reusable overlapping workspace windows and the first common `sumide` application with Code, Output and Command windows, Python/R direct mode, F5 run/stop and F6/F11/Ctrl+F4 window operations.

### sumBASIC 0.1.0a6 onward - 2026

- Introduced the BASIC-aware source IDE on top of sumTUI, then added non-blocking F5 execution, streamed/ANSI-aware run output, cancellation and live `INKEY$` routing in subsequent alphas. The editor shell now migrates to sumIDE; BASIC runtime semantics remain in sumBASIC.

### sumX pre-0.1.16 - 2026

- Developed the xBase-oriented editor/interactive workspace on top of sumTUI alongside the interpreter/database runtime. At 0.1.16 the source-editor shell moves to sumIDE while xBase execution, compilation and database semantics remain in sumX.
