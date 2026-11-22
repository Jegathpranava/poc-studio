# Graph Report - poc-studio  (2026-11-23)

## Corpus Check
- 407 files · ~176,463 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .css 34, (none) 11, .vtt 5)

## Summary
- 3971 nodes · 11254 edges · 198 communities (140 shown, 58 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 934 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbd0da80`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- toast.js
- i
- web/package.json
- test_pitch.py
- ref_react
- Tasks
- runs-view.tsx
- _t
- test_manager.py
- ChatReply
- deck-view.tsx
- steps
- brief-view.tsx
- procs.py
- complete_json
- _broken_json
- _to_end
- validate.py
- parse_build_error
- A
- new-run-form.tsx
- app.js
- ScreenPack
- _Converter
- PoC Studio — Developer Guidelines & Architecture Rules
- test_settings.py
- github/publish.py
- checks.py
- ecommerce/app/package.json
- PoC Studio — Developer Guidelines & Architecture Rules
- UI preview
- runtime.js
- constructor
- redact
- Architecture
- timeline-view.tsx
- run-context.tsx
- re
- parse.py
- test_run_eval.py
- package.json
- secrets.py
- fintech/app/package.json
- test_artifacts_files.py
- t
- test_validate.py
- screenpack.py
- test_port.py
- healthcare/app/package.json
- logistics/app/package.json
- compilerOptions
- compilerOptions
- compilerOptions
- owner-direction-2026-11-22.md
- NEXT_STEPS.md
- check-github-token.sh
- api.ts
- test_env.py
- poc-studio-api
- settings.py
- compilerOptions
- media/video.py
- compilerOptions
- 0005_repo_artifact.py
- ref_node_path
- run_eval.py
- _make_binary_fixtures.py
- build.py
- PoC Studio: design spec
- BuildResult
- build_share_zip
- A
- Technical Requirements Document: Returns and Substitution Assistant
- Technical Requirements Document: Last-Mile Route Re-Optimiser
- Business Requirements Document: Dock Scheduling Assistant
- sd
- intelligence.py
- Business Requirements Document: Patient Intake and Prior Authorisation Assistant
- Wv
- PreviewManager
- dependencies
- env
- test_screens.py
- share-api.ts
- test_retention.py
- test_json.py
- bT
- sample.md
- Sector templates
- web/README.md
- AGENTS.md
- seed_run
- client
- settings_store.py
- W
- deck.py
- gate2-view.tsx
- loose_match
- artifacts.py
- MockGitHub
- FakeProvider
- Decisions
- decide
- launch_next
- build.mjs
- RunEvent
- architecture-view.tsx
- RunService
- schemas.py
- export_share
- TestClient
- open_session
- test_full_run.py
- deck_runtime/README.md
- eo
- test_event_loop.py
- test_a_raise_resumes_with_no_duplicate_paid_call
- LiveGitHub
- app.js
- test_jsx.py
- llm/client.py
- test_qa_node.py
- Settings
- el
- test_drift.py
- test_client.py
- ChatReply
- web/app/layout.tsx
- parse_file
- pytest
- test_degrade.py
- dev.mjs
- mountScreen
- PreviewError
- page.py
- _ensure
- runs.py
- load_kit
- healthcare kit: selector and anchor guide
- post
- test_gate_events.py
- scripts
- tokens.py
- get_publish
- Eval
- get_github
- extra_routes.py
- event_name
- datetime
- _fake_pdf
- PoC Studio build plan
- FileTooLarge
- _patch_sandbox
- open_session
- guard.py
- RedactingFilter
- test_intelligence_is_unmasked_by_default
- db/models.py

## God Nodes (most connected - your core abstractions)
1. `open_session()` - 137 edges
2. `get_settings()` - 113 edges
3. `wait_status()` - 91 edges
4. `client()` - 88 edges
5. `ScreenPack` - 86 edges
6. `create_run()` - 82 edges
7. `DeckPlan` - 74 edges
8. `Artifact` - 69 edges
9. `Run` - 68 edges
10. `A()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `File map` --references--> `NodeSpec`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/graph/registry.py
- `7. Data model and interfaces` --references--> `DeckPlan`  [INFERRED]
  docs/specs/2026-11-22-poc-studio-design.md → services/api/poc_studio/schemas/deck.py
- `Measures` --references--> `no_secrets()`  [INFERRED]
  eval/README.md → services/api/poc_studio/qa/checks.py
- `Example screens` --references--> `steps()`  [INFERRED]
  templates/healthcare/kit/selectors.md → services/api/tests/fixtures/deck/build_fixture.py
- `Task 16: MP4 recorder and Deck and video page  [after: 8, 14, 15]` --references--> `video_check()`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/media/video.py

## Import Cycles
- None detected.

## Communities (198 total, 58 thin omitted)

### Community 0 - "toast.js"
Cohesion: 0.01
Nodes (137): _4(), add(), addValue(), addVariantChild(), Ag(), b4(), bindToMotionValue(), BM() (+129 more)

### Community 1 - "i"
Cohesion: 0.06
Nodes (88): Aa(), ap(), bD(), bT(), c1(), Cg(), cT(), Dd() (+80 more)

### Community 2 - "web/package.json"
Cohesion: 0.09
Nodes (29): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, jsdom@^31.0.1, openapi-typescript@^7.13.0, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3 (+21 more)

### Community 3 - "test_pitch.py"
Cohesion: 0.07
Nodes (45): apply_patch(), available_figure_paths(), build_prompt(), check_plan(), add(), fallback_figures(), figure_problem(), format_figure_paths() (+37 more)

### Community 4 - "ref_react"
Cohesion: 0.06
Nodes (18): AppLayout(), metadata, ShareLayout(), AppShell(), Brand(), BudgetMeter(), NAV_ITEMS, NavItem (+10 more)

### Community 5 - "Tasks"
Cohesion: 0.08
Nodes (26): Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues), Increment 7: hardening (visible: request changes, budget pause, share zip), Task 10: Sector kits and starters  [after: 1, parallel with 4-9] (+18 more)

