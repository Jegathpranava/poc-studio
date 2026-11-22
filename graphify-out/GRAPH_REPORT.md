# Graph Report - poc-studio  (2026-11-22)

## Corpus Check
- 402 files · ~173,672 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .css 34, (none) 11, .vtt 5)

## Summary
- 3899 nodes · 10835 edges · 203 communities (127 shown, 76 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 617 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5469c2f6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- toast.js
- i
- web/package.json
- pitch.py
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
- validate.py
- parse_build_error
- A
- new-run-form.tsx
- app.js
- ScreenPack
- open_session
- PoC Studio — Developer Guidelines & Architecture Rules
- 0005_repo_artifact.py
- github/publish.py
- checks.py
- ecommerce/app/package.json
- PoC Studio — Developer Guidelines & Architecture Rules
- UI preview
- runtime.js
- constructor
- test_screens.py
- secrets.py
- timeline-view.tsx
- QAInputs
- re
- parse.py
- share.py
- package.json
- decide
- fintech/app/package.json
- FakeProvider
- t
- test_validate.py
- port.py
- graph/conftest.py
- healthcare/app/package.json
- logistics/app/package.json
- compilerOptions
- compilerOptions
- compilerOptions
- owner-direction-2026-11-22.md
- NEXT_STEPS.md
- check-github-token.sh
- api.ts
- test_pii.py
- poc-studio-api
- settings.py
- compilerOptions
- media/video.py
- compilerOptions
- typing
- ref_node_path
- run_eval.py
- _make_binary_fixtures.py
- settings-form.tsx
- BuildResult
- test_export.py
- A
- Technical Requirements Document: Returns and Substitution Assistant
- Technical Requirements Document: Last-Mile Route Re-Optimiser
- Business Requirements Document: Dock Scheduling Assistant
- sd
- intelligence.py
- Business Requirements Document: Patient Intake and Prior Authorisation Assistant
- Wv
- dependencies
- routes/revise.py
- env
- Recorder
- api.ts
- db/models.py
- now
- bT
- sample.md
- Sector templates
- web/README.md
- AGENTS.md
- wait_status
- GitHubClient
- W
- pptx.py
- gate2-view.tsx
- _latest_file
- github/publish.py
- MockGitHub
- pathlib
- FakeBuild
- architecture-view.tsx
- RunService
- schemas.py
- runner.py
- TestClient
- pytest
- deck_runtime/README.md
- eo
- test_video_node.py
- screenpack.py
- test_full_run.py
- test_jsx.py
- complete_json
- Eval
- Settings
- seed_run
- test_drift.py
- Settings
- web/app/layout.tsx
- dev.mjs
- open_session
- LiveGitHub
- page.py
- build.mjs
- scripts
- _drive
- post
- loose_match
- test_artifacts_files.py
- guard.py
- tokens.py
- create_run
- test_gate2.py
- manager.py
- _ensure
- run-context.tsx
- github/client.py
- Decisions
- decide_gate
- FakeEventSource
- launch_next
- health

## God Nodes (most connected - your core abstractions)
1. `open_session()` - 135 edges
2. `get_settings()` - 110 edges
3. `wait_status()` - 90 edges
4. `create_run()` - 81 edges
5. `DeckPlan` - 65 edges
6. `ScreenPack` - 65 edges
7. `A()` - 58 edges
8. `Run` - 57 edges
9. `step_scope()` - 54 edges
10. `i()` - 53 edges

## Surprising Connections (you probably didn't know these)
- `7. Data model and interfaces` --references--> `DeckPlan`  [INFERRED]
  docs/specs/2026-11-22-poc-studio-design.md → services/api/poc_studio/schemas/deck.py
- `Measures` --references--> `no_secrets()`  [INFERRED]
  eval/README.md → services/api/poc_studio/qa/checks.py
- `LLM pricing` --references--> `InputTooLarge`  [INFERRED]
  docs/decisions.md → services/api/poc_studio/llm/budget.py
- `7a. Deck and prototype output contract (amendment 8)` --references--> `ScreenPack`  [INFERRED]
  docs/specs/2026-11-22-poc-studio-design.md → services/api/poc_studio/schemas/screenpack.py
- `Request changes, retry and budget` --references--> `RunBudgetBanner()`  [INFERRED]
  docs/decisions.md → apps/web/components/run/budget-banner.tsx

## Import Cycles
- None detected.

## Communities (203 total, 76 thin omitted)

### Community 0 - "toast.js"
Cohesion: 0.01
Nodes (137): _4(), add(), addValue(), addVariantChild(), Ag(), b4(), bindToMotionValue(), BM() (+129 more)

### Community 1 - "i"
Cohesion: 0.06
Nodes (88): Aa(), ap(), bD(), bT(), c1(), Cg(), cT(), Dd() (+80 more)

### Community 2 - "web/package.json"
Cohesion: 0.09
Nodes (31): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, jsdom@^31.0.1, openapi-typescript@^7.13.0, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3 (+23 more)

### Community 3 - "pitch.py"
Cohesion: 0.07
Nodes (33): apply_patch(), build_prompt(), check_plan(), add(), figure_problem(), _pick(), polish_input(), Polished (+25 more)

### Community 4 - "react"
Cohesion: 0.06
Nodes (19): AppLayout(), metadata, ShareLayout(), AppShell(), Brand(), BudgetMeter(), NAV_ITEMS, NavItem (+11 more)

### Community 5 - "Tasks"
Cohesion: 0.05
Nodes (36): File map, Global constraints, Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues) (+28 more)

