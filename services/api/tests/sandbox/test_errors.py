from pathlib import Path

from poc_studio.sandbox.errors import parse_build_error

MODULE_NOT_FOUND = """
> logistics-starter@0.1.0 build
> next build

\x1b[1m\x1b[38;2;173;127;168m\u25b2 Next.js 16.4.6\x1b[39m\x1b[22m (Turbopack)

  Creating an optimized production build ...

> Build error occurred
Error: Turbopack build failed with 1 errors:
./app/broken/page.tsx:1:1
Module not found: Can't resolve '../../components/missing'
> 1 | import Missing from "../../components/missing";
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  2 |
  3 | export default function Page() {

Import map: aliased to relative '../../components/missing' inside of [project]/

https://nextjs.org/docs/messages/module-not-found
"""

TYPE_NOT_ASSIGNABLE = """
> next build

  Creating an optimized production build ...
 \u2713 Compiled successfully in 3.1s
  Running TypeScript ...
Failed to compile.

./app/shipments/page.tsx:12:9
Type error: Type 'string' is not assignable to type 'number'.

  10 | export default function Page() {
  11 |   return (
> 12 |     const total: number = "12";
     |           ^
  13 |   );
Next.js build worker exited with code: 1 and signal: null
"""

CANNOT_FIND_NAME = """
Failed to compile.

./components/ScreenNav.tsx:7:22
Type error: Cannot find name 'usePathnam'. Did you mean 'usePathname'?

   5 | export default function ScreenNav() {
   6 |   const path = usePathname();
>  7 |   const other = usePathnam();
     |                 ^
"""

JSX_SYNTAX = """
> Build error occurred
Error: Turbopack build failed with 1 errors:
./app/fleet/page.tsx:5:34
Parsing ecmascript source code failed
  3 | export default function Page() {
  4 |   return (
> 5 |     <div className="pf"><span>Total</div></div>
    |                                  ^^^^^^
  6 |   );

Unexpected token. Did you mean `{'>'}` or `&gt;`?

Import trace:
  App Browser:
    ./app/fleet/page.tsx
"""


def test_module_not_found() -> None:
    err = parse_build_error(MODULE_NOT_FOUND)
    assert err is not None
    assert (err.file, err.line, err.col) == ("app/broken/page.tsx", 1, 1)
    assert err.message == "Module not found: Can't resolve '../../components/missing'"
    assert 'import Missing from "../../components/missing";' in err.excerpt


def test_type_not_assignable() -> None:
    err = parse_build_error(TYPE_NOT_ASSIGNABLE)
    assert err is not None
    assert (err.file, err.line, err.col) == ("app/shipments/page.tsx", 12, 9)
    assert err.message == "Type 'string' is not assignable to type 'number'."


def test_cannot_find_name() -> None:
    err = parse_build_error(CANNOT_FIND_NAME)
    assert err is not None
    assert (err.file, err.line, err.col) == ("components/ScreenNav.tsx", 7, 22)
    assert err.message == "Cannot find name 'usePathnam'. Did you mean 'usePathname'?"


def test_jsx_syntax_error_takes_the_message_after_the_frame() -> None:
    err = parse_build_error(JSX_SYNTAX)
    assert err is not None
    assert (err.file, err.line, err.col) == ("app/fleet/page.tsx", 5, 34)
    assert (
        err.message
        == "Parsing ecmascript source code failed Unexpected token. Did you mean `{'>'}` or `&gt;`?"
    )


def test_tsc_style_line() -> None:
    err = parse_build_error("app/page.tsx(5,7): error TS2322: Type 'a' is not assignable to type 'b'.\n")
    assert err is not None and (err.file, err.line, err.col) == ("app/page.tsx", 5, 7)
    assert err.message == "Type 'a' is not assignable to type 'b'."


def test_excerpt_from_disk_marks_the_error_line(tmp_path: Path) -> None:
    page = tmp_path / "app" / "p" / "page.tsx"
    page.parent.mkdir(parents=True)
    page.write_text("\n".join(f"line {i}" for i in range(1, 11)), encoding="utf-8")
    err = parse_build_error("./app/p/page.tsx:5:3\nType error: Boom.\n", tmp_path)
    assert err is not None
    assert err.excerpt.splitlines() == [
        "  3 | line 3",
        "  4 | line 4",
        "> 5 | line 5",
        "  6 | line 6",
        "  7 | line 7",
    ]


def test_clean_output_is_not_an_error() -> None:
    assert parse_build_error(" \u2713 Compiled successfully\nRoute (app)\n") is None


def test_excerpt_is_confined_to_the_app_dir(tmp_path: Path) -> None:
    from poc_studio.sandbox.errors import excerpt_from_file

    app = tmp_path / "app_dir"
    (app / "lib").mkdir(parents=True)
    (app / "lib" / "a.ts").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (tmp_path / "x.json").write_text('{"secret": 1}\n', encoding="utf-8")
    assert "> 2 | two" in excerpt_from_file(app, "lib/a.ts", 2)  # any subpath of app_dir is allowed
    bs = chr(92)
    assert excerpt_from_file(app, f"..{bs}..{bs}x.json", 1) == ""
    assert excerpt_from_file(app, "../x.json", 1) == ""
    assert excerpt_from_file(app, str(tmp_path / "x.json"), 1) == ""