### Community 6 - "runs-view.tsx"
Cohesion: 0.08
Nodes (36): RunsPage(), durationMs(), formatDuration(), formatUsd(), formatWhen(), matchesFilter(), matchesQuery(), PLACEHOLDER (+28 more)

### Community 7 - "_t"
Cohesion: 0.11
Nodes (20): ao(), CO(), Da(), Dv(), dx(), e3(), f1(), hx() (+12 more)

### Community 8 - "test_manager.py"
Cohesion: 0.25
Nodes (15): Fake, make_runs(), record_previews(), recorded(), test_a_process_that_died_after_the_http_check_is_not_served(), test_concurrent_ensure_gets_distinct_ports(), test_dead_server_is_restarted(), test_failed_start_releases_the_reservation_and_stop_drops_the_lock() (+7 more)

### Community 9 - "ChatReply"
Cohesion: 0.13
Nodes (5): MockProvider, _reskin_screens(), Recorder, test_fixture_is_a_port_fix(), Recorder

### Community 10 - "deck-view.tsx"
Cohesion: 0.17
Nodes (15): DeckPage(), DeckPanel(), DeckView(), DocsPanel(), ErrorBanner(), formatTime(), VideoPanel(), VideoState (+7 more)

### Community 11 - "steps"
Cohesion: 0.08
Nodes (25): runs-on, steps, timeout-minutes, env, APP_ENV, GITHUB_MODE, LLM_PROVIDER, jobs (+17 more)

### Community 12 - "brief-view.tsx"
Cohesion: 0.13
Nodes (30): BriefPage(), BriefFeatures(), PRIORITIES, Props, BriefGoalsPanel(), Props, BriefSide(), Props (+22 more)

### Community 13 - "procs.py"
Cohesion: 0.20
Nodes (4): kill_pid_tree(), pid_alive(), process_image(), _kill_tree()

### Community 14 - "complete_json"
Cohesion: 0.17
Nodes (12): RunBudget, complete_json(), repair_prompt(), strip_fences(), Answer, test_free_model_ignores_budget(), test_over_budget_raises_before_any_call(), test_mask_applied_to_user_text() (+4 more)

### Community 16 - "_to_end"
Cohesion: 0.28
Nodes (6): test_failing_recorder_fails_the_step_but_not_the_run(), boom(), test_no_placeholder_warning_without_video_fake(), test_startup_logs_a_warning_when_video_fake_is_set(), test_video_fake_emits_a_placeholder_warning(), _to_end()

### Community 17 - "validate.py"
Cohesion: 0.12
Nodes (22): DeckPlanInvalid, _added_css(), format_issues(), repair_prompt(), ScreenPackInvalid, url_problem(), Screen, _anchor_issues() (+14 more)

### Community 18 - "parse_build_error"
Cohesion: 0.21
Nodes (12): _clean(), excerpt_from_file(), _next_block(), parse_build_error(), test_cannot_find_name(), test_clean_output_is_not_an_error(), test_excerpt_from_disk_marks_the_error_line(), test_excerpt_is_confined_to_the_app_dir() (+4 more)