### Community 6 - "runs-view.tsx"
Cohesion: 0.10
Nodes (30): RunsPage(), durationMs(), formatDuration(), formatUsd(), formatWhen(), matchesFilter(), matchesQuery(), PLACEHOLDER (+22 more)

### Community 7 - "_t"
Cohesion: 0.11
Nodes (20): ao(), CO(), Da(), Dv(), dx(), e3(), f1(), hx() (+12 more)

### Community 8 - "test_manager.py"
Cohesion: 0.26
Nodes (15): Fake, make_runs(), record_previews(), recorded(), test_a_process_that_died_after_the_http_check_is_not_served(), test_concurrent_ensure_gets_distinct_ports(), test_dead_server_is_restarted(), test_failed_start_releases_the_reservation_and_stop_drops_the_lock() (+7 more)

### Community 9 - "MockProvider"
Cohesion: 0.11
Nodes (5): ChatReply, MockProvider, _reskin_screens(), Recorder, Recorder

### Community 10 - "api.ts"
Cohesion: 0.23
Nodes (12): DeckPage(), DeckPanel(), DeckView(), DocsPanel(), ErrorBanner(), formatTime(), VideoPanel(), VideoState (+4 more)

### Community 11 - "steps"
Cohesion: 0.08
Nodes (25): runs-on, steps, timeout-minutes, env, APP_ENV, GITHUB_MODE, LLM_PROVIDER, jobs (+17 more)

### Community 12 - "brief-view.tsx"
Cohesion: 0.13
Nodes (30): BriefPage(), BriefFeatures(), PRIORITIES, Props, BriefGoalsPanel(), Props, BriefSide(), Props (+22 more)

### Community 13 - "PreviewManager"
Cohesion: 0.12
Nodes (6): lifespan(), Entry, PreviewError, PreviewManager, loop(), test_build_serve_get_stop()

### Community 14 - "test_run_eval.py"
Cohesion: 0.20
Nodes (12): _load(), restore_env(), test_dry_eval_restores_the_env_and_the_runner(), test_dry_eval_two_fixtures(), test_dry_full_stage_two_fixtures(), test_full_live_is_refused_without_the_flag(), test_github_is_forced_to_mock_and_video_to_fake_even_when_live(), test_live_is_refused_inside_run_eval_without_the_flag() (+4 more)

### Community 15 - "llm/client.py"
Cohesion: 0.15
Nodes (9): _resolve(), Result, SchemaError, repair_prompt(), strip_fences(), ChatProvider, GatewayProvider, get_provider() (+1 more)

### Community 17 - "validate.py"
Cohesion: 0.13
Nodes (19): DeckPlanInvalid, ScreenPackInvalid, url_problem(), Screen, _anchor_issues(), _css_url_issues(), _defined_classes(), _html_issues() (+11 more)

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
Cohesion: 0.07
Nodes (29): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T (+21 more)

### Community 22 - "ScreenPack"
Cohesion: 0.14
Nodes (33): assemble(), _check_css(), _check_html(), fail(), _check_script(), DeckNotSelfContained, _json_for_script(), _read() (+25 more)

