import copy
import json
from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit, sector_dir
from poc_studio.screens.validate import validate

KIT = load_kit("logistics")
FIXTURES = json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))
VALID: dict[str, Any] = FIXTURES[1]
INVALID: dict[str, Any] = FIXTURES[0]


def codes(data: dict[str, Any]) -> set[str]:
    return {i.code for i in validate(ScreenPack.model_validate(data), KIT)}


def mutated(change: Callable[[dict[str, Any]], None]) -> set[str]:
    data = copy.deepcopy(VALID)
    change(data)
    return codes(data)


def test_valid_fixture_passes() -> None:
    pack = ScreenPack.model_validate(VALID)
    assert validate(pack, KIT) == []
    assert len(pack.screens) == 6 and sum(s.play for s in pack.screens) >= 3


def test_invalid_fixture_reports_its_planted_problems() -> None:
    assert codes(INVALID) == {"css_scope", "step_css_scope", "undefined_class", "route_format"}


def test_app_class_must_equal_the_kit() -> None:
    assert "app_class" in mutated(lambda d: d.update(app_class="other"))


def test_product_css_must_be_scoped() -> None:
    assert "css_scope" in mutated(
        lambda d: d.update(product_css=d["product_css"] + "\n.card { color: red; }")
    )
    assert "css_scope" in mutated(
        lambda d: d.update(product_css=d["product_css"] + "\n.pf .zzz .card { color: red; }")
    )
    assert "css_scope" in mutated(
        lambda d: d.update(product_css=d["product_css"] + "\n@font-face { font-family: x; }")
    )
    assert "css_scope" in mutated(
        lambda d: d.update(product_css=d["product_css"] + "\n@keyframes spin { from {top:0} }")
    )


def test_scoped_media_and_keyframes_are_fine() -> None:
    extra = (
        "\n@keyframes lgx-pulse { from { opacity: 0 } 50% { opacity: 1 } }\n"
        "@media (max-width: 500px) { .pf .lgx .card { padding: 0; } }\n"
    )
    assert mutated(lambda d: d.update(product_css=d["product_css"] + extra)) == set()


def test_step_css_must_start_with_the_screen_scope() -> None:
    def other_screen(d: dict[str, Any]) -> None:
        d["screens"][0]["step_css"] = '.pf.sl-regions[data-step="1"] .lgx .card { color: red; }'

    def unscoped(d: dict[str, Any]) -> None:
        d["screens"][0]["step_css"] = ".pf .lgx .card { color: red; }"

    def second_selector(d: dict[str, Any]) -> None:
        d["screens"][0]["step_css"] = '.pf.sl-overview[data-step="1"] .lgx .card, .lgx .stat { color: red; }'

    for change in (other_screen, unscoped, second_selector):
        assert "step_css_scope" in mutated(change)


def test_classes_must_be_defined() -> None:
    def add(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] = (
            d["screens"][0]["html"]
            .replace("kpis", "kpis", 1)
            .replace('class="stat"', 'class="stat ghost-class"', 1)
        )

    assert "undefined_class" in mutated(add)


def test_root_needs_the_app_class() -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] = d["screens"][0]["html"].replace(
            '<div class="lgx">', '<div class="shell">', 1
        )

    assert "root_class" in mutated(change)


@pytest.mark.parametrize(
    "snippet",
    [
        "<script>1</script>",
        '<iframe src="data:text/html,x"></iframe>',
        "<object></object>",
        "<embed>",
        '<meta name="x" content="y">',
        '<base href="/">',
        "<form></form>",
        '<link rel="stylesheet">',
        "<style>.a{}</style>",
        "<template><p>x</p></template>",
    ],
)
def test_forbidden_elements(snippet: str) -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] = d["screens"][0]["html"].replace("</main>", snippet + "</main>", 1)

    assert "forbidden_element" in mutated(change)


def test_event_handler_attributes_are_rejected() -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] = d["screens"][0]["html"].replace(
            'class="btn btn-primary"', 'class="btn btn-primary" onclick="x()"', 1
        )

    assert "forbidden_attribute" in mutated(change)


@pytest.mark.parametrize(
    "attr",
    ['href="https://evil.example.net/x"', 'href="//evil.example.net/x"', 'href="javascript:alert(1)"',
     'src="http://evil.example.net/a.png"', 'data-x="javascript:alert(1)"'],
)  # fmt: skip
def test_external_urls_are_rejected(attr: str) -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] = d["screens"][0]["html"].replace("</main>", f"<a {attr}>x</a></main>", 1)

    assert "external_url" in mutated(change)


def test_external_urls_in_css_are_rejected() -> None:
    def product(d: dict[str, Any]) -> None:
        d["product_css"] += '\n.pf .lgx .x { background: url("https://evil.example.net/a.png"); }'

    def step(d: dict[str, Any]) -> None:
        d["screens"][0]["step_css"] = '@import url("x.css");'

    assert "css_external" in mutated(product)
    assert "css_external" in mutated(step)


@pytest.mark.parametrize(
    "js",
    [
        "fetch('/x')",
        "new XMLHttpRequest()",
        "new WebSocket('x')",
        "document.cookie",
        "eval('1')",
        "location.href = 'x'",
    ],
)
def test_script_network_calls_are_rejected(js: str) -> None:
    assert "script_network" in mutated(lambda d: d["screens"][0].update(script=js))


def test_anchors_must_be_unique_per_screen() -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["anchors"].append(copy.deepcopy(d["screens"][0]["anchors"][0]))

    assert "duplicate_anchor" in mutated(change)


def test_anchor_matching_nothing_fails_the_schema() -> None:
    data = copy.deepcopy(VALID)
    data["screens"][0]["anchors"][0]["selector"] = '[data-anchor="does-not-exist"]'
    with pytest.raises(ValidationError, match="matches no element"):
        ScreenPack.model_validate(data)


@pytest.mark.parametrize("route", ["weekly", "/Weekly", "/a/b", "/a_b", "/-a", "//"])
def test_routes_must_be_kebab_case(route: str) -> None:
    assert "route_format" in mutated(lambda d: d["screens"][3].update(route=route))


def test_routes_must_be_unique() -> None:
    assert "route_duplicate" in mutated(lambda d: d["screens"][3].update(route="/regions"))


def test_exactly_one_home() -> None:
    assert "route_home" in mutated(lambda d: d["screens"][0].update(route="/home"))
    assert "route_home" in mutated(lambda d: d["screens"][1].update(route="/"))


def test_at_least_three_play_screens() -> None:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["play"] = False

    assert "play_count" in mutated(change)


def test_sector_mapping() -> None:
    assert sector_dir("e-commerce") == "ecommerce"
    assert sector_dir("other", "patients book clinic appointments") == "healthcare"
    assert sector_dir("other", "card payments and fraud checks") == "fintech"
    assert sector_dir("other", "nothing relevant here") == "logistics"
