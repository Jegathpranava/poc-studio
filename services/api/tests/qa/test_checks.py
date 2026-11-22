from poc_studio.qa import checks as c
from poc_studio.qa.checks import QAInputs
from poc_studio.qa.secrets import Finding
from poc_studio.schemas.deck import Figure


def test_every_check_passes_on_the_good_inputs(good: QAInputs) -> None:
    results = c.run_checks(good)
    assert [r.name for r in results] == [f.__name__ for f in c.ALL_CHECKS]
    assert [r.name for r in results if not r.ok] == []


def test_deck_present(good: QAInputs) -> None:
    good.deck_html = None
    result = c.deck_present(good)
    assert not result.ok and result.owner_agent == "assemble" and result.report_only
    good.lenient = True
    assert c.deck_present(good).ok  # stub mode skips...
    good.deck_failed = True
    assert not c.deck_present(good).ok  # ...unless the deck step reported its own failure


def test_deck_self_contained(good: QAInputs) -> None:
    assert c.deck_self_contained(good).ok
    for bad in (
        '<img src="https://evil.test/a.png">',
        '<link href="//cdn.test/x.css" rel="stylesheet">',
        '<img srcset="https://cdn.test/a.png 2x">',
        '<video poster="http://x.test/p.png"></video>',
        "<style>.a{background:url(https://x.test/a.png)}</style>",
        "<style>@import 'x.css';</style>",
        '<style>.a{background:image-set("https://x.test/a.png" 1x)}</style>',
        '<div style="background:url(http://x.test/a.png)"></div>',
    ):
        good.deck_html = f"<html><body>{bad}</body></html>"
        result = c.deck_self_contained(good)
        assert not result.ok and result.owner_agent == "assemble" and result.report_only, bad


def test_spotlights_resolve(good: QAInputs) -> None:
    assert c.spotlights_resolve(good).ok
    assert good.plan is not None
    step = next(s for sl in good.plan.slides for s in sl.steps)
    step.spotlight = ".nothing-here"
    result = c.spotlights_resolve(good)
    assert not result.ok and result.owner_agent == "pitch" and ".nothing-here" in result.detail


def test_features_consistent(good: QAInputs) -> None:
    assert c.features_consistent(good).ok
    assert good.req is not None
    good.req.features[0].name = "Quantum teleportation manifest"
    missing = c.features_consistent(good)
    assert not missing.ok and missing.owner_agent == "screens"


def test_feature_on_screens_but_not_in_deck_goes_to_pitch(good: QAInputs) -> None:
    assert good.plan is not None
    for s in good.plan.slides:
        s.title, s.caption = "Overview", "Nothing relevant"
        for st in s.steps:
            st.title, st.caption = "Look", "Here"
    good.plan.title = "Tour"
    result = c.features_consistent(good)
    assert not result.ok and result.owner_agent == "pitch"


def test_loose_match_is_60_percent_of_long_words() -> None:
    assert c.loose_match("Weekly sales dashboard", "a sales dashboard for the team")  # 2 of 3
    assert not c.loose_match("Weekly sales dashboard", "dashboard only")  # 1 of 3
    assert c.loose_match("AI", "an ai helper")  # no long words: plain substring


def test_names_consistent(good: QAInputs) -> None:
    assert c.names_consistent(good).ok
    assert good.req is not None
    good.req.client = "Globex"
    result = c.names_consistent(good)
    assert not result.ok and result.owner_agent == "pitch"


def test_costs_consistent(good: QAInputs) -> None:
    assert c.costs_consistent(good).ok
    assert good.plan is not None
    close = next(s for s in good.plan.slides if s.kind == "close")
    close.figures = [
        Figure(label="Monthly running cost", value=99, source="architecture: monthly_cost.total_usd")
    ]
    assert not c.costs_consistent(good).ok
    close.figures = []
    good.plan.exec_summary_md = "no figures here"
    result = c.costs_consistent(good)
    assert not result.ok and "executive summary" in result.detail


def test_figures_sourced(good: QAInputs) -> None:
    assert c.figures_sourced(good).ok
    assert good.plan is not None
    next(s for s in good.plan.slides if s.kind == "close").figures[0].verified = False
    result = c.figures_sourced(good)
    assert not result.ok and result.owner_agent == "pitch"


def test_build_passed(good: QAInputs) -> None:
    assert c.build_passed(good).ok
    good.build = {"ok": False, "error": {"message": "Module not found"}}
    result = c.build_passed(good)
    assert not result.ok and result.owner_agent == "port" and result.report_only
    assert "did not build" in result.detail


def test_no_secrets(good: QAInputs) -> None:
    assert c.no_secrets(good).ok
    good.secret_findings = [Finding(file="app/a.ts", line=3, kind="github_token")]
    result = c.no_secrets(good)
    assert not result.ok and result.owner_agent == "port" and not result.report_only
    assert "app/a.ts:3" in result.detail


def test_no_pii_is_a_warning_owned_by_the_file(good: QAInputs) -> None:
    assert c.no_pii(good).ok
    good.pii_findings = [Finding(file="app/app/page.tsx", line=1, kind="email")]
    result = c.no_pii(good)
    assert not result.ok and result.owner_agent == "screens" and result.report_only
    good.pii_findings = [Finding(file="deck/x.html", line=1, kind="phone")]
    assert c.no_pii(good).owner_agent == "pitch"


def test_missing_inputs_fail_in_a_real_run_and_skip_in_stub_mode() -> None:
    real = c.spotlights_resolve(QAInputs())
    assert not real.ok and real.report_only
    stub = c.spotlights_resolve(QAInputs(lenient=True))
    assert stub.ok and stub.detail == "skipped (stub)"
