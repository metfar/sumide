# sumIDE 0.2.0

`sumIDE` is the common multi-language IDE for the Sum ecosystem. It is built on `sumTUI`, but it is a separate project: `sumTUI` owns reusable terminal UI/editor primitives and `sumIDE` owns IDE behavior, language profiles, templates, preferences, build/run integration and project-oriented features.

## Origin

`sumIDE` was extracted in September 2026 from the IDE/editor work that had accumulated in `sumTUI`, `sumX` and `sumBASIC`. This repository intentionally keeps that lineage in `CHANGELOG.md`; version `0.2.0` is the first coordinated post-extraction release; the package version is not a claim that the IDE work started from zero.

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

## Preferences

`Options -> Preferences...` opens a centralized, sectioned dialog inspired by the organizational model of editors such as Geany. The 0.2.0 release includes General, Editor/Features, Editor/Indentation, Editor/Modelines, Files, Templates, Keybindings, Terminal and Languages pages.

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

<p align=center><b>- oOo -<b></p>
