# Graph Report - poc-studio  (2026-11-23)

## Corpus Check
- 403 files · ~174,020 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .css 34, (none) 11, .vtt 5)

## Summary
- 3909 nodes · 11075 edges · 185 communities (136 shown, 49 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 937 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6769a99`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- toast.js
- i
- web/package.json
- test_pitch.py
- react
- Tasks
- runs-view.tsx
- _t
- test_manager.py
- MockProvider
- api.ts
- steps
- brief-view.tsx
- PreviewManager
- test_run_eval.py
- llm/client.py
- open_session
- validate.py
- parse_build_error
- A
- new-run-form.tsx
- app.js
- ScreenPack
- get_settings
- PoC Studio — Developer Guidelines & Architecture Rules
- 0005_repo_artifact.py
- github/publish.py
- checks.py
- ecommerce/app/package.json
- PoC Studio — Developer Guidelines & Architecture Rules
- UI preview
- runtime.js
- constructor
- redact
- secrets.py
- timeline-view.tsx
- run-context.tsx
- re
- parse.py
- share.py
- package.json
- screenpack.py
- fintech/app/package.json
- FakeProvider
- t
- test_validate.py
- port.py
- Run
- healthcare/app/package.json
- logistics/app/package.json
- compilerOptions
- compilerOptions
- compilerOptions
- owner-direction-2026-11-22.md
- NEXT_STEPS.md
- check-github-token.sh
- api.ts
- test_budget_additive.py
- poc-studio-api
- settings.py
- compilerOptions
- media/video.py
- compilerOptions
- RunState
- ref_node_path
- run_eval.py
- _make_binary_fixtures.py
- build.py
- PoC Studio: design spec
- tests/conftest.py
- seed_run
- A
- Technical Requirements Document: Returns and Substitution Assistant
- Technical Requirements Document: Last-Mile Route Re-Optimiser
- Business Requirements Document: Dock Scheduling Assistant
- sd
- Run
- Business Requirements Document: Patient Intake and Prior Authorisation Assistant
- Wv
- json
- dependencies
- env
- Recorder
- share-api.ts
- db/models.py
- complete_json
- bT
- sample.md
- Sector templates
- web/README.md
- AGENTS.md
- test_degrade.py
- wait_status
- GitHubClient
- W
- deck.py
- gate2-view.tsx
- test_assemble_node.py
- _latest_file
- test_publish.py
- test_port.py
- PoC Studio build plan
- test_intelligence.py
- tokens.py
- build.mjs
- test_pii.py
- architecture-view.tsx
- RunService
- schemas.py
- runner.py
- TestClient
- architecture.py
- test_full_run.py
- deck_runtime/README.md
- eo
- parse_file
- page.py
- test_artifacts_files.py
- app.js
- test_jsx.py
- complete_json
- MockGitHub
- Settings
- el
- test_drift.py
- Settings
- test_tokens.py
- web/app/layout.tsx
- Decisions
- _fake_pdf
- test_env.py
- dev.mjs
- mountScreen
- MockProvider
- poc_studio/events.py
- datetime
- _fixture
- LiveGitHub
- healthcare kit: selector and anchor guide
- requirements.py
- poc_studio/ingest/__init__.py
- scripts
- FileTooLarge
- procs.py
- _drive
- main.py
- test_gate2.py
- manager.py
- _ensure
- now

## God Nodes (most connected - your core abstractions)
1. `open_session()` - 135 edges
2. `get_settings()` - 113 edges
3. `wait_status()` - 90 edges
4. `client()` - 87 edges
5. `create_run()` - 81 edges
6. `ScreenPack` - 80 edges
7. `DeckPlan` - 74 edges
8. `Run` - 70 edges
9. `Artifact` - 68 edges
10. `A()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `Task 4: LLM client, mock provider, budget guard  [after: 1]` --references--> `SchemaError`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/llm/client.py
- `7. Data model and interfaces` --references--> `DeckPlan`  [INFERRED]
  docs/specs/2026-11-22-poc-studio-design.md → services/api/poc_studio/schemas/deck.py
- `File map` --references--> `NodeSpec`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/graph/registry.py
- `Example screens` --references--> `steps()`  [INFERRED]
  templates/healthcare/kit/selectors.md → services/api/tests/fixtures/deck/build_fixture.py
- `Task 15: Pitch and Docs agent  [after: 11, 14]` --references--> `BudgetExceeded`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/llm/budget.py

## Import Cycles
- None detected.

## Communities (185 total, 49 thin omitted)

### Community 0 - "toast.js"
Cohesion: 0.01
Nodes (137): _4(), add(), addValue(), addVariantChild(), Ag(), b4(), bindToMotionValue(), BM() (+129 more)

### Community 1 - "i"
Cohesion: 0.06
Nodes (88): Aa(), ap(), bD(), bT(), c1(), Cg(), cT(), Dd() (+80 more)

### Community 2 - "web/package.json"
Cohesion: 0.09
Nodes (31): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, jsdom@^31.0.1, openapi-typescript@^7.13.0, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3 (+23 more)

### Community 3 - "test_pitch.py"
Cohesion: 0.15
Nodes (21): apply_patch(), _pick(), polish_input(), PolishPatch, codes(), _load(), plan(), _run() (+13 more)

### Community 4 - "react"
Cohesion: 0.06
Nodes (18): AppLayout(), metadata, ShareLayout(), AppShell(), Brand(), BudgetMeter(), NAV_ITEMS, NavItem (+10 more)

### Community 5 - "Tasks"
Cohesion: 0.07
Nodes (29): Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues), Increment 7: hardening (visible: request changes, budget pause, share zip), Task 10: Sector kits and starters  [after: 1, parallel with 4-9] (+21 more)

