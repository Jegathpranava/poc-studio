# Graph Report - poc-studio  (2026-11-23)

## Corpus Check
- 404 files · ~175,073 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .css 34, (none) 11, .vtt 5)

## Summary
- 3934 nodes · 11151 edges · 185 communities (140 shown, 45 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 927 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcd71b47`
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
- api.ts
- steps
- brief-view.tsx
- runner.py
- complete_json
- poc_studio/llm/__init__.py
- open_session
- validate.py
- PreviewManager
- A
- new-run-form.tsx
- app.js
- ScreenPack
- config.py
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
- secrets.py
- timeline-view.tsx
- run-context.tsx
- re
- parse.py
- share.py
- package.json
- secrets.py
- fintech/app/package.json
- Answer
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
- open_session
- poc-studio-api
- settings.py
- compilerOptions
- media/video.py
- compilerOptions
- templates.py
- ref_node_path
- run_eval.py
- _make_binary_fixtures.py
- typing
- PoC Studio: design spec
- tests/conftest.py
- seed_run
- A
- Technical Requirements Document: Returns and Substitution Assistant
- Technical Requirements Document: Last-Mile Route Re-Optimiser
- Business Requirements Document: Dock Scheduling Assistant
- sd
- intelligence.py
- Business Requirements Document: Patient Intake and Prior Authorisation Assistant
- Wv
- MockGitHub
- dependencies
- env
- test_screens.py
- share-api.ts
- Project
- test_json.py
- bT
- sample.md
- Sector templates
- web/README.md
- AGENTS.md
- routes/revise.py
- client
- GitHubClient
- W
- deck.py
- gate2-view.tsx
- _Converter
- _latest_file
- test_publish.py
- FakeProvider
- Decisions
- decide
- tokens.py
- build.mjs
- manager.py
- architecture-view.tsx
- RunService
- schemas.py
- routes/publish.py
- TestClient
- get_settings
- test_full_run.py
- deck_runtime/README.md
- eo
- poc_studio/events.py
- preview.py
- Segment
- app.js
- test_jsx.py
- complete_json
- test_qa_node.py
- Settings
- el
- test_drift.py
- Settings
- test_tokens.py
- web/app/layout.tsx
- parse_file
- test_schemas.py
- test_degrade.py
- dev.mjs
- mountScreen
- sqlalchemy
- datetime
- test_pii.py
- LiveGitHub
- healthcare kit: selector and anchor guide
- post
- scripts
- test_gate2.py
- runs.py
- Eval
- build_fixture.py
- PoC Studio build plan
- FileTooLarge
- decide_gate
- port.py
- guard.py
- collections_abc
- get_settings

## God Nodes (most connected - your core abstractions)
1. `open_session()` - 135 edges
2. `get_settings()` - 113 edges
3. `wait_status()` - 90 edges
4. `client()` - 87 edges
5. `ScreenPack` - 82 edges
6. `create_run()` - 81 edges
7. `DeckPlan` - 74 edges
8. `Artifact` - 68 edges
9. `Run` - 67 edges
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
- `Task 4: LLM client, mock provider, budget guard  [after: 1]` --references--> `SchemaError`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/llm/client.py

## Import Cycles
- None detected.

## Communities (185 total, 45 thin omitted)

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
Cohesion: 0.07
Nodes (40): apply_patch(), build_prompt(), check_plan(), figure_problem(), _pick(), polish_input(), Polished, PolishedSlide (+32 more)

### Community 4 - "ref_react"
Cohesion: 0.06
Nodes (18): AppLayout(), metadata, ShareLayout(), AppShell(), Brand(), BudgetMeter(), NAV_ITEMS, NavItem (+10 more)

### Community 5 - "Tasks"
Cohesion: 0.08
Nodes (25): Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues), Increment 7: hardening (visible: request changes, budget pause, share zip), Task 10: Sector kits and starters  [after: 1, parallel with 4-9] (+17 more)

### Community 6 - "runs-view.tsx"
Cohesion: 0.10
Nodes (29): RunsPage(), durationMs(), formatDuration(), formatUsd(), formatWhen(), matchesFilter(), matchesQuery(), PLACEHOLDER (+21 more)

### Community 7 - "_t"
Cohesion: 0.11
Nodes (20): ao(), CO(), Da(), Dv(), dx(), e3(), f1(), hx() (+12 more)

### Community 8 - "test_manager.py"
Cohesion: 0.22
Nodes (16): PreviewError, Fake, make_runs(), record_previews(), recorded(), test_a_process_that_died_after_the_http_check_is_not_served(), test_concurrent_ensure_gets_distinct_ports(), test_dead_server_is_restarted() (+8 more)

### Community 9 - "ChatReply"
Cohesion: 0.11
Nodes (5): ChatReply, MockProvider, _reskin_screens(), Recorder, Recorder

### Community 10 - "api.ts"
Cohesion: 0.12
Nodes (24): DeckPage(), Page(), TemplatesPage(), DeckPanel(), DeckView(), DocsPanel(), ErrorBanner(), formatTime() (+16 more)

### Community 11 - "steps"
Cohesion: 0.08
Nodes (25): runs-on, steps, timeout-minutes, env, APP_ENV, GITHUB_MODE, LLM_PROVIDER, jobs (+17 more)

### Community 12 - "brief-view.tsx"
Cohesion: 0.13
Nodes (30): BriefPage(), BriefFeatures(), PRIORITIES, Props, BriefGoalsPanel(), Props, BriefSide(), Props (+22 more)

### Community 13 - "runner.py"
Cohesion: 0.05
Nodes (49): _clean(), excerpt_from_file(), _next_block(), parse_build_error(), strip_ansi(), kill_pid_tree(), build(), BuildResult (+41 more)

### Community 14 - "complete_json"
Cohesion: 0.16
Nodes (10): RunBudget, _broken_json(), complete_json(), repair_prompt(), strip_fences(), test_free_model_ignores_budget(), test_over_budget_raises_before_any_call(), NoUsageProvider (+2 more)

### Community 15 - "poc_studio/llm/__init__.py"
Cohesion: 0.20
Nodes (6): Task 4: LLM client, mock provider, budget guard  [after: 1], _resolve(), Result, SchemaError, ChatProvider, get_provider()

### Community 16 - "open_session"
Cohesion: 0.09
Nodes (30): AgentStep, Artifact, open_session(), load_events(), load_latest_requirements(), test_graph_run_writes_architecture(), _artifacts(), _brief() (+22 more)

### Community 17 - "validate.py"
Cohesion: 0.12
Nodes (20): add(), DeckPlanInvalid, ScreenPackInvalid, url_problem(), Anchor, Screen, _anchor_issues(), _css_url_issues() (+12 more)

### Community 18 - "PreviewManager"
Cohesion: 0.16
Nodes (3): lifespan(), PreviewManager, loop()

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
Cohesion: 0.11
Nodes (40): assemble(), _check_css(), _check_html(), fail(), _check_script(), DeckNotSelfContained, _json_for_script(), _read() (+32 more)

### Community 23 - "config.py"
Cohesion: 0.08
Nodes (22): run_assemble(), _run_assemble(), _write_outputs(), _build_info(), _deck_html(), gather(), _load(), _readme() (+14 more)

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.18
Nodes (10): 7 agents, Commands, Core tech stack (budget build, decided at intake), graphify, Human approval gates, Knowledge graph (graphify), Mission, PoC Studio — Developer Guidelines & Architecture Rules (+2 more)

### Community 25 - "test_settings.py"
Cohesion: 0.16
Nodes (9): env_file_path(), _gateway_mode(), secrets_set(), test_key_not_set_reads_false(), test_put_never_writes_env(), test_put_updates_the_budget_and_persists(), test_test_gateway_failure_is_reported_without_the_key(), test_test_gateway_in_mock_mode_makes_no_network_call() (+1 more)

### Community 26 - "github/publish.py"
Cohesion: 0.12
Nodes (18): _check_clean(), _copy(), _file_count(), _git(), git_auth_header(), _git_env(), _latest_path(), NothingToPublish (+10 more)

### Community 27 - "checks.py"
Cohesion: 0.12
Nodes (39): build_passed(), Check, costs_consistent(), _css_problems(), deck_present(), deck_self_contained(), _deck_text(), _fail() (+31 more)

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
Cohesion: 0.20
Nodes (9): _files(), scan_pii(), scan_tree(), temp_env(), test_env_file_is_read_at_call_time(), test_env_value_is_matched_by_hash(), test_example_com_and_stakeholder_emails_are_allowed_but_real_looking_ones_are_not(), test_scan_tree_excludes_node_modules_and_home() (+1 more)

### Community 35 - "timeline-view.tsx"
Cohesion: 0.07
Nodes (56): RunTimelinePage(), CostByModel(), COPY, GateRow(), NextForYou(), CLASS, elapsed(), PipelineStep() (+48 more)

### Community 36 - "run-context.tsx"
Cohesion: 0.08
Nodes (35): RunLayout(), Props, BannerProps, BudgetBanner(), RunBudgetBanner(), RequestChanges(), RequestChangesProps, ReviseButton() (+27 more)

### Community 37 - "re"
Cohesion: 0.24
Nodes (14): test_no_external_src_or_href(), _defined_classes(), _fragment(), _kit(), _strip_comments(), _strip_urls(), test_anchors(), test_app_kit_copies_match() (+6 more)

### Community 38 - "parse.py"
Cohesion: 0.24
Nodes (12): _line_segment(), _paragraph_segments(), _parse_docx(), _parse_pdf(), _parse_plain(), _parse_txt(), _parse_vtt_file(), _read_text() (+4 more)

### Community 39 - "share.py"
Cohesion: 0.17
Nodes (14): create_share_token(), download_share_zip(), export_share(), get_share_deck(), get_share_page(), get_share_video(), _manifest_warnings(), _shareable_run() (+6 more)

### Community 40 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, dev, lint, test, typecheck, version (+1 more)

### Community 41 - "secrets.py"
Cohesion: 0.16
Nodes (11): _assignment_is_secret(), env_hashes(), _hashes_of(), _kind(), _line_at(), add(), scan_text(), add() (+3 more)

### Community 42 - "fintech/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 43 - "Answer"
Cohesion: 0.20
Nodes (10): GatewayProvider, Answer, test_fast_model_live(), test_mask_applied_to_user_text(), test_wrap_untrusted_neutralises_wrapper_tags(), _call(), test_explicit_timeout_wins(), test_gateway_sdk_does_not_retry() (+2 more)

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
Cohesion: 0.16
Nodes (5): _drive(), FakeBuild, FakePreviews, test_a_port_run_stops_that_runs_preview_first(), test_reset_stops_the_preview_and_deletes_a_stale_build_json()

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

### Community 62 - "open_session"
Cohesion: 0.13
Nodes (20): Task 6: Run engine, events, SSE, gates  [after: 4, 5], options_from_state(), run_repo(), Run, add_paid(), node_budget(), _finish(), step_scope() (+12 more)

### Community 64 - "settings.py"
Cohesion: 0.12
Nodes (19): BudgetPatch, BudgetSettings, _client(), current(), GatewayPatch, GatewaySettings, GatewayTest, get_current_settings() (+11 more)

### Community 67 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 68 - "media/video.py"
Cohesion: 0.10
Nodes (25): Task 16: MP4 recorder and Deck and video page  [after: 8, 14, 15], Chapter, _deck_slides(), fake_record(), _ffmpeg(), _finish(), plan_holds(), probe() (+17 more)

### Community 69 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "templates.py"
Cohesion: 0.16
Nodes (6): _factory(), get_session(), _first_time_ok(), _kits(), list_templates(), TemplateStat

### Community 71 - "ref_node_path"
Cohesion: 0.08
Nodes (14): SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, @playwright/test@^1.65.1 (+6 more)

### Community 72 - "run_eval.py"
Cohesion: 0.11
Nodes (25): _clear_caches(), client_name_from(), configure_env(), feature_found(), _finish_full(), _fmt_time(), _isolated(), LiveRefused (+17 more)

### Community 73 - "_make_binary_fixtures.py"
Cohesion: 0.24
Nodes (3): _esc(), make_docx(), make_pdf()

### Community 74 - "typing"
Cohesion: 0.08
Nodes (15): after_gate1(), after_gate2(), after_qa(), build_graph(), builtin_nodes(), _gate_node(), gate_node(), intake() (+7 more)

### Community 75 - "PoC Studio: design spec"
Cohesion: 0.12
Nodes (16): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+8 more)

### Community 76 - "tests/conftest.py"
Cohesion: 0.28
Nodes (4): _no_real_npm(), fake_build(), fake_install(), _no_real_recorder()

### Community 79 - "seed_run"
Cohesion: 0.09
Nodes (23): ShareContent, build_share_zip(), _record(), render_pdf(), share_dir(), ShareBlocked, ShareUnavailable, _zip() (+15 more)

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
Nodes (24): apply_owner_input(), build_prompt(), _client_name(), format_ts(), load_transcript(), next_requirements_version(), _norm(), _project_input() (+16 more)

### Community 86 - "Business Requirements Document: Patient Intake and Prior Authorisation Assistant"
Cohesion: 0.17
Nodes (11): 10. Risks, 1. Context, 2. Current pain points, 3. Objectives, 4. Must-have capabilities, 5. Should-have capabilities, 6. Compliance and security, 7. Budget and timeline (+3 more)

### Community 87 - "Wv"
Cohesion: 0.09
Nodes (48): Ai(), Ax(), Az(), Bv(), De(), ep(), eT(), Ft() (+40 more)

### Community 89 - "dependencies"
Cohesion: 0.14
Nodes (14): dependencies, @fontsource-variable/geist@^5.3.0, @fontsource-variable/geist-mono@^5.3.0, lucide-react@^1.77.0, mermaid@^12.3.0, next@16.4.6, react@19.3.0, react-dom@19.3.0 (+6 more)

### Community 90 - "env"
Cohesion: 0.15
Nodes (4): _clear_caches(), client_for(), make(), env()

### Community 92 - "test_screens.py"
Cohesion: 0.12
Nodes (29): set_provider(), _plan_for(), Recorder, _run_to_screens(), test_graph_run_repairs_and_stores_screenpack(), test_mock_screens_follow_the_chosen_sector_kit(), test_pack_still_invalid_after_two_repairs_fails_the_step(), test_repair_prompt_names_the_issue_codes() (+21 more)

### Community 93 - "share-api.ts"
Cohesion: 0.07
Nodes (36): SettingsPage(), SharePage(), KeyStatus(), buildPatch(), Draft, SettingsForm(), save(), toDraft() (+28 more)

### Community 94 - "Project"
Cohesion: 0.15
Nodes (9): run_migrations_offline(), run_migrations_online(), Base, Project, get_engine(), main(), _run(), _create_tables() (+1 more)

### Community 95 - "test_json.py"
Cohesion: 0.31
Nodes (9): _call(), _run(), test_fenced_reply_parses(), test_mock_provider_fixture(), test_repair_on_second_attempt(), test_schema_error_repair_quotes_the_validation_error(), test_schema_in_system_prompt(), test_three_invalid_raise() (+1 more)

### Community 96 - "bT"
Cohesion: 0.22
Nodes (11): cp(), cV(), dc(), dT(), fc(), ip(), mT(), pu() (+3 more)

### Community 99 - "Sector templates"
Cohesion: 0.40
Nodes (4): How the builder uses a kit, Sector templates, Starters, Tests

### Community 100 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 111 - "routes/revise.py"
Cohesion: 0.23
Nodes (11): BudgetRequest, _fail(), _port_failed(), raise_budget(), retry_run(), RetryRequest, revise_artifact(), ReviseRequest (+3 more)

### Community 112 - "client"
Cohesion: 0.06
Nodes (62): record(), test_markdown_download_rejects_other_types(), test_gate1_changes_makes_v2_with_note(), test_unsupported_constraint_unconfirmed(), _run(), run_id(), agents(), create_run() (+54 more)

### Community 113 - "GitHubClient"
Cohesion: 0.36
Nodes (4): GitHubClient, RepoInfo, _create_repo(), _open_issues()

### Community 114 - "W"
Cohesion: 0.06
Nodes (54): aS(), bp(), ch(), ci(), cM(), Cn(), cS(), dh() (+46 more)

### Community 115 - "deck.py"
Cohesion: 0.10
Nodes (10): _add_slide(), build_pptx(), _figure_value(), _rgb(), _text(), _Camel, Figure, PlayScreen (+2 more)

### Community 116 - "gate2-view.tsx"
Cohesion: 0.08
Nodes (50): ConfirmPublish(), Props, DeliveredView(), InAppItem(), ItemProps, summary(), Gate2View(), Qa (+42 more)

### Community 117 - "_Converter"
Cohesion: 0.16
Nodes (4): _attr_value(), _Converter, jsx_attr_name(), _text()

### Community 118 - "_latest_file"
Cohesion: 0.14
Nodes (13): download_markdown_artifact(), FileNode, get_build(), get_deck_html(), get_deck_pptx(), get_doc(), get_file_tree(), get_json_artifact() (+5 more)

### Community 119 - "test_publish.py"
Cohesion: 0.16
Nodes (15): default_repo_name(), publish(), PublishBlocked, PublishOptions, _artifact_json(), _git(), _qa_report(), test_block_publish_in_the_qa_report_blocks() (+7 more)

### Community 120 - "FakeProvider"
Cohesion: 0.27
Nodes (10): FakeProvider, _call(), EmptyThenOk, test_caller_note_replaces_the_default(), test_empty_answer_retries_fresh_and_passes_reasoning_effort(), test_only_empty_answers_raise_a_clear_error(), test_other_broken_json_gets_a_short_note(), test_retries_do_not_grow_after_repeated_truncation() (+2 more)

### Community 121 - "Decisions"
Cohesion: 0.29
Nodes (6): Decisions, GitHub publish, Request changes, retry and budget, Resolved values, Task 1 notes, Verified prices

### Community 122 - "decide"
Cohesion: 0.31
Nodes (14): decide(), Decision, bad(), ok(), test_after_two_send_backs_none_are_made_but_secrets_still_block(), test_all_passing_sends_nothing_back(), test_assemble_and_video_owners_are_never_sent_back(), test_build_failure_is_report_only() (+6 more)

### Community 123 - "tokens.py"
Cohesion: 0.29
Nodes (5): new_run_id(), create_token(), hash_token(), resolve_token(), _utcnow()

### Community 126 - "build.mjs"
Cohesion: 0.27
Nodes (7): SAMPLE, status(), waitFor(), build(), here, orderScripts(), read()

### Community 127 - "manager.py"
Cohesion: 0.11
Nodes (8): Entry, http_ready(), launch_next(), port_is_free(), looks_like_preview_image(), pid_alive(), process_image(), test_build_serve_get_stop()

### Community 128 - "architecture-view.tsx"
Cohesion: 0.13
Nodes (21): ArchitecturePage(), ArchitectureView(), Load, CostTable(), MermaidDiagram(), Result, themeVariables(), token() (+13 more)

### Community 130 - "schemas.py"
Cohesion: 0.14
Nodes (15): health(), ArtifactJson, BudgetRaiseRequest, CreateRunOptions, CreateRunResponse, EventError, HealthResponse, PublishOptionsRequest (+7 more)

### Community 132 - "routes/publish.py"
Cohesion: 0.23
Nodes (7): latest_qa_report(), PublishResult, _approved_options(), _failure(), get_publish(), PublishStatus, _result()

### Community 133 - "TestClient"
Cohesion: 0.28
Nodes (10): test_a_bad_host_is_400(), test_a_post_without_origin_passes(), test_gets_are_never_blocked(), test_json_post_from_a_foreign_origin_is_403(), test_json_post_from_the_app_origin_passes(), test_local_hosts_are_allowed(), test_multipart_run_creation_from_the_app_origin_passes(), test_put_and_delete_are_guarded_too() (+2 more)

### Community 134 - "get_settings"
Cohesion: 0.08
Nodes (29): build_prompt(), _latest_requirements(), persist_architecture(), render_markdown(), run_architect(), _added_css(), build_prompt(), format_issues() (+21 more)

### Community 136 - "test_full_run.py"
Cohesion: 0.28
Nodes (10): _agents(), _artifacts(), _assert_order(), _drive(), _reports(), test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(), failing_build(), test_full_run_through_both_gates_to_delivered() (+2 more)

### Community 138 - "eo"
Cohesion: 0.08
Nodes (32): $d(), eo(), ey(), Fh(), Fv(), hc(), hE(), hp() (+24 more)

### Community 139 - "poc_studio/events.py"
Cohesion: 0.10
Nodes (10): Event, event_name(), EventBus, Subscription, to_event(), event_stream(), _sse(), stream_events() (+2 more)

### Community 142 - "preview.py"
Cohesion: 0.27
Nodes (4): _ensure(), PreviewInfo, redirect_preview(), start_preview()

### Community 143 - "Segment"
Cohesion: 0.42
Nodes (3): Segment, Transcript, parse_files()

### Community 144 - "app.js"
Cohesion: 0.22
Nodes (8): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T

### Community 145 - "test_jsx.py"
Cohesion: 0.10
Nodes (17): _read_failing(), node_access_problem(), apply_fix(), FixFile, PortFix, safe_path(), UnsafePath, page_source() (+9 more)

### Community 146 - "complete_json"
Cohesion: 0.16
Nodes (10): LLM pricing, count_tokens(), InputTooLarge, cost_usd(), is_claude(), prices(), test_claude_cost_nonzero(), test_claude_input_over_12k_tokens() (+2 more)

### Community 147 - "test_qa_node.py"
Cohesion: 0.26
Nodes (7): _drive(), _reports(), _steps(), test_missing_deck_fails_deck_present_and_the_run_still_reaches_gate2(), test_mock_run_reaches_gate2_with_a_passing_qa_report(), test_planted_secret_sends_port_back_twice_then_blocks_publish(), test_real_run_without_a_deck_is_flagged_even_without_a_failure_marker()

### Community 148 - "Settings"
Cohesion: 0.16
Nodes (4): Settings, test_setting_defaults_to_300_and_reads_env(), test_production_refuses_mock_github(), test_production_refuses_mock_llm()

### Community 149 - "el"
Cohesion: 0.40
Nodes (8): build(), buildClose(), buildPlay(), buildWelcome(), el(), header(), spot(), txt()

### Community 150 - "test_drift.py"
Cohesion: 0.21
Nodes (7): _codes(), _product_css(), _screen_html(), change(), _script(), test_style_is_forbidden_by_the_validator_only(), test_the_baseline_is_clean_on_both_sides()

### Community 151 - "Settings"
Cohesion: 0.13
Nodes (16): get_github(), GitHubError, GitHubNotConfigured, RepoNameTaken, get_user(), _client(), wrapped(), test_create_issue_and_repo_exists() (+8 more)

### Community 152 - "test_tokens.py"
Cohesion: 0.12
Nodes (13): ShareToken, _fake_pdf(), _fixture(), seed_run(), _build(), test_stats_come_from_the_runs(), test_expired_token_is_404_on_a_fake_clock(), test_public_json() (+5 more)

### Community 154 - "web/app/layout.tsx"
Cohesion: 0.28
Nodes (6): metadata, RootLayout(), AppToaster(), TOAST_OPTIONS, sileo@^0.1.6, sileo

### Community 155 - "parse_file"
Cohesion: 0.30
Nodes (11): parse_file(), test_fixture_exists_and_parses(), _close(), test_docx_includes_table_cells(), test_file_over_20mb_raises(), test_md_paragraphs(), test_parse_files_merges_in_order(), test_pdf_extracts_text() (+3 more)

### Community 156 - "test_schemas.py"
Cohesion: 0.39
Nodes (8): _pack(), _plan(), _screen(), _slide(), test_deckplan_valid(), test_screenpack_anchor_must_match_html(), test_screenpack_five_screens_fails(), test_screenpack_valid()

### Community 157 - "test_degrade.py"
Cohesion: 0.35
Nodes (8): AlwaysInvalidPitch, _drive(), _empty(), _errors(), _step(), test_pitch_with_invalid_plans_after_repairs_fails_and_the_run_reaches_gate2(), test_real_run_with_missing_inputs_fails_the_steps_but_reaches_gate2(), test_stub_graphs_still_skip_silently()

### Community 158 - "dev.mjs"
Cohesion: 0.16
Nodes (10): @vitejs/plugin-react@^6.3.0, @vitejs/plugin-react, children, kill(), root, shutdown(), start(), api (+2 more)

### Community 159 - "mountScreen"
Cohesion: 0.40
Nodes (4): 7a. Deck and prototype output contract (amendment 8), show(), mountScreen(), toast()

### Community 161 - "sqlalchemy"
Cohesion: 0.12
Nodes (9): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), _deck_files(), _full_run(), test_assembled_deck_runs_every_step() (+1 more)

### Community 163 - "test_pii.py"
Cohesion: 0.20
Nodes (10): mask_for_run(), mask_pii(), _options_path(), run_masks_pii(), write_run_options(), _name_forms(), test_keeps_a_stakeholders_own_address_only_when_named(), test_keeps_example_com_names_and_timestamps() (+2 more)

### Community 165 - "healthcare kit: selector and anchor guide"
Cohesion: 0.40
Nodes (4): Anchors, Example screens, healthcare kit: selector and anchor guide, Scoping

### Community 166 - "post"
Cohesion: 0.23
Nodes (7): InvalidUpload, safe_name(), post(), test_colon_names_rejected(), test_safe_name_compares_casefolded(), test_too_many_files(), test_total_size_limit()

### Community 168 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, gen:types, lint, start, test (+1 more)

### Community 169 - "test_gate2.py"
Cohesion: 0.27
Nodes (8): Approval, _approvals(), test_approve_stores_the_options_and_delivers(), test_block_publish_returns_409_and_leaves_the_gate_open(), test_invalid_options_return_422(), test_missing_options_default_to_a_private_repo_named_from_the_client(), test_publish_status_is_pending_before_gate_2_and_404_for_unknown(), _to_gate2()

### Community 171 - "runs.py"
Cohesion: 0.15
Nodes (12): create_run(), get_run(), get_service(), list_runs(), _summary_fields(), _total_message(), AgentStepOut, ArtifactOut (+4 more)

### Community 173 - "Eval"
Cohesion: 0.22
Nodes (8): Dry mode, Eval, Flags, Isolation, Live mode, Measures, Stages, Success measures (full summary)

### Community 174 - "build_fixture.py"
Cohesion: 0.38
Nodes (5): Task 11: Prototype Builder: ScreenPack  [after: 9, 10], Task 14: Vendored deck engine and assembler  [after: 1, parallel with 4-13; runs on the owner's machine, where `reference/` exists], anchors_of(), build_pack(), step_css()

### Community 182 - "PoC Studio build plan"
Cohesion: 0.33
Nodes (5): File map, Global constraints, Owner-only steps, Parked (NEXT_STEPS.md), PoC Studio build plan

### Community 183 - "FileTooLarge"
Cohesion: 0.33
Nodes (3): Task 5: Ingest parsers and eval fixtures  [after: 1, parallel with 4], FileTooLarge, UnsupportedFile

### Community 184 - "decide_gate"
Cohesion: 0.29
Nodes (5): decide_gate(), _publish_options(), GateDecisionRequest, GateDecisionResponse, validate_requirements_edits()

### Community 185 - "port.py"
Cohesion: 0.16
Nodes (16): _fix(), fix_prompt(), layout_source(), nav_source(), persist_prototype(), _port(), PortFailed, reset_previous_build() (+8 more)

### Community 186 - "guard.py"
Cohesion: 0.13
Nodes (4): _forbidden(), UnsafeRequestGuard, create_app(), set_preview_manager()

### Community 190 - "collections_abc"
Cohesion: 0.32
Nodes (3): downgrade(), _swap(), upgrade()

### Community 199 - "get_settings"
Cohesion: 0.18
Nodes (10): now(), include_extra(), on_startup(), mark_consumed(), apply_retention(), run_dir(), test_default_is_off_and_startup_deletes_nothing(), test_old_inputs_are_deleted_and_artifacts_kept() (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `poc-studio-api`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1174 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `up()` connect `bT` to `toast.js`, `i`, `A`, `app.js`?**
  _High betweenness centrality (0.229) - this node is a cross-community bridge._
- **What connects `poc-studio-api` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013941543353308059 - nodes in this community are weakly interconnected._
- **Why does `steps()` connect `app.js` to `healthcare kit: selector and anchor guide`, `ScreenPack`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.06256384065372829 - nodes in this community are weakly interconnected._
- **Why does `build_plan()` connect `ScreenPack` to `app.js`, `build_fixture.py`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Should `web/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.08522727272727272 - nodes in this community are weakly interconnected._