### Community 19 - "A"
Cohesion: 0.08
Nodes (48): Ad(), bh(), bo(), Br(), Bu(), bx(), Cr(), Dr() (+40 more)

### Community 20 - "new-run-form.tsx"
Cohesion: 0.11
Nodes (25): NewRunPage(), FileDrop(), Props, buildRunForm(), NewRunForm(), DEFAULT_OPTIONS, OptionSwitches(), Props (+17 more)

### Community 21 - "app.js"
Cohesion: 0.12
Nodes (19): 7b. Pipeline, schemas and budgets (resolved after the builder check, Claude's call unless marked), steps(), step(), Anchors, Component classes, ecommerce kit: selector and anchor guide, Example screens, Scoping (+11 more)

### Community 22 - "ScreenPack"
Cohesion: 0.08
Nodes (45): assemble(), _check_css(), _check_html(), fail(), _check_script(), DeckNotSelfContained, _json_for_script(), _read() (+37 more)

### Community 23 - "_Converter"
Cohesion: 0.16
Nodes (4): _attr_value(), _Converter, jsx_attr_name(), _text()

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.18
Nodes (10): 7 agents, Commands, Core tech stack (budget build, decided at intake), graphify, Human approval gates, Knowledge graph (graphify), Mission, PoC Studio — Developer Guidelines & Architecture Rules (+2 more)

### Community 25 - "test_settings.py"
Cohesion: 0.19
Nodes (8): _gateway_mode(), secrets_set(), test_key_not_set_reads_false(), test_put_never_writes_env(), test_put_updates_the_budget_and_persists(), test_test_gateway_failure_is_reported_without_the_key(), test_test_gateway_in_mock_mode_makes_no_network_call(), test_test_gateway_lists_models_only()

### Community 26 - "github/publish.py"
Cohesion: 0.05
Nodes (47): GitHubClient, GitHubError, RepoInfo, RepoNameTaken, _check_clean(), _copy(), _create_repo(), default_repo_name() (+39 more)

### Community 27 - "checks.py"
Cohesion: 0.14
Nodes (35): build_passed(), Check, costs_consistent(), _css_problems(), deck_present(), deck_self_contained(), _deck_text(), _fail() (+27 more)

### Community 28 - "ecommerce/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 29 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.29
Nodes (6): 6 Specialist Agents & State, Coding Style & Budget Rules, Core Tech Stack, Human Approval Gates, Mission, PoC Studio — Developer Guidelines & Architecture Rules

### Community 30 - "UI preview"
Cohesion: 0.33
Nodes (5): After approval, Build, Layout, Rules, UI preview

### Community 31 - "runtime.js"
Cohesion: 0.20
Nodes (14): buildScreen(), check(), clearSpot(), countUp(), describe(), fitText(), flatIndex(), goTo() (+6 more)

### Community 32 - "constructor"
Cohesion: 0.06
Nodes (56): addListeners(), af(), attachTimeline(), cancel(), clearAnimation(), clearListeners(), commitStyles(), constructor() (+48 more)

### Community 33 - "redact"
Cohesion: 0.18
Nodes (6): install_log_redaction(), redact_obj(), test_dict_key_masks_whole_value(), test_log_records_from_child_loggers_are_redacted(), test_more_secret_shapes_are_masked(), test_plain_words_are_left_alone()

### Community 34 - "Architecture"
Cohesion: 0.20
Nodes (10): Architecture, Component, CostLine, ModelPick, MonthlyCost, Phase, _fixture(), test_mermaid_must_be_a_diagram() (+2 more)

### Community 35 - "timeline-view.tsx"
Cohesion: 0.08
Nodes (50): RunTimelinePage(), CostByModel(), COPY, GateRow(), NextForYou(), CLASS, elapsed(), PipelineStep() (+42 more)

### Community 36 - "run-context.tsx"
Cohesion: 0.06
Nodes (45): RunLayout(), BannerProps, BudgetBanner(), RunBudgetBanner(), RequestChanges(), RequestChangesProps, ReviseButton(), RunContext (+37 more)

### Community 37 - "re"
Cohesion: 0.14
Nodes (21): Task 11: Prototype Builder: ScreenPack  [after: 9, 10], Task 14: Vendored deck engine and assembler  [after: 1, parallel with 4-13; runs on the owner's machine, where `reference/` exists], test_no_external_src_or_href(), anchors_of(), build_pack(), build_plan(), step_css(), _defined_classes() (+13 more)

### Community 38 - "parse.py"
Cohesion: 0.28
Nodes (12): Segment, _line_segment(), _paragraph_segments(), _parse_docx(), _parse_pdf(), _parse_plain(), _parse_txt(), _parse_vtt_file() (+4 more)

### Community 39 - "test_run_eval.py"
Cohesion: 0.27
Nodes (10): _load(), restore_env(), test_dry_eval_restores_the_env_and_the_runner(), test_dry_eval_two_fixtures(), test_dry_full_stage_two_fixtures(), test_full_live_is_refused_without_the_flag(), test_github_is_forced_to_mock_and_video_to_fake_even_when_live(), test_live_is_refused_inside_run_eval_without_the_flag() (+2 more)

### Community 40 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, dev, lint, test, typecheck, version (+1 more)

### Community 41 - "secrets.py"
Cohesion: 0.10
Nodes (23): _assignment_is_secret(), env_file_path(), env_hashes(), _files(), Finding, _hashes_of(), _kind(), _line_at() (+15 more)

### Community 42 - "fintech/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 43 - "test_artifacts_files.py"
Cohesion: 0.27
Nodes (8): names(), test_build_returns_build_json(), test_file_tree_depth_is_capped_at_six(), test_file_tree_skips_node_modules_next_and_dotfiles(), test_files_and_build_404_for_unknown_run_and_no_app(), test_preview_409_until_built_then_redirects_to_the_direct_url(), test_traversal_is_impossible_there_is_no_path_input(), write()

### Community 44 - "t"
Cohesion: 0.07
Nodes (38): Be(), bg(), c2(), cl(), cx(), DM(), fa(), fx() (+30 more)

### Community 45 - "test_validate.py"
Cohesion: 0.10
Nodes (23): codes(), mutated(), test_anchor_matching_nothing_fails_the_schema(), test_anchors_must_be_unique_per_screen(), test_app_class_must_equal_the_kit(), test_at_least_three_play_screens(), test_classes_must_be_defined(), test_event_handler_attributes_are_rejected() (+15 more)

### Community 46 - "screenpack.py"
Cohesion: 0.19
Nodes (10): route_file(), html_to_jsx(), _as_xml(), _balanced(), test_attribute_and_text_rules(), test_braces_are_balanced_jsx_expressions(), test_every_screen_converts_to_wellformed_jsx(), test_invalid_tag_names_are_dropped_but_text_kept() (+2 more)

### Community 49 - "test_port.py"
Cohesion: 0.19
Nodes (5): set_preview_manager(), FakeBuild, FakePreviews, test_a_port_run_stops_that_runs_preview_first(), test_reset_stops_the_preview_and_deletes_a_stale_build_json()

### Community 51 - "healthcare/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 52 - "logistics/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 53 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 54 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 55 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 61 - "api.ts"
Cohesion: 0.18
Nodes (17): PrototypePage(), BuildLog(), BuildStatus(), Device, DeviceFrame(), DeviceToggle(), FileTree(), Nodes() (+9 more)

### Community 62 - "test_env.py"
Cohesion: 0.12
Nodes (23): strip_ansi(), build(), child_env(), _command(), container_name(), _docker_kill(), install(), prepare() (+15 more)

### Community 64 - "settings.py"
Cohesion: 0.21
Nodes (12): BudgetPatch, BudgetSettings, _client(), current(), GatewayPatch, GatewaySettings, GatewayTest, get_current_settings() (+4 more)

### Community 67 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 68 - "media/video.py"
Cohesion: 0.17
Nodes (13): Chapter, _deck_slides(), fake_record(), _ffmpeg(), _finish(), probe(), record(), _to_mp4() (+5 more)

### Community 69 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "0005_repo_artifact.py"
Cohesion: 0.83
Nodes (3): downgrade(), _swap(), upgrade()

### Community 71 - "ref_node_path"
Cohesion: 0.08
Nodes (14): SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, @playwright/test@^1.65.1 (+6 more)

### Community 72 - "run_eval.py"
Cohesion: 0.12
Nodes (24): _clear_caches(), client_name_from(), configure_env(), feature_found(), _finish_full(), _fmt_time(), _isolated(), LiveRefused (+16 more)

### Community 73 - "_make_binary_fixtures.py"
Cohesion: 0.24
Nodes (3): _esc(), make_docx(), make_pdf()

### Community 74 - "build.py"
Cohesion: 0.12
Nodes (9): Request changes, retry and budget, after_gate1(), after_gate2(), after_qa(), build_graph(), collect_nodes(), state(), test_default_app_has_no_stub_nodes() (+1 more)

### Community 75 - "PoC Studio: design spec"
Cohesion: 0.12
Nodes (16): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+8 more)

### Community 76 - "BuildResult"
Cohesion: 0.20
Nodes (7): BuildResult, _no_real_npm(), fake_build(), fake_install(), _no_real_recorder(), failing_build(), build()

### Community 79 - "build_share_zip"
Cohesion: 0.16
Nodes (16): build_share_zip(), ShareBlocked, ShareUnavailable, external_refs(), run_dir(), _names(), test_export_is_recorded_once_per_path(), test_external_assets_are_refused() (+8 more)

### Community 80 - "A"
Cohesion: 0.07
Nodes (38): A(), a1(), Ar(), aT(), Av(), b1(), b3(), bi() (+30 more)

### Community 81 - "Technical Requirements Document: Returns and Substitution Assistant"
Cohesion: 0.12
Nodes (16): 1. Summary, 2. Problem, 3.1 Smart substitution ranking, 3.2 Preference-safe rules, 3.3 Claim triage, 3.4 Agent review console, 3.5 Customer reply drafting, 3.6 Reporting (+8 more)

### Community 82 - "Technical Requirements Document: Last-Mile Route Re-Optimiser"
Cohesion: 0.12
Nodes (16): Acceptance criteria, Action items, Budget and schedule, Current system, Data, Functional requirements, Non-functional requirements, Open questions (+8 more)

### Community 83 - "Business Requirements Document: Dock Scheduling Assistant"
Cohesion: 0.14
Nodes (13): 10. Action items, 11. Risks, 12. Glossary, 1. Background, 2. Problem statement, 3. Goals, 4. Must-have features, 5. Nice-to-have features (+5 more)

### Community 84 - "sd"
Cohesion: 0.08
Nodes (33): _1(), ab(), Ex(), fu(), Gx(), h1(), ib(), iO() (+25 more)

### Community 85 - "intelligence.py"
Cohesion: 0.08
Nodes (27): apply_owner_input(), build_prompt(), _client_name(), format_ts(), load_transcript(), next_requirements_version(), _norm(), _project_input() (+19 more)

### Community 86 - "Business Requirements Document: Patient Intake and Prior Authorisation Assistant"
Cohesion: 0.17
Nodes (11): 10. Risks, 1. Context, 2. Current pain points, 3. Objectives, 4. Must-have capabilities, 5. Should-have capabilities, 6. Compliance and security, 7. Budget and timeline (+3 more)

### Community 87 - "Wv"
Cohesion: 0.09
Nodes (48): Ai(), Ax(), Az(), Bv(), De(), ep(), eT(), Ft() (+40 more)

### Community 88 - "PreviewManager"
Cohesion: 0.13
Nodes (5): lifespan(), Entry, PreviewManager, loop(), looks_like_preview_image()

### Community 89 - "dependencies"
Cohesion: 0.14
Nodes (14): dependencies, @fontsource-variable/geist@^5.3.0, @fontsource-variable/geist-mono@^5.3.0, lucide-react@^1.77.0, mermaid@^12.3.0, next@16.4.6, react@19.3.0, react-dom@19.3.0 (+6 more)

### Community 90 - "env"
Cohesion: 0.15
Nodes (4): _clear_caches(), client_for(), make(), env()

### Community 92 - "test_screens.py"
Cohesion: 0.14
Nodes (21): set_provider(), _full_run(), _drive(), _run(), Recorder, _run_to_screens(), test_mock_screens_follow_the_chosen_sector_kit(), test_repair_prompt_names_the_issue_codes() (+13 more)

### Community 93 - "share-api.ts"
Cohesion: 0.06
Nodes (37): SettingsPage(), TemplatesPage(), SharePage(), KeyStatus(), buildPatch(), Draft, SettingsForm(), save() (+29 more)

### Community 94 - "test_retention.py"
Cohesion: 0.42
Nodes (6): on_startup(), apply_retention(), test_default_is_off_and_startup_deletes_nothing(), test_old_inputs_are_deleted_and_artifacts_kept(), test_zero_days_turns_it_off(), _with_input()

### Community 95 - "test_json.py"
Cohesion: 0.20
Nodes (11): Task 4: LLM client, mock provider, budget guard  [after: 1], SchemaError, _call(), _run(), test_fenced_reply_parses(), test_mock_provider_fixture(), test_repair_on_second_attempt(), test_schema_error_repair_quotes_the_validation_error() (+3 more)

### Community 96 - "bT"
Cohesion: 0.22
Nodes (11): cp(), cV(), dc(), dT(), fc(), ip(), mT(), pu() (+3 more)

### Community 99 - "Sector templates"
Cohesion: 0.40
Nodes (4): How the builder uses a kit, Sector templates, Starters, Tests

### Community 100 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 111 - "seed_run"
Cohesion: 0.20
Nodes (10): ShareToken, _fixture(), seed_run(), test_expired_token_is_404_on_a_fake_clock(), test_public_json(), test_run_must_be_delivered_or_at_gate2_with_a_deck(), test_share_export_route_and_download(), test_share_export_with_a_secret_is_422_without_the_value() (+2 more)

### Community 112 - "client"
Cohesion: 0.08
Nodes (56): test_graph_run_writes_architecture(), test_markdown_download_rejects_other_types(), _brief(), _create(), test_client_and_sector_follow_the_owners_input(), test_extracted_sector_is_kept_when_the_owner_picked_none(), test_gate1_changes_makes_v2_with_note(), test_unsupported_constraint_unconfirmed() (+48 more)

### Community 113 - "settings_store.py"
Cohesion: 0.22
Nodes (7): update_settings(), apply_overrides(), effective_hours_saved(), load(), save(), settings_path(), StoredSettings

### Community 114 - "W"
Cohesion: 0.06
Nodes (54): aS(), bp(), ch(), ci(), cM(), Cn(), cS(), dh() (+46 more)

### Community 115 - "deck.py"
Cohesion: 0.17
Nodes (6): _add_slide(), build_pptx(), _figure_value(), _rgb(), _text(), Slide

### Community 116 - "gate2-view.tsx"
Cohesion: 0.08
Nodes (50): Page(), ConfirmPublish(), Props, DeliveredView(), InAppItem(), ItemProps, summary(), Gate2View() (+42 more)

### Community 117 - "loose_match"
Cohesion: 0.50
Nodes (3): loose_match(), _words(), test_loose_match_is_60_percent_of_long_words()

### Community 118 - "artifacts.py"
Cohesion: 0.13
Nodes (13): download_markdown_artifact(), FileNode, get_build(), get_deck_html(), get_deck_pptx(), get_doc(), get_file_tree(), get_json_artifact() (+5 more)

### Community 120 - "FakeProvider"
Cohesion: 0.27
Nodes (10): FakeProvider, _call(), EmptyThenOk, test_caller_note_replaces_the_default(), test_empty_answer_retries_fresh_and_passes_reasoning_effort(), test_only_empty_answers_raise_a_clear_error(), test_other_broken_json_gets_a_short_note(), test_retries_do_not_grow_after_repeated_truncation() (+2 more)

### Community 121 - "Decisions"
Cohesion: 0.33
Nodes (5): Decisions, GitHub publish, Resolved values, Task 1 notes, Verified prices

### Community 122 - "decide"
Cohesion: 0.27
Nodes (14): decide(), Decision, bad(), ok(), test_after_two_send_backs_none_are_made_but_secrets_still_block(), test_all_passing_sends_nothing_back(), test_assemble_and_video_owners_are_never_sent_back(), test_build_failure_is_report_only() (+6 more)

### Community 126 - "build.mjs"
Cohesion: 0.27
Nodes (7): SAMPLE, status(), waitFor(), build(), here, orderScripts(), read()

### Community 127 - "RunEvent"
Cohesion: 0.21
Nodes (5): Event, EventBus, Subscription, to_event(), RunEvent

### Community 128 - "architecture-view.tsx"
Cohesion: 0.13
Nodes (21): ArchitecturePage(), ArchitectureView(), Load, CostTable(), MermaidDiagram(), Result, themeVariables(), token() (+13 more)

### Community 129 - "RunService"
Cohesion: 0.09
Nodes (15): new_run_id(), decide_gate(), _publish_options(), BudgetRequest, _fail(), _port_failed(), raise_budget(), retry_run() (+7 more)

### Community 130 - "schemas.py"
Cohesion: 0.13
Nodes (21): AgentStepOut, ArtifactJson, ArtifactOut, BudgetRaiseRequest, CreateRunOptions, CreateRunResponse, EventError, GateDecisionRequest (+13 more)

### Community 132 - "export_share"
Cohesion: 0.21
Nodes (10): create_share_token(), download_share_zip(), export_share(), get_share_deck(), get_share_page(), get_share_video(), ShareExportOut, SharePageOut (+2 more)

### Community 133 - "TestClient"
Cohesion: 0.28
Nodes (10): test_a_bad_host_is_400(), test_a_post_without_origin_passes(), test_gets_are_never_blocked(), test_json_post_from_a_foreign_origin_is_403(), test_json_post_from_the_app_origin_passes(), test_local_hosts_are_allowed(), test_multipart_run_creation_from_the_app_origin_passes(), test_put_and_delete_are_guarded_too() (+2 more)

### Community 134 - "open_session"
Cohesion: 0.04
Nodes (80): Task 6: Run engine, events, SSE, gates  [after: 4, 5], build_prompt(), _latest_requirements(), persist_architecture(), render_markdown(), run_architect(), run_assemble(), _run_assemble() (+72 more)

### Community 136 - "test_full_run.py"
Cohesion: 0.30
Nodes (9): _agents(), _artifacts(), _assert_order(), _drive(), _reports(), test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(), test_full_run_through_both_gates_to_delivered(), test_planted_secret_sends_back_port_only_and_blocks_publish() (+1 more)

### Community 138 - "eo"
Cohesion: 0.08
Nodes (32): $d(), eo(), ey(), Fh(), Fv(), hc(), hE(), hp() (+24 more)

### Community 139 - "test_event_loop.py"
Cohesion: 0.23
Nodes (3): loop_factory(), test_loop_can_start_subprocesses(), test_windows_gets_the_proactor_loop()

### Community 142 - "test_a_raise_resumes_with_no_duplicate_paid_call"
Cohesion: 0.23
Nodes (9): _fail_builds(), _paid(), PaidRecorder, _paused(), test_a_raise_resumes_with_no_duplicate_paid_call(), test_invalid_budgets_are_rejected(), test_retry_attempts_limit_the_builds(), test_retry_with_a_note_reruns_only_port_with_the_note() (+1 more)

### Community 144 - "app.js"
Cohesion: 0.22
Nodes (8): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T

### Community 145 - "test_jsx.py"
Cohesion: 0.12
Nodes (15): node_access_problem(), apply_fix(), FixFile, PortFix, safe_path(), UnsafePath, page_source(), test_apply_fix_skips_a_rejected_file_with_a_reason_and_applies_the_rest() (+7 more)

### Community 146 - "llm/client.py"
Cohesion: 0.14
Nodes (12): LLM pricing, BudgetExceeded, count_tokens(), InputTooLarge, cost_usd(), is_claude(), prices(), architect() (+4 more)

### Community 147 - "test_qa_node.py"
Cohesion: 0.28
Nodes (7): _drive(), _reports(), _steps(), test_missing_deck_fails_deck_present_and_the_run_still_reaches_gate2(), test_mock_run_reaches_gate2_with_a_passing_qa_report(), test_planted_secret_sends_port_back_twice_then_blocks_publish(), test_real_run_without_a_deck_is_flagged_even_without_a_failure_marker()

### Community 148 - "Settings"
Cohesion: 0.13
Nodes (11): Settings, GatewayProvider, test_fast_model_live(), _call(), test_explicit_timeout_wins(), test_gateway_sdk_does_not_retry(), test_setting_defaults_to_300_and_reads_env(), test_timeout_defaults_to_settings() (+3 more)

### Community 149 - "el"
Cohesion: 0.40
Nodes (8): build(), buildClose(), buildPlay(), buildWelcome(), el(), header(), spot(), txt()

### Community 150 - "test_drift.py"
Cohesion: 0.32
Nodes (5): _product_css(), _screen_html(), change(), _script(), test_style_is_forbidden_by_the_validator_only()

### Community 151 - "test_client.py"
Cohesion: 0.23
Nodes (10): http_ready(), _client(), wrapped(), test_create_issue_and_repo_exists(), handler(), test_create_repo_name_clash_is_its_own_error(), test_create_repo_posts_to_user_repos_private(), test_errors_never_carry_the_token() (+2 more)

### Community 154 - "web/app/layout.tsx"
Cohesion: 0.28
Nodes (6): metadata, RootLayout(), AppToaster(), TOAST_OPTIONS, sileo@^0.1.6, sileo

### Community 155 - "parse_file"
Cohesion: 0.17
Nodes (14): Transcript, parse_file(), parse_files(), test_fixture_exists_and_parses(), _close(), test_docx_includes_table_cells(), test_file_over_20mb_raises(), test_md_paragraphs() (+6 more)

### Community 156 - "pytest"
Cohesion: 0.11
Nodes (22): plan_holds(), _deck_files(), test_assembled_deck_runs_every_step(), test_graph_run_assembles_a_self_contained_deck(), browser_name_and_browser(), deck_html(), icons_css(), pack() (+14 more)

### Community 157 - "test_degrade.py"
Cohesion: 0.44
Nodes (7): _drive(), _empty(), _errors(), _step(), test_pitch_with_invalid_plans_after_repairs_fails_and_the_run_reaches_gate2(), test_real_run_with_missing_inputs_fails_the_steps_but_reaches_gate2(), test_stub_graphs_still_skip_silently()

### Community 158 - "dev.mjs"
Cohesion: 0.16
Nodes (10): @vitejs/plugin-react@^6.3.0, @vitejs/plugin-react, children, kill(), root, shutdown(), start(), api (+2 more)

### Community 159 - "mountScreen"
Cohesion: 0.40
Nodes (4): 7a. Deck and prototype output contract (amendment 8), show(), mountScreen(), toast()

### Community 161 - "page.py"
Cohesion: 0.19
Nodes (5): ShareContent, render_pdf(), render_index(), _tokens(), write_pdf()

### Community 162 - "_ensure"
Cohesion: 0.33
Nodes (4): _ensure(), PreviewInfo, redirect_preview(), start_preview()

### Community 163 - "runs.py"
Cohesion: 0.08
Nodes (19): mask_for_run(), mask_pii(), _options_path(), run_masks_pii(), write_run_options(), create_run(), get_run(), get_service() (+11 more)

### Community 164 - "load_kit"
Cohesion: 0.14
Nodes (10): layout_source(), nav_source(), write_app(), port_is_free(), ExampleScreen, Kit, load_kit(), test_fixture_is_a_repair_scenario() (+2 more)

### Community 165 - "healthcare kit: selector and anchor guide"
Cohesion: 0.40
Nodes (4): Anchors, Example screens, healthcare kit: selector and anchor guide, Scoping

### Community 166 - "post"
Cohesion: 0.36
Nodes (4): post(), test_colon_names_rejected(), test_too_many_files(), test_total_size_limit()

### Community 167 - "test_gate_events.py"
Cohesion: 0.24
Nodes (3): stream_events(), test_event_stream_holds_no_request_session(), test_gate_decision_event_is_emitted_once()

### Community 168 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, gen:types, lint, start, test (+1 more)

### Community 169 - "tokens.py"
Cohesion: 0.33
Nodes (4): create_token(), hash_token(), resolve_token(), _utcnow()

### Community 171 - "get_publish"
Cohesion: 0.31
Nodes (5): _approved_options(), _failure(), get_publish(), PublishStatus, _result()

### Community 173 - "Eval"
Cohesion: 0.22
Nodes (8): Dry mode, Eval, Flags, Isolation, Live mode, Measures, Stages, Success measures (full summary)

### Community 174 - "get_github"
Cohesion: 0.32
Nodes (4): get_github(), GitHubNotConfigured, test_get_github_refuses_live_without_a_token(), test_get_github_selects_by_mode()

### Community 177 - "event_name"
Cohesion: 0.50
Nodes (3): event_name(), event_stream(), _sse()

### Community 182 - "PoC Studio build plan"
Cohesion: 0.33
Nodes (5): File map, Global constraints, Owner-only steps, Parked (NEXT_STEPS.md), PoC Studio build plan

### Community 183 - "FileTooLarge"
Cohesion: 0.33
Nodes (3): Task 5: Ingest parsers and eval fixtures  [after: 1, parallel with 4], FileTooLarge, UnsupportedFile

### Community 185 - "open_session"
Cohesion: 0.09
Nodes (28): _record_usage(), AgentStep, Artifact, open_session(), load_events(), _resolve(), Result, ChatProvider (+20 more)

### Community 186 - "guard.py"
Cohesion: 0.13
Nodes (4): _forbidden(), UnsafeRequestGuard, create_app(), health()

### Community 188 - "test_intelligence_is_unmasked_by_default"
Cohesion: 0.50
Nodes (3): _run_with(), test_intelligence_is_unmasked_by_default(), test_intelligence_sends_a_masked_prompt_when_the_option_is_on()

### Community 199 - "db/models.py"
Cohesion: 0.04
Nodes (33): run_migrations_offline(), run_migrations_online(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), _a() (+25 more)

## Knowledge Gaps
- **1 isolated node(s):** `poc-studio-api`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1186 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `up()` connect `bT` to `toast.js`, `i`, `A`, `app.js`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **What connects `poc-studio-api` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013941543353308059 - nodes in this community are weakly interconnected._
- **Why does `steps()` connect `app.js` to `re`, `healthcare kit: selector and anchor guide`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.06256384065372829 - nodes in this community are weakly interconnected._
- **Why does `build_plan()` connect `re` to `app.js`, `ScreenPack`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Should `web/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.09247311827956989 - nodes in this community are weakly interconnected._