### Community 6 - "runs-view.tsx"
Cohesion: 0.10
Nodes (29): RunsPage(), durationMs(), formatDuration(), formatUsd(), formatWhen(), matchesFilter(), matchesQuery(), PLACEHOLDER (+21 more)

### Community 7 - "_t"
Cohesion: 0.11
Nodes (20): ao(), CO(), Da(), Dv(), dx(), e3(), f1(), hx() (+12 more)

### Community 8 - "test_manager.py"
Cohesion: 0.25
Nodes (15): Fake, make_runs(), record_previews(), recorded(), test_a_process_that_died_after_the_http_check_is_not_served(), test_concurrent_ensure_gets_distinct_ports(), test_dead_server_is_restarted(), test_failed_start_releases_the_reservation_and_stop_drops_the_lock() (+7 more)

### Community 9 - "MockProvider"
Cohesion: 0.16
Nodes (3): ChatReply, _reskin_screens(), AlwaysInvalidPitch

### Community 10 - "api.ts"
Cohesion: 0.12
Nodes (24): DeckPage(), Page(), TemplatesPage(), DeckPanel(), DeckView(), DocsPanel(), ErrorBanner(), formatTime() (+16 more)

### Community 11 - "steps"
Cohesion: 0.08
Nodes (25): runs-on, steps, timeout-minutes, env, APP_ENV, GITHUB_MODE, LLM_PROVIDER, jobs (+17 more)

### Community 12 - "brief-view.tsx"
Cohesion: 0.13
Nodes (30): BriefPage(), BriefFeatures(), PRIORITIES, Props, BriefGoalsPanel(), Props, BriefSide(), Props (+22 more)

### Community 13 - "PreviewManager"
Cohesion: 0.16
Nodes (3): PreviewManager, loop(), test_build_serve_get_stop()

### Community 14 - "test_run_eval.py"
Cohesion: 0.27
Nodes (10): _load(), restore_env(), test_dry_eval_restores_the_env_and_the_runner(), test_dry_eval_two_fixtures(), test_dry_full_stage_two_fixtures(), test_full_live_is_refused_without_the_flag(), test_github_is_forced_to_mock_and_video_to_fake_even_when_live(), test_live_is_refused_inside_run_eval_without_the_flag() (+2 more)

### Community 15 - "llm/client.py"
Cohesion: 0.18
Nodes (7): _resolve(), Result, SchemaError, repair_prompt(), strip_fences(), ChatProvider, get_provider()