### Community 23 - "open_session"
Cohesion: 0.07
Nodes (42): build_prompt(), _latest_requirements(), persist_architecture(), render_markdown(), run_architect(), _run_assemble(), repair_prompt(), run_pitch() (+34 more)

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.18
Nodes (10): 7 agents, Commands, Core tech stack (budget build, decided at intake), graphify, Human approval gates, Knowledge graph (graphify), Mission, PoC Studio — Developer Guidelines & Architecture Rules (+2 more)

### Community 25 - "0005_repo_artifact.py"
Cohesion: 0.83
Nodes (3): downgrade(), _swap(), upgrade()

### Community 26 - "github/publish.py"
Cohesion: 0.06
Nodes (33): _copy(), _file_count(), _latest_path(), latest_qa_report(), NothingToPublish, prepare_repo_dir(), publish_dir(), PublishResult (+25 more)

### Community 27 - "checks.py"
Cohesion: 0.22
Nodes (20): build_passed(), Check, costs_consistent(), _css_problems(), deck_present(), deck_self_contained(), _deck_text(), _fail() (+12 more)

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
Cohesion: 0.07
Nodes (44): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+36 more)

### Community 32 - "constructor"
Cohesion: 0.06
Nodes (56): addListeners(), af(), attachTimeline(), cancel(), clearAnimation(), clearListeners(), commitStyles(), constructor() (+48 more)

### Community 33 - "test_screens.py"
Cohesion: 0.11
Nodes (15): _full_run(), _run(), test_graph_run_repairs_polishes_and_stores_outputs(), test_run_goes_to_paused_budget_when_polish_does_not_fit(), _drive(), _run(), _plan_for(), Recorder (+7 more)

### Community 34 - "secrets.py"
Cohesion: 0.12
Nodes (18): _assignment_is_secret(), _files(), Finding, _kind(), _line_at(), scan_pii(), add(), scan_text() (+10 more)

### Community 35 - "timeline-view.tsx"
Cohesion: 0.09
Nodes (44): RunTimelinePage(), CostByModel(), COPY, GateRow(), NextForYou(), CLASS, elapsed(), PipelineStep() (+36 more)

### Community 36 - "QAInputs"
Cohesion: 0.21
Nodes (16): QAInputs, run_checks(), Figure, test_build_passed(), test_costs_consistent(), test_deck_present(), test_deck_self_contained(), test_every_check_passes_on_the_good_inputs() (+8 more)

### Community 37 - "re"
Cohesion: 0.24
Nodes (14): test_no_external_src_or_href(), _defined_classes(), _fragment(), _kit(), _strip_comments(), _strip_urls(), test_anchors(), test_app_kit_copies_match() (+6 more)

### Community 38 - "parse.py"
Cohesion: 0.09
Nodes (34): build_prompt(), format_ts(), _norm(), render_transcript(), validate_against_transcript(), found(), Segment, Transcript (+26 more)

### Community 39 - "share.py"
Cohesion: 0.17
Nodes (15): create_share_token(), download_share_zip(), export_share(), get_share_deck(), get_share_page(), get_share_video(), _manifest_warnings(), _shareable_run() (+7 more)

### Community 40 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, dev, lint, test, typecheck, version (+1 more)

### Community 41 - "decide"
Cohesion: 0.27
Nodes (14): decide(), Decision, bad(), ok(), test_after_two_send_backs_none_are_made_but_secrets_still_block(), test_all_passing_sends_nothing_back(), test_assemble_and_video_owners_are_never_sent_back(), test_build_failure_is_report_only() (+6 more)

### Community 42 - "fintech/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 43 - "FakeProvider"
Cohesion: 0.19
Nodes (16): wrap_untrusted(), Answer, FakeProvider, _call(), _run(), test_fenced_reply_parses(), test_mock_provider_fixture(), test_repair_on_second_attempt() (+8 more)

### Community 44 - "t"
Cohesion: 0.07
Nodes (38): Be(), bg(), c2(), cl(), cx(), DM(), fa(), fx() (+30 more)

