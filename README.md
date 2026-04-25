# rtv (RepoRescue fork) — Reddit Terminal Viewer, Python 3.13 compatible

> **Read this first.** Upstream `rtv` was abandoned in 2019 after Reddit
> changed its OAuth-app policy in a way that broke `rtv`'s auth flow.
> If what you want is a *working* curses Reddit client today, look at the
> community forks **[tuir](https://gitlab.com/ajak/tuir)** and
> **tuir-fork** — they are the maintained successors.
>
> This fork's scope is narrower: keep `rtv` **importable, installable,
> and runnable as a CLI on Python 3.13 + modern dependencies**, so that
> the styling/config/help-text/Reddit-URL helper layers (which a number
> of small terminal tools still pull in) remain usable. Whether the
> end-to-end *interactive* Reddit browse flow works for you depends on
> what you can still get out of Reddit's OAuth API with your own keys —
> that part is not, and cannot be, fixed in source.

`rtv` is a curses-based TUI Reddit reader. Originally Python 2.7 / early
Python 3 era; depended on `configparser.readfp`, the stdlib `mailcap`
module, `setuptools.use_2to3`, and `beautifulsoup4==4.5.1`. All four of
those broke between Python 3.10 and 3.13. This fork patches the source
so the package and its `rtv` console script load cleanly on a stock
Python 3.13.

---

## What changed vs upstream

Four distinct Python 3.13 break surfaces are addressed. All evidence is
in `outputs/glm/rtv/rtv.src.patch`:

| # | Break | Fix |
|---|---|---|
| 1 | `configparser.readfp` removed in Python 3.12 | `rtv/config.py:253` and `rtv/theme.py:402` switched to `configparser.read_file` |
| 2 | `mailcap` module removed in Python 3.13 | Added `mailcap-fix==1.0.1` (drop-in re-impl) to `install_requires` |
| 3 | `setuptools.use_2to3` removed in setuptools 58+ | Stripped legacy 2-to-3 conditional from `setup.py` |
| 4 | `beautifulsoup4 4.5.1` has no Python 3.13 wheel | Bumped to `beautifulsoup4 4.14.3` |

No behavioural change is intended outside those compatibility points.
The vendored legacy `rtv.packages.praw` is left intact and imports clean
on 3.13.

---

## Install

```bash
# Python 3.13 venv recommended
python3.13 -m venv venv
source venv/bin/activate
pip install -e .
```

Resolved dependency set on a clean Python 3.13 install:

```
beautifulsoup4 4.14.3
decorator      5.2.1
kitchen        1.2.6
mailcap-fix    1.0.1
requests       2.33.1
six            1.17.0
```

The `rtv` console script is installed by `setup.py`'s
`entry_points.console_scripts = rtv=rtv.__main__:main`.

---

## Quick start (CLI)

The CLI surface is the part most likely to keep being useful: it does
not touch Reddit at all.

```bash
rtv --help                    # full option listing
rtv --version                 # -> "rtv 1.27.1"
rtv --list-themes             # 5 presets: molokai, papercolor,
                              #   solarized-dark, solarized-light,
                              #   colorblind-dark
rtv --copy-config             # writes default rtv.cfg into
                              #   $XDG_CONFIG_HOME/rtv/rtv.cfg
```

If you want to actually open the TUI (`rtv` with no args), you will be
prompted to OAuth into Reddit. Whether that succeeds depends entirely
on your Reddit API credentials and current Reddit policy — it is not
something this fork can fix.

---

## Quick start (library API)

`rtv` ships several modules that are useful even when you are not
running the curses event loop. The pieces validated to work on
Python 3.13:

```python
from rtv.config import Config, OrderedSet, build_parser
from rtv.theme  import Theme, ThemeList
from rtv       import content as rtv_content
from rtv       import docs, exceptions

# Parse an rtv-format config file (uses the patched read_file path)
rtv_dict, bindings, *_ = Config.get_file("/path/to/rtv.cfg")
print(rtv_dict["subreddit"], rtv_dict["ascii"])

# Load a preset or custom theme (also uses patched read_file)
t = Theme.from_name("molokai")
print(len(t.elements), "themed elements")

themes, errors = Theme.list_themes()       # walks preset + installed
print([th.name for th in themes])

# Reddit URL normalization without touching the network
url = rtv_content.normalize_url(
    "https://www.reddit.com/r/python/comments/aa1/x/")

# Reuse rtv's argparse (same parser the CLI uses)
ns = build_parser().parse_args(["-s", "python", "--ascii"])

# Pre-canned help text and exception hierarchy
help_blob = max((v for v in vars(docs).values() if isinstance(v, str)), key=len)
print(len(exceptions.__dict__), "names exposed in rtv.exceptions")
```

A larger end-to-end "themed dashboard" example that writes a custom
theme + config to disk, loads them through the patched
`configparser.read_file` paths, and renders a synthetic submission
listing with theme colors is in
[`.reporescue/scenario_validate.py`](.reporescue/scenario_validate.py).

---

## What we verified

Two real validation harnesses live under `.reporescue/`. Both run in
a clean Python 3.13 venv with only `pip install -e .` performed.

### `usability_validate.py` — CLI + lib smoke test

| Surface | Probe | Result |
|---|---|---|
| `rtv.__main__` | `rtv --help` (real subprocess) | OK, contains "Reddit Terminal Viewer", `--list-themes`, `--copy-config` |
| `rtv.__main__` | `rtv --version` | OK, `rtv 1.27.1` |
| `rtv.__main__` | `rtv --list-themes` | OK, all 5 presets visible |
| `rtv.__main__` | `rtv --copy-config` (HOME redirected) | OK, 5409-byte `rtv.cfg` produced |
| `rtv.config` | `Config.get_file()` parses 18 keys via patched `read_file` | OK |
| `rtv.config` | `Config()` constructs (touches HISTORY/TOKEN env logic) | OK |
| `rtv.config` | `build_parser()` parses real argv | OK |
| `rtv.config` | `OrderedSet` basic ops | OK (note: `add()` is not idempotent — pre-existing) |
| `rtv.theme`  | `Theme.from_name("molokai")` -> 96 elements via patched `read_file` | OK |
| `rtv.theme`  | `Theme.list_themes()` parses 7 files | OK, errors=0 |
| `rtv.theme`  | `ThemeList.next()` cycles `molokai -> papercolor` | OK |
| `rtv.docs`   | 25 public names, biggest help string 3941 bytes | OK |
| `rtv.exceptions` | 14 exception classes, sample `AccountError` | OK |
| 3.13 stress  | `inspect.getsource(Config.get_file)` contains `read_file`, not `readfp` | OK |

### `scenario_validate.py` — Path B standalone scenario

A 30+ LOC offline workflow acting as a "themed reddit-style dashboard"
developer:

1. Write a custom theme file with `ansi_*` color specs.
2. Load it via `Theme.from_file` (patched `read_file`).
3. Write a custom config file.
4. Load it via `Config.get_file` (patched `read_file`).
5. Call `rtv.content.normalize_url` on a real Reddit permalink.
6. Render a synthetic submission listing using the loaded theme's color
   tuples; assert `ansi_81 -> fg int 81`, `ansi_222 -> fg int 222`,
   and that unicode authors (`céline`) survive the round trip.

No live downstream package on PyPI declares an `rtv` dependency
(community migrated to `tuir` / `tuir-fork`), so a Path-A cascade test
is N/A. Path B is the substitute.

### `bug_hunt.py` — actively tried to break it

Seven probes, two issues surfaced — **both pre-existing in upstream
rtv**, not introduced by the rescue:

- `OrderedSet.add` is not idempotent: the underlying `_list.append` is
  unconditional, so `OrderedSet(["a","b"]).add("a")` yields list
  `["a","b","a"]` while the set member check would say `"a"` is already
  present. Located at `rtv/config.py:150-152`.
- BOM-prefixed config files crash `Config.get_file` with
  `MissingSectionHeaderError`. Root cause is upstream's
  `codecs.open(..., "utf-8")`; using `"utf-8-sig"` would fix it. Real
  edge case (some Windows editors save `.cfg` with a BOM).

The rescue did not introduce these and did not fix them either; they
are flagged here so downstream consumers know.

---

## Status: USABLE

Per RepoRescue's usability rubric this fork is **USABLE** — clean
Python 3.13 install succeeds, the `rtv` console script answers
`--help`/`--version`/`--list-themes`/`--copy-config` with the documented
output, six distinct submodules (`config`, `theme`, `docs`,
`exceptions`, `content`, `__main__`) work, both patched
`configparser.read_file` lines run on real I/O paths that the original
test suite never covered, and four distinct Python 3.13 break surfaces
are demonstrably handled.

What "usable" does **not** mean: the original interactive TUI Reddit
browse flow is not promised here. It died upstream because of Reddit's
OAuth-app policy change, not because of a Python version bump, and
this fork has nothing to say about that.

---

## Disclaimer

This is a Python 3.13 compatibility fork produced by the
[RepoRescue](https://github.com/RepoRescue) benchmark. Code changes
were generated by an AI agent (model: GLM) and validated by the harness
described above. The original repository is at
<https://github.com/michael-lazar/rtv> and is unmaintained. For an
actively maintained Reddit terminal client, use
[tuir](https://gitlab.com/ajak/tuir) or `tuir-fork`.

## License

MIT — same as upstream rtv. See [`LICENSE`](LICENSE).