### Community 16 - "open_session"
Cohesion: 0.09
Nodes (27): next_version(), _add_artifact(), _fake_enabled(), _latest_deck_html(), _record(), run_video(), VideoFailed, AgentStep (+19 more)

### Community 17 - "validate.py"
Cohesion: 0.18
Nodes (17): add(), DeckPlanInvalid, Screen, _anchor_issues(), _css_url_issues(), _defined_classes(), _html_issues(), _is_keyframes() (+9 more)

### Community 18 - "parse_build_error"
Cohesion: 0.20
Nodes (12): _clean(), excerpt_from_file(), _next_block(), parse_build_error(), test_cannot_find_name(), test_clean_output_is_not_an_error(), test_excerpt_from_disk_marks_the_error_line(), test_excerpt_is_confined_to_the_app_dir() (+4 more)

### Community 19 - "A"
Cohesion: 0.08
Nodes (48): Ad(), bh(), bo(), Br(), Bu(), bx(), Cr(), Dr() (+40 more)

### Community 20 - "new-run-form.tsx"
Cohesion: 0.10
Nodes (26): NewRunPage(), FileDrop(), Props, buildRunForm(), NewRunForm(), DEFAULT_OPTIONS, OptionSwitches(), Props (+18 more)

### Community 21 - "app.js"
Cohesion: 0.12
Nodes (19): 7b. Pipeline, schemas and budgets (resolved after the builder check, Claude's call unless marked), steps(), step(), Anchors, Component classes, ecommerce kit: selector and anchor guide, Example screens, Scoping (+11 more)

### Community 22 - "ScreenPack"
Cohesion: 0.08
Nodes (48): assemble(), _check_css(), _check_html(), fail(), _check_script(), DeckNotSelfContained, _json_for_script(), _read() (+40 more)

### Community 23 - "get_settings"
Cohesion: 0.09
Nodes (25): run_assemble(), _run_assemble(), build_prompt(), check_plan(), figure_problem(), Polished, PolishedSlide, repair_prompt() (+17 more)

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.18
Nodes (10): 7 agents, Commands, Core tech stack (budget build, decided at intake), graphify, Human approval gates, Knowledge graph (graphify), Mission, PoC Studio — Developer Guidelines & Architecture Rules (+2 more)

### Community 25 - "0005_repo_artifact.py"
Cohesion: 0.83
Nodes (3): downgrade(), _swap(), upgrade()

### Community 26 - "github/publish.py"
Cohesion: 0.15
Nodes (13): _copy(), _file_count(), _git(), git_auth_header(), _git_env(), _latest_path(), NothingToPublish, prepare_repo_dir() (+5 more)

### Community 27 - "checks.py"
Cohesion: 0.07
Nodes (62): Dry mode, Eval, Flags, Isolation, Live mode, Measures, Stages, Success measures (full summary) (+54 more)

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
Cohesion: 0.13
Nodes (10): install_log_redaction(), redact(), redact_obj(), RedactingFilter, test_redact_key_values_and_clean_text(), test_redact_masks_known_patterns(), test_dict_key_masks_whole_value(), test_log_records_from_child_loggers_are_redacted() (+2 more)

### Community 34 - "secrets.py"
Cohesion: 0.10
Nodes (21): _assignment_is_secret(), env_hashes(), _files(), _hashes_of(), _kind(), _line_at(), _name_forms(), scan_pii() (+13 more)

### Community 35 - "timeline-view.tsx"
Cohesion: 0.07
Nodes (56): RunTimelinePage(), CostByModel(), COPY, GateRow(), NextForYou(), CLASS, elapsed(), PipelineStep() (+48 more)

### Community 36 - "run-context.tsx"
Cohesion: 0.08
Nodes (35): RunLayout(), Props, BannerProps, BudgetBanner(), RunBudgetBanner(), RequestChanges(), RequestChangesProps, ReviseButton() (+27 more)

### Community 37 - "re"
Cohesion: 0.18
Nodes (17): test_no_external_src_or_href(), anchors_of(), build_pack(), _defined_classes(), _fragment(), _kit(), _strip_comments(), _strip_urls() (+9 more)

### Community 38 - "parse.py"
Cohesion: 0.28
Nodes (12): Segment, _line_segment(), _paragraph_segments(), _parse_docx(), _parse_pdf(), _parse_plain(), _parse_txt(), _parse_vtt_file() (+4 more)

### Community 39 - "share.py"
Cohesion: 0.16
Nodes (15): create_share_token(), download_share_zip(), export_share(), get_share_deck(), get_share_page(), get_share_video(), _manifest_warnings(), _shareable_run() (+7 more)

### Community 40 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, dev, lint, test, typecheck, version (+1 more)

### Community 41 - "screenpack.py"
Cohesion: 0.14
Nodes (11): route_file(), html_to_jsx(), Anchor, _as_xml(), _balanced(), test_attribute_and_text_rules(), test_braces_are_balanced_jsx_expressions(), test_every_screen_converts_to_wellformed_jsx() (+3 more)

### Community 42 - "fintech/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 43 - "FakeProvider"
Cohesion: 0.26
Nodes (9): FakeProvider, _call(), _run(), test_fenced_reply_parses(), test_mock_provider_fixture(), test_repair_on_second_attempt(), test_schema_in_system_prompt(), test_three_invalid_raise() (+1 more)

### Community 44 - "t"
Cohesion: 0.07
Nodes (38): Be(), bg(), c2(), cl(), cx(), DM(), fa(), fx() (+30 more)

### Community 45 - "test_validate.py"
Cohesion: 0.10
Nodes (23): codes(), mutated(), test_anchor_matching_nothing_fails_the_schema(), test_anchors_must_be_unique_per_screen(), test_app_class_must_equal_the_kit(), test_at_least_three_play_screens(), test_classes_must_be_defined(), test_event_handler_attributes_are_rejected() (+15 more)

### Community 46 - "port.py"
Cohesion: 0.14
Nodes (17): _fix(), fix_prompt(), layout_source(), nav_source(), persist_prototype(), _port(), PortFailed, _read_failing() (+9 more)

### Community 49 - "Run"
Cohesion: 0.09
Nodes (20): build_prompt(), _latest_requirements(), persist_architecture(), render_markdown(), run_architect(), build_prompt(), format_issues(), persist_screenpack() (+12 more)

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

### Community 62 - "test_budget_additive.py"
Cohesion: 0.17
Nodes (16): with_node(), run_with_budget(), test_charges_of_a_failed_attempt_stay_in_paid_usd(), architect(), test_parallel_branches_both_count(), test_resume_with_a_higher_budget_progresses(), values(), wait_steps() (+8 more)

### Community 64 - "settings.py"
Cohesion: 0.07
Nodes (28): env_file_path(), BudgetPatch, BudgetSettings, _client(), current(), GatewayPatch, GatewaySettings, GatewayTest (+20 more)

### Community 67 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 68 - "media/video.py"
Cohesion: 0.14
Nodes (16): Task 16: MP4 recorder and Deck and video page  [after: 8, 14, 15], Chapter, _deck_slides(), fake_record(), _ffmpeg(), _finish(), probe(), record() (+8 more)

### Community 69 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "RunState"
Cohesion: 0.09
Nodes (22): Task 6: Run engine, events, SSE, gates  [after: 4, 5], _build_info(), _deck_html(), gather(), _load(), _readme(), run_qa(), _scan() (+14 more)

### Community 71 - "ref_node_path"
Cohesion: 0.08
Nodes (14): SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, @playwright/test@^1.65.1 (+6 more)

### Community 72 - "run_eval.py"
Cohesion: 0.10
Nodes (25): _clear_caches(), client_name_from(), configure_env(), feature_found(), _finish_full(), _fmt_time(), _isolated(), LiveRefused (+17 more)

### Community 73 - "_make_binary_fixtures.py"
Cohesion: 0.24
Nodes (3): _esc(), make_docx(), make_pdf()

### Community 74 - "build.py"
Cohesion: 0.13
Nodes (8): Request changes, retry and budget, after_gate1(), after_gate2(), after_qa(), build_graph(), state(), test_default_app_has_no_stub_nodes(), test_send_back_cap_is_at_most_two()

### Community 75 - "PoC Studio: design spec"
Cohesion: 0.12
Nodes (16): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+8 more)