### Community 45 - "test_validate.py"
Cohesion: 0.10
Nodes (23): codes(), mutated(), test_anchor_matching_nothing_fails_the_schema(), test_anchors_must_be_unique_per_screen(), test_app_class_must_equal_the_kit(), test_at_least_three_play_screens(), test_classes_must_be_defined(), test_event_handler_attributes_are_rejected() (+15 more)

### Community 46 - "port.py"
Cohesion: 0.07
Nodes (31): _fix(), fix_prompt(), layout_source(), nav_source(), persist_prototype(), _port(), PortFailed, _read_failing() (+23 more)

### Community 49 - "graph/conftest.py"
Cohesion: 0.11
Nodes (22): run_repo(), rerun_reason(), add_paid(), node_budget(), step_scope(), with_node(), run_with_budget(), spender() (+14 more)

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
Cohesion: 0.15
Nodes (20): PrototypePage(), BuildLog(), BuildStatus(), Device, DeviceFrame(), DeviceToggle(), FileTree(), Nodes() (+12 more)

### Community 62 - "test_pii.py"
Cohesion: 0.20
Nodes (10): mask_for_run(), mask_pii(), _options_path(), run_masks_pii(), write_run_options(), _name_forms(), test_keeps_a_stakeholders_own_address_only_when_named(), test_keeps_example_com_names_and_timestamps() (+2 more)

### Community 64 - "settings.py"
Cohesion: 0.08
Nodes (24): env_file_path(), env_hashes(), BudgetPatch, BudgetSettings, _client(), current(), GatewayPatch, GatewaySettings (+16 more)

### Community 67 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 68 - "media/video.py"
Cohesion: 0.17
Nodes (14): Chapter, _deck_slides(), fake_record(), _ffmpeg(), _finish(), probe(), record(), _to_mp4() (+6 more)

### Community 69 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "typing"
Cohesion: 0.06
Nodes (25): run_assemble(), after_gate1(), after_gate2(), after_qa(), build_graph(), builtin_nodes(), _gate_node(), gate_node() (+17 more)

### Community 71 - "ref_node_path"
Cohesion: 0.08
Nodes (14): SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, @playwright/test@^1.65.1 (+6 more)

### Community 72 - "run_eval.py"
Cohesion: 0.11
Nodes (25): _clear_caches(), client_name_from(), configure_env(), feature_found(), _finish_full(), _fmt_time(), _isolated(), LiveRefused (+17 more)

### Community 73 - "_make_binary_fixtures.py"
Cohesion: 0.24
Nodes (3): _esc(), make_docx(), make_pdf()

### Community 74 - "settings-form.tsx"
Cohesion: 0.14
Nodes (15): SettingsPage(), KeyStatus(), buildPatch(), Draft, SettingsForm(), save(), toDraft(), settingsApi (+7 more)

### Community 76 - "BuildResult"
Cohesion: 0.11
Nodes (13): build(), BuildResult, install(), prepare(), StepResult, _tail(), _no_real_npm(), fake_build() (+5 more)

### Community 79 - "test_export.py"
Cohesion: 0.19
Nodes (16): build_share_zip(), ShareBlocked, _zip(), external_refs(), run_dir(), _names(), test_export_is_recorded_once_per_path(), test_external_assets_are_refused() (+8 more)

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
Nodes (17): run_migrations_offline(), run_migrations_online(), apply_owner_input(), _client_name(), load_transcript(), next_requirements_version(), _project_input(), _record_usage() (+9 more)

### Community 86 - "Business Requirements Document: Patient Intake and Prior Authorisation Assistant"
Cohesion: 0.17
Nodes (11): 10. Risks, 1. Context, 2. Current pain points, 3. Objectives, 4. Must-have capabilities, 5. Should-have capabilities, 6. Compliance and security, 7. Budget and timeline (+3 more)

### Community 87 - "Wv"
Cohesion: 0.09
Nodes (48): Ai(), Ax(), Az(), Bv(), De(), ep(), eT(), Ft() (+40 more)

### Community 88 - "dependencies"
Cohesion: 0.17
Nodes (12): dependencies, @fontsource-variable/geist@^5.3.0, @fontsource-variable/geist-mono@^5.3.0, lucide-react@^1.77.0, mermaid@^12.3.0, next@16.4.6, react@19.3.0, react-dom@19.3.0 (+4 more)

