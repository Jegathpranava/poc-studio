from poc_studio.qa.checks import Check
from poc_studio.qa.routing import decide


def ok(name: str, owner: str = "pitch") -> Check:
    return Check(name=name, ok=True, detail="ok", owner_agent=owner)


def bad(name: str, owner: str, report_only: bool = False) -> Check:
    return Check(name=name, ok=False, detail="x", owner_agent=owner, report_only=report_only)


def test_all_passing_sends_nothing_back() -> None:
    assert decide([ok("a"), ok("b")], 0) == {"send_back": None, "block_publish": False}


def test_spotlight_failure_goes_to_pitch() -> None:
    checks = [ok("deck_present", "assemble"), bad("spotlights_resolve", "pitch")]
    assert decide(checks, 0)["send_back"] == "pitch"


def test_feature_missing_from_screens_goes_to_screens() -> None:
    assert decide([bad("features_consistent", "screens")], 1)["send_back"] == "screens"


def test_secret_goes_to_port_and_blocks_publish() -> None:
    assert decide([ok("x"), bad("no_secrets", "port")], 0) == {"send_back": "port", "block_publish": True}


def test_build_failure_is_report_only() -> None:
    result = decide([bad("build_passed", "port", report_only=True)], 0)
    assert result == {"send_back": None, "block_publish": False}


def test_self_contained_failure_is_report_only() -> None:
    assert decide([bad("deck_self_contained", "assemble", report_only=True)], 0)["send_back"] is None


def test_assemble_and_video_owners_are_never_sent_back() -> None:
    assert decide([bad("deck_present", "assemble"), bad("mp4", "video")], 0)["send_back"] is None


def test_pii_and_missing_input_failures_are_report_only() -> None:
    assert decide([bad("no_pii", "pitch", report_only=True)], 0)["send_back"] is None


def test_first_sendable_failure_wins() -> None:
    checks = [bad("build_passed", "port", True), bad("spotlights_resolve", "pitch")]
    checks.append(bad("no_secrets", "port"))
    assert decide(checks, 0)["send_back"] == "pitch"


def test_after_two_send_backs_none_are_made_but_secrets_still_block() -> None:
    checks = [bad("spotlights_resolve", "pitch"), bad("no_secrets", "port")]
    assert decide(checks, 1)["send_back"] == "pitch"
    assert decide(checks, 2) == {"send_back": None, "block_publish": True}