### Community 76 - "tests/conftest.py"
Cohesion: 0.18
Nodes (8): BuildResult, StepResult, _no_real_npm(), fake_build(), fake_install(), _no_real_recorder(), failing_build(), build()

### Community 79 - "seed_run"
Cohesion: 0.16
Nodes (17): build_share_zip(), render_pdf(), ShareBlocked, _zip(), external_refs(), run_dir(), _names(), test_export_is_recorded_once_per_path() (+9 more)

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

### Community 85 - "Run"
Cohesion: 0.07
Nodes (31): run_migrations_offline(), run_migrations_online(), apply_owner_input(), build_prompt(), _client_name(), format_ts(), load_transcript(), next_requirements_version() (+23 more)

### Community 86 - "Business Requirements Document: Patient Intake and Prior Authorisation Assistant"
Cohesion: 0.17
Nodes (11): 10. Risks, 1. Context, 2. Current pain points, 3. Objectives, 4. Must-have capabilities, 5. Should-have capabilities, 6. Compliance and security, 7. Budget and timeline (+3 more)

### Community 87 - "Wv"
Cohesion: 0.09
Nodes (48): Ai(), Ax(), Az(), Bv(), De(), ep(), eT(), Ft() (+40 more)

### Community 88 - "json"
Cohesion: 0.11
Nodes (13): mask_for_run(), _options_path(), run_masks_pii(), write_run_options(), ExampleScreen, Kit, load_kit(), _plan_for() (+5 more)