### Community 89 - "routes/revise.py"
Cohesion: 0.25
Nodes (11): BudgetRequest, _fail(), _port_failed(), raise_budget(), retry_run(), RetryRequest, revise_artifact(), ReviseRequest (+3 more)

### Community 90 - "env"
Cohesion: 0.15
Nodes (4): _clear_caches(), client_for(), make(), env()

### Community 92 - "Recorder"
Cohesion: 0.16
Nodes (21): set_provider(), _fail_builds(), _paid(), PaidRecorder, _paused(), test_a_raise_resumes_with_no_duplicate_paid_call(), test_invalid_budgets_are_rejected(), test_retry_attempts_limit_the_builds() (+13 more)

### Community 93 - "api.ts"
Cohesion: 0.07
Nodes (35): TemplatesPage(), SharePage(), ShareRoute(), ShareView(), State, LABELS, TemplatesView(), ApiError (+27 more)

### Community 94 - "db/models.py"
Cohesion: 0.05
Nodes (26): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), options_from_state(), Base, Approval (+18 more)

### Community 95 - "now"
Cohesion: 0.23
Nodes (9): now(), UTCDateTime, on_startup(), _finish(), apply_retention(), test_default_is_off_and_startup_deletes_nothing(), test_old_inputs_are_deleted_and_artifacts_kept(), test_zero_days_turns_it_off() (+1 more)

### Community 96 - "bT"
Cohesion: 0.22
Nodes (11): cp(), cV(), dc(), dT(), fc(), ip(), mT(), pu() (+3 more)

### Community 99 - "Sector templates"
Cohesion: 0.40
Nodes (4): How the builder uses a kit, Sector templates, Starters, Tests

### Community 100 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 112 - "wait_status"
Cohesion: 0.07
Nodes (51): test_graph_run_writes_architecture(), test_markdown_download_rejects_other_types(), _brief(), _create(), test_client_and_sector_follow_the_owners_input(), test_extracted_sector_is_kept_when_the_owner_picked_none(), test_gate1_changes_makes_v2_with_note(), test_node_writes_artifact_and_step() (+43 more)

### Community 113 - "GitHubClient"
Cohesion: 0.31
Nodes (4): GitHubClient, RepoInfo, _create_repo(), _open_issues()

### Community 114 - "W"
Cohesion: 0.06
Nodes (54): aS(), bp(), ch(), ci(), cM(), Cn(), cS(), dh() (+46 more)

### Community 115 - "pptx.py"
Cohesion: 0.12
Nodes (9): _add_slide(), build_pptx(), _figure_value(), _rgb(), _text(), _Camel, PlayScreen, Slide (+1 more)

### Community 116 - "gate2-view.tsx"
Cohesion: 0.08
Nodes (52): Page(), ConfirmPublish(), Props, DeliveredView(), InAppItem(), ItemProps, summary(), Gate2View() (+44 more)

### Community 118 - "_latest_file"
Cohesion: 0.12
Nodes (13): download_markdown_artifact(), FileNode, get_build(), get_deck_html(), get_deck_pptx(), get_doc(), get_file_tree(), get_json_artifact() (+5 more)

### Community 119 - "github/publish.py"
Cohesion: 0.11
Nodes (23): _check_clean(), _git(), git_auth_header(), _git_env(), publish(), PublishBlocked, PublishFailed, PublishOptions (+15 more)

### Community 126 - "pathlib"
Cohesion: 0.11
Nodes (9): _a(), _hashes_of(), _sha(), strip_ansi(), apply_overrides(), effective_hours_saved(), load(), save() (+1 more)

### Community 127 - "FakeBuild"
Cohesion: 0.22
Nodes (3): FakeBuild, FakePreviews, test_a_port_run_stops_that_runs_preview_first()

### Community 128 - "architecture-view.tsx"
Cohesion: 0.13
Nodes (21): ArchitecturePage(), ArchitectureView(), Load, CostTable(), MermaidDiagram(), Result, themeVariables(), token() (+13 more)

### Community 130 - "schemas.py"
Cohesion: 0.14
Nodes (20): AgentStepOut, ArtifactJson, ArtifactOut, BudgetRaiseRequest, CreateRunOptions, CreateRunResponse, EventError, GateDecisionResponse (+12 more)

### Community 132 - "runner.py"
Cohesion: 0.18
Nodes (16): child_env(), _command(), container_name(), _run(), sandbox_mode(), shared_npm_cache(), _python(), test_child_env_has_no_secrets_and_keeps_path() (+8 more)