### Community 89 - "dependencies"
Cohesion: 0.14
Nodes (14): dependencies, @fontsource-variable/geist@^5.3.0, @fontsource-variable/geist-mono@^5.3.0, lucide-react@^1.77.0, mermaid@^12.3.0, next@16.4.6, react@19.3.0, react-dom@19.3.0 (+6 more)

### Community 90 - "env"
Cohesion: 0.17
Nodes (4): _clear_caches(), client_for(), make(), env()

### Community 92 - "Recorder"
Cohesion: 0.12
Nodes (28): set_provider(), _full_run(), Recorder, _run_to_screens(), test_mock_screens_follow_the_chosen_sector_kit(), test_repair_prompt_names_the_issue_codes(), _fail_builds(), _paid() (+20 more)

### Community 93 - "share-api.ts"
Cohesion: 0.07
Nodes (36): SettingsPage(), SharePage(), KeyStatus(), buildPatch(), Draft, SettingsForm(), save(), toDraft() (+28 more)

### Community 94 - "db/models.py"
Cohesion: 0.05
Nodes (23): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), _a(), get_session(), latest_qa_report() (+15 more)

### Community 95 - "complete_json"
Cohesion: 0.26
Nodes (11): RunBudget, complete_json(), Answer, test_free_model_ignores_budget(), test_over_budget_raises_before_any_call(), test_fast_model_live(), test_mask_applied_to_user_text(), test_wrap_untrusted_neutralises_wrapper_tags() (+3 more)

### Community 96 - "bT"
Cohesion: 0.22
Nodes (11): cp(), cV(), dc(), dT(), fc(), ip(), mT(), pu() (+3 more)

### Community 99 - "Sector templates"
Cohesion: 0.40
Nodes (4): How the builder uses a kit, Sector templates, Starters, Tests

### Community 100 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 111 - "test_degrade.py"
Cohesion: 0.32
Nodes (8): collect_nodes(), _drive(), _empty(), _errors(), _step(), test_pitch_with_invalid_plans_after_repairs_fails_and_the_run_reaches_gate2(), test_real_run_with_missing_inputs_fails_the_steps_but_reaches_gate2(), test_stub_graphs_still_skip_silently()

### Community 112 - "wait_status"
Cohesion: 0.10
Nodes (38): Approval, Event, run_id(), agents(), create_run(), wait_status(), test_budget_exceeded_pauses_then_resumes(), parse_sse() (+30 more)

### Community 113 - "GitHubClient"
Cohesion: 0.36
Nodes (4): GitHubClient, RepoInfo, _create_repo(), _open_issues()

### Community 114 - "W"
Cohesion: 0.06
Nodes (54): aS(), bp(), ch(), ci(), cM(), Cn(), cS(), dh() (+46 more)

### Community 115 - "deck.py"
Cohesion: 0.12
Nodes (9): _add_slide(), build_pptx(), _figure_value(), _rgb(), _text(), _Camel, PlayScreen, Slide (+1 more)

### Community 116 - "gate2-view.tsx"
Cohesion: 0.08
Nodes (50): ConfirmPublish(), Props, DeliveredView(), InAppItem(), ItemProps, summary(), Gate2View(), Qa (+42 more)

### Community 117 - "test_assemble_node.py"
Cohesion: 0.17
Nodes (12): plan_holds(), _deck_files(), test_assembled_deck_runs_every_step(), test_graph_run_assembles_a_self_contained_deck(), browser_name_and_browser(), deck_html(), icons_css(), pack() (+4 more)

### Community 118 - "_latest_file"
Cohesion: 0.14
Nodes (13): download_markdown_artifact(), FileNode, get_build(), get_deck_html(), get_deck_pptx(), get_doc(), get_file_tree(), get_json_artifact() (+5 more)

### Community 119 - "test_publish.py"
Cohesion: 0.11
Nodes (21): _check_clean(), publish(), PublishBlocked, PublishFailed, PublishOptions, PublishResult, push(), _artifact_json() (+13 more)

### Community 120 - "test_port.py"
Cohesion: 0.17
Nodes (9): _drive(), FakeBuild, FakePreviews, _port_step(), test_a_port_run_stops_that_runs_preview_first(), test_fail_then_pass_costs_one_model_call(), test_fixture_is_a_port_fix(), test_reset_stops_the_preview_and_deletes_a_stale_build_json() (+1 more)

### Community 121 - "PoC Studio build plan"
Cohesion: 0.33
Nodes (5): File map, Global constraints, Owner-only steps, Parked (NEXT_STEPS.md), PoC Studio build plan

### Community 122 - "test_intelligence.py"
Cohesion: 0.32
Nodes (10): _artifacts(), _brief(), _create(), test_client_and_sector_follow_the_owners_input(), test_extracted_sector_is_kept_when_the_owner_picked_none(), test_gate1_changes_makes_v2_with_note(), test_mock_output_validates(), test_node_writes_artifact_and_step() (+2 more)

### Community 123 - "tokens.py"
Cohesion: 0.26
Nodes (6): new_run_id(), ShareToken, create_token(), hash_token(), resolve_token(), _utcnow()

### Community 126 - "build.mjs"
Cohesion: 0.27
Nodes (7): SAMPLE, status(), waitFor(), build(), here, orderScripts(), read()

### Community 127 - "test_pii.py"
Cohesion: 0.24
Nodes (8): mask_pii(), Recorder, _run_with(), test_intelligence_is_unmasked_by_default(), test_intelligence_sends_a_masked_prompt_when_the_option_is_on(), test_keeps_a_stakeholders_own_address_only_when_named(), test_keeps_example_com_names_and_timestamps(), test_masks_emails_and_phones()

### Community 128 - "architecture-view.tsx"
Cohesion: 0.13
Nodes (21): ArchitecturePage(), ArchitectureView(), Load, CostTable(), MermaidDiagram(), Result, themeVariables(), token() (+13 more)

### Community 129 - "RunService"
Cohesion: 0.07
Nodes (22): lifespan(), BudgetRequest, _fail(), _port_failed(), raise_budget(), retry_run(), RetryRequest, revise_artifact() (+14 more)

### Community 130 - "schemas.py"
Cohesion: 0.13
Nodes (21): AgentStepOut, ArtifactJson, ArtifactOut, BudgetRaiseRequest, CreateRunOptions, CreateRunResponse, EventError, GateDecisionRequest (+13 more)

### Community 132 - "runner.py"
Cohesion: 0.13
Nodes (15): strip_ansi(), kill_pid_tree(), build(), child_env(), _command(), container_name(), _docker_kill(), install() (+7 more)