### Community 133 - "TestClient"
Cohesion: 0.25
Nodes (10): test_a_bad_host_is_400(), test_a_post_without_origin_passes(), test_gets_are_never_blocked(), test_json_post_from_a_foreign_origin_is_403(), test_json_post_from_the_app_origin_passes(), test_local_hosts_are_allowed(), test_multipart_run_creation_from_the_app_origin_passes(), test_put_and_delete_are_guarded_too() (+2 more)

### Community 136 - "pytest"
Cohesion: 0.13
Nodes (21): plan_holds(), _deck_files(), test_assembled_deck_runs_every_step(), test_graph_run_assembles_a_self_contained_deck(), browser_name_and_browser(), deck_html(), icons_css(), pack() (+13 more)

### Community 138 - "eo"
Cohesion: 0.08
Nodes (32): $d(), eo(), ey(), Fh(), Fv(), hc(), hE(), hp() (+24 more)

### Community 139 - "test_video_node.py"
Cohesion: 0.24
Nodes (8): _rows(), test_failing_recorder_fails_the_step_but_not_the_run(), boom(), test_full_run_records_a_video_after_gate_2(), test_no_placeholder_warning_without_video_fake(), test_startup_logs_a_warning_when_video_fake_is_set(), test_video_fake_emits_a_placeholder_warning(), _to_end()

### Community 142 - "screenpack.py"
Cohesion: 0.18
Nodes (4): Anchor, anchors_of(), build_pack(), step_css()

### Community 143 - "test_full_run.py"
Cohesion: 0.35
Nodes (9): _agents(), _artifacts(), _assert_order(), _drive(), _reports(), test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(), test_full_run_through_both_gates_to_delivered(), test_planted_secret_sends_back_port_only_and_blocks_publish() (+1 more)

### Community 145 - "test_jsx.py"
Cohesion: 0.06
Nodes (29): route_file(), node_access_problem(), apply_fix(), FixFile, PortFix, safe_path(), UnsafePath, _attr_value() (+21 more)

### Community 146 - "complete_json"
Cohesion: 0.14
Nodes (14): BudgetExceeded, count_tokens(), InputTooLarge, RunBudget, complete_json(), cost_usd(), is_claude(), prices() (+6 more)

### Community 147 - "Eval"
Cohesion: 0.22
Nodes (8): Dry mode, Eval, Flags, Isolation, Live mode, Measures, Stages, Success measures (full summary)

### Community 148 - "Settings"
Cohesion: 0.12
Nodes (5): Settings, MonthlyCost, test_get_github_selects_by_mode(), test_production_refuses_mock_github(), test_production_refuses_mock_llm()

### Community 149 - "seed_run"
Cohesion: 0.22
Nodes (10): seed_run(), _build(), test_stats_come_from_the_runs(), test_expired_token_is_404_on_a_fake_clock(), test_public_json(), test_run_must_be_delivered_or_at_gate2_with_a_deck(), test_share_export_route_and_download(), test_share_export_with_a_secret_is_422_without_the_value() (+2 more)

### Community 150 - "test_drift.py"
Cohesion: 0.24
Nodes (8): _codes(), _product_css(), _screen_html(), change(), _script(), test_style_is_forbidden_by_the_validator_only(), test_the_baseline_is_clean_on_both_sides(), test_validate_and_assemble_reject_the_same_bad_pack()

### Community 151 - "Settings"
Cohesion: 0.19
Nodes (13): GitHubError, RepoNameTaken, test_a_github_error_fails_the_run(), get_user(), _client(), wrapped(), test_create_issue_and_repo_exists(), handler() (+5 more)

### Community 154 - "web/app/layout.tsx"
Cohesion: 0.28
Nodes (6): metadata, RootLayout(), AppToaster(), TOAST_OPTIONS, sileo@^0.1.6, sileo

### Community 158 - "dev.mjs"
Cohesion: 0.19
Nodes (8): children, kill(), root, shutdown(), start(), api, groups, root

### Community 161 - "open_session"
Cohesion: 0.05
Nodes (24): Event, event_name(), EventBus, load_events(), Subscription, to_event(), install_log_redaction(), redact() (+16 more)