### Community 133 - "TestClient"
Cohesion: 0.28
Nodes (10): test_a_bad_host_is_400(), test_a_post_without_origin_passes(), test_gets_are_never_blocked(), test_json_post_from_a_foreign_origin_is_403(), test_json_post_from_the_app_origin_passes(), test_local_hosts_are_allowed(), test_multipart_run_creation_from_the_app_origin_passes(), test_put_and_delete_are_guarded_too() (+2 more)

### Community 134 - "architecture.py"
Cohesion: 0.25
Nodes (5): Component, CostLine, ModelPick, MonthlyCost, Phase

### Community 136 - "test_full_run.py"
Cohesion: 0.28
Nodes (9): _agents(), _artifacts(), _assert_order(), _drive(), _reports(), test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(), test_full_run_through_both_gates_to_delivered(), test_planted_secret_sends_back_port_only_and_blocks_publish() (+1 more)

### Community 138 - "eo"
Cohesion: 0.08
Nodes (32): $d(), eo(), ey(), Fh(), Fv(), hc(), hE(), hp() (+24 more)

### Community 139 - "parse_file"
Cohesion: 0.27
Nodes (12): parse_file(), test_fixture_exists_and_parses(), _close(), test_docx_includes_table_cells(), test_file_over_20mb_raises(), test_md_paragraphs(), test_parse_files_merges_in_order(), test_pdf_extracts_text() (+4 more)

### Community 142 - "page.py"
Cohesion: 0.21
Nodes (4): ShareContent, render_index(), _tokens(), write_pdf()

### Community 143 - "test_artifacts_files.py"
Cohesion: 0.27
Nodes (8): names(), test_build_returns_build_json(), test_file_tree_depth_is_capped_at_six(), test_file_tree_skips_node_modules_next_and_dotfiles(), test_files_and_build_404_for_unknown_run_and_no_app(), test_preview_409_until_built_then_redirects_to_the_direct_url(), test_traversal_is_impossible_there_is_no_path_input(), write()

### Community 144 - "app.js"
Cohesion: 0.22
Nodes (8): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T

### Community 145 - "test_jsx.py"
Cohesion: 0.07
Nodes (20): node_access_problem(), apply_fix(), FixFile, PortFix, safe_path(), UnsafePath, _attr_value(), _Converter (+12 more)

### Community 146 - "complete_json"
Cohesion: 0.12
Nodes (12): LLM pricing, BudgetExceeded, count_tokens(), InputTooLarge, cost_usd(), is_claude(), prices(), architect() (+4 more)

### Community 148 - "Settings"
Cohesion: 0.13
Nodes (10): Settings, GatewayProvider, _call(), test_explicit_timeout_wins(), test_gateway_sdk_does_not_retry(), test_setting_defaults_to_300_and_reads_env(), test_timeout_defaults_to_settings(), TimeoutRecorder (+2 more)

### Community 149 - "el"
Cohesion: 0.40
Nodes (8): build(), buildClose(), buildPlay(), buildWelcome(), el(), header(), spot(), txt()

### Community 150 - "test_drift.py"
Cohesion: 0.19
Nodes (7): _codes(), _product_css(), _screen_html(), change(), _script(), test_style_is_forbidden_by_the_validator_only(), test_the_baseline_is_clean_on_both_sides()

### Community 151 - "Settings"
Cohesion: 0.14
Nodes (15): get_github(), GitHubError, GitHubNotConfigured, RepoNameTaken, _client(), wrapped(), test_create_issue_and_repo_exists(), handler() (+7 more)

### Community 152 - "test_tokens.py"
Cohesion: 0.19
Nodes (11): _fixture(), seed_run(), _build(), test_stats_come_from_the_runs(), test_expired_token_is_404_on_a_fake_clock(), test_public_json(), test_run_must_be_delivered_or_at_gate2_with_a_deck(), test_share_export_route_and_download() (+3 more)

### Community 154 - "web/app/layout.tsx"
Cohesion: 0.28
Nodes (6): metadata, RootLayout(), AppToaster(), TOAST_OPTIONS, sileo@^0.1.6, sileo

### Community 155 - "Decisions"
Cohesion: 0.33
Nodes (5): Decisions, GitHub publish, Resolved values, Task 1 notes, Verified prices

### Community 157 - "test_env.py"
Cohesion: 0.38
Nodes (9): _python(), test_child_env_has_no_secrets_and_keeps_path(), test_child_env_points_home_dirs_at_the_run_folder(), test_docker_is_never_used_unless_asked(), test_install_skips_lifecycle_scripts(), test_output_is_redacted(), test_secrets_do_not_reach_the_process(), test_the_child_sees_the_per_run_home() (+1 more)

### Community 158 - "dev.mjs"
Cohesion: 0.16
Nodes (10): @vitejs/plugin-react@^6.3.0, @vitejs/plugin-react, children, kill(), root, shutdown(), start(), api (+2 more)

### Community 159 - "mountScreen"
Cohesion: 0.40
Nodes (4): 7a. Deck and prototype output contract (amendment 8), show(), mountScreen(), toast()

### Community 161 - "poc_studio/events.py"
Cohesion: 0.11
Nodes (8): event_name(), EventBus, Subscription, to_event(), event_stream(), _sse(), stream_events(), RunEvent

### Community 163 - "_fixture"
Cohesion: 0.36
Nodes (6): _fixture(), test_graph_run_writes_architecture(), test_markdown_download_rejects_other_types(), test_mermaid_must_be_a_diagram(), test_mock_output_validates(), test_total_must_match_lines()

### Community 165 - "healthcare kit: selector and anchor guide"
Cohesion: 0.40
Nodes (4): Anchors, Example screens, healthcare kit: selector and anchor guide, Scoping

### Community 166 - "requirements.py"
Cohesion: 0.39
Nodes (5): ActionItem, Budget, Constraint, Feature, Stakeholder

### Community 168 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, gen:types, lint, start, test (+1 more)

### Community 169 - "FileTooLarge"
Cohesion: 0.33
Nodes (3): Task 5: Ingest parsers and eval fixtures  [after: 1, parallel with 4], FileTooLarge, UnsupportedFile

### Community 176 - "_drive"
Cohesion: 0.32
Nodes (7): _drive(), _reports(), _steps(), test_missing_deck_fails_deck_present_and_the_run_still_reaches_gate2(), test_mock_run_reaches_gate2_with_a_passing_qa_report(), test_planted_secret_sends_port_back_twice_then_blocks_publish(), test_real_run_without_a_deck_is_flagged_even_without_a_failure_marker()

### Community 186 - "main.py"
Cohesion: 0.11
Nodes (5): _forbidden(), UnsafeRequestGuard, create_app(), set_preview_manager(), health()

### Community 187 - "test_gate2.py"
Cohesion: 0.47
Nodes (7): _approvals(), test_approve_stores_the_options_and_delivers(), test_block_publish_returns_409_and_leaves_the_gate_open(), test_invalid_options_return_422(), test_missing_options_default_to_a_private_repo_named_from_the_client(), test_publish_status_is_pending_before_gate_2_and_404_for_unknown(), _to_gate2()

### Community 190 - "manager.py"
Cohesion: 0.15
Nodes (6): Entry, http_ready(), launch_next(), port_is_free(), looks_like_preview_image(), pid_alive()

### Community 191 - "_ensure"
Cohesion: 0.18
Nodes (5): PreviewError, _ensure(), PreviewInfo, redirect_preview(), start_preview()

### Community 199 - "now"
Cohesion: 0.20
Nodes (8): now(), include_extra(), on_startup(), apply_retention(), test_default_is_off_and_startup_deletes_nothing(), test_old_inputs_are_deleted_and_artifacts_kept(), test_zero_days_turns_it_off(), _with_input()

## Knowledge Gaps
- **1 isolated node(s):** `poc-studio-api`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1167 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `up()` connect `bT` to `toast.js`, `i`, `A`, `app.js`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **What connects `poc-studio-api` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013941543353308059 - nodes in this community are weakly interconnected._
- **Why does `Request changes, retry and budget` connect `build.py` to `RunService`, `Decisions`, `run-context.tsx`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.06256384065372829 - nodes in this community are weakly interconnected._
- **Why does `RunBudgetBanner()` connect `run-context.tsx` to `build.py`, `runs-view.tsx`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Should `web/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.08522727272727272 - nodes in this community are weakly interconnected._