### Community 166 - "page.py"
Cohesion: 0.19
Nodes (5): ShareContent, render_pdf(), render_index(), _tokens(), write_pdf()

### Community 167 - "build.mjs"
Cohesion: 0.27
Nodes (7): SAMPLE, status(), waitFor(), build(), here, orderScripts(), read()

### Community 168 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, gen:types, lint, start, test (+1 more)

### Community 176 - "_drive"
Cohesion: 0.28
Nodes (7): _drive(), _reports(), _steps(), test_missing_deck_fails_deck_present_and_the_run_still_reaches_gate2(), test_mock_run_reaches_gate2_with_a_passing_qa_report(), test_planted_secret_sends_port_back_twice_then_blocks_publish(), test_real_run_without_a_deck_is_flagged_even_without_a_failure_marker()

### Community 177 - "post"
Cohesion: 0.26
Nodes (7): InvalidUpload, safe_name(), post(), test_colon_names_rejected(), test_safe_name_compares_casefolded(), test_too_many_files(), test_total_size_limit()

### Community 178 - "loose_match"
Cohesion: 0.50
Nodes (3): loose_match(), _words(), test_loose_match_is_60_percent_of_long_words()

### Community 182 - "test_artifacts_files.py"
Cohesion: 0.27
Nodes (8): names(), test_build_returns_build_json(), test_file_tree_depth_is_capped_at_six(), test_file_tree_skips_node_modules_next_and_dotfiles(), test_files_and_build_404_for_unknown_run_and_no_app(), test_preview_409_until_built_then_redirects_to_the_direct_url(), test_traversal_is_impossible_there_is_no_path_input(), write()

### Community 187 - "tokens.py"
Cohesion: 0.29
Nodes (5): ShareToken, create_token(), hash_token(), resolve_token(), _utcnow()

### Community 188 - "create_run"
Cohesion: 0.20
Nodes (4): create_run(), get_service(), _total_message(), RunOptions

### Community 189 - "test_gate2.py"
Cohesion: 0.47
Nodes (7): _approvals(), test_approve_stores_the_options_and_delivers(), test_block_publish_returns_409_and_leaves_the_gate_open(), test_invalid_options_return_422(), test_missing_options_default_to_a_private_repo_named_from_the_client(), test_publish_status_is_pending_before_gate_2_and_404_for_unknown(), _to_gate2()

### Community 190 - "manager.py"
Cohesion: 0.13
Nodes (7): http_ready(), kill_pid_tree(), looks_like_preview_image(), pid_alive(), process_image(), _docker_kill(), _kill_tree()

### Community 191 - "_ensure"
Cohesion: 0.33
Nodes (4): _ensure(), PreviewInfo, redirect_preview(), start_preview()

### Community 192 - "run-context.tsx"
Cohesion: 0.08
Nodes (42): RunLayout(), BannerProps, BudgetBanner(), RunBudgetBanner(), RequestChanges(), RequestChangesProps, ReviseButton(), RunContext (+34 more)

### Community 193 - "github/client.py"
Cohesion: 0.31
Nodes (3): get_github(), GitHubNotConfigured, test_get_github_refuses_live_without_a_token()

### Community 194 - "Decisions"
Cohesion: 0.25
Nodes (7): Decisions, GitHub publish, LLM pricing, Request changes, retry and budget, Resolved values, Task 1 notes, Verified prices

### Community 195 - "decide_gate"
Cohesion: 0.38
Nodes (3): decide_gate(), _publish_options(), GateDecisionRequest

## Knowledge Gaps
- **1 isolated node(s):** `poc-studio-api`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1178 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `intelligence.py` to `graph/conftest.py`, `github/publish.py`, `media/video.py`, `app.js`?**
  _High betweenness centrality (0.269) - this node is a cross-community bridge._
- **What connects `poc-studio-api` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013941543353308059 - nodes in this community are weakly interconnected._
- **Why does `up()` connect `bT` to `toast.js`, `i`, `A`, `app.js`?**
  _High betweenness centrality (0.263) - this node is a cross-community bridge._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.06256384065372829 - nodes in this community are weakly interconnected._
- **Why does `Request changes, retry and budget` connect `Decisions` to `run-context.tsx`, `RunService`, `typing`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Should `web/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.08712121212121213 - nodes in this community are weakly interconnected._