# Graph Report - poc-studio  (2026-11-23)

## Corpus Check
- 404 files · ~174,665 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .css 34, (none) 11, .vtt 5)

## Summary
- 3923 nodes · 11116 edges · 177 communities (126 shown, 51 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 936 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d35e18b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- toast.js
- i
- web/package.json
- plan
- react
- Tasks
- runs-view.tsx
- _t
- test_manager.py
- test_usage_fallback.py
- api.ts
- steps
- brief-view.tsx
- BuildError
- test_run_eval.py
- json_repair.py
- open_session
- validate.py
- parse_build_error
- A
- new-run-form.tsx
- app.js
- ScreenPack
- get_settings
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
- revise-button.tsx
- re
- parse.py
- share.py
- package.json
- run-context.tsx
- fintech/app/package.json
- test_timeout.py
- t
- test_validate.py
- settings-form.tsx
- healthcare/app/package.json
- logistics/app/package.json
- compilerOptions
- compilerOptions
- compilerOptions
- owner-direction-2026-11-22.md
- NEXT_STEPS.md
- check-github-token.sh
- api.ts
- wait_status
- poc-studio-api
- settings.py
- compilerOptions
- media/video.py
- compilerOptions
- PageHead
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
- MockGitHub
- dependencies
- env
- wait_status
- share-api.ts
- db/models.py
- test_json.py
- bT
- sample.md
- Sector templates
- web/README.md
- AGENTS.md
- Answer
- client
- GitHubClient
- W
- deck.py
- gate2-view.tsx
- FakeProvider
- _latest_file
- test_publish.py
- _fake_pdf
- InputTooLarge
- decide
- tokens.py
- build.mjs
- json
- architecture-view.tsx
- RunService
- schemas.py
- _run
- TestClient
- requirements.py
- test_full_run.py
- deck_runtime/README.md
- eo
- page.py
- _broken_json
- app.js
- test_jsx.py
- complete_json
- Settings
- el
- test_drift.py
- Settings
- test_tokens.py
- web/app/layout.tsx
- Path
- dev.mjs
- mountScreen
- MockProvider
- routes/publish.py
- datetime
- LiveGitHub
- healthcare kit: selector and anchor guide
- test_schemas.py
- scripts
- os
- Eval
- build_fixture.py
- loose_match
- guard.py
- 0005_repo_artifact.py
- now

## God Nodes (most connected - your core abstractions)
1. `open_session()` - 135 edges
2. `get_settings()` - 113 edges
3. `wait_status()` - 90 edges
4. `client()` - 87 edges
5. `ScreenPack` - 82 edges
6. `create_run()` - 81 edges
7. `DeckPlan` - 74 edges
8. `Run` - 70 edges
9. `Artifact` - 68 edges
10. `A()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `7. Data model and interfaces` --references--> `DeckPlan`  [INFERRED]
  docs/specs/2026-11-22-poc-studio-design.md → services/api/poc_studio/schemas/deck.py
- `File map` --references--> `NodeSpec`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/graph/registry.py
- `Measures` --references--> `no_secrets()`  [INFERRED]
  eval/README.md → services/api/poc_studio/qa/checks.py
- `Example screens` --references--> `steps()`  [INFERRED]
  templates/healthcare/kit/selectors.md → services/api/tests/fixtures/deck/build_fixture.py
- `Task 16: MP4 recorder and Deck and video page  [after: 8, 14, 15]` --references--> `video_check()`  [INFERRED]
  docs/plans/2026-11-22-poc-studio-build.md → services/api/poc_studio/media/video.py

## Import Cycles
- None detected.

## Communities (177 total, 51 thin omitted)

### Community 0 - "toast.js"
Cohesion: 0.01
Nodes (137): _4(), add(), addValue(), addVariantChild(), Ag(), b4(), bindToMotionValue(), BM() (+129 more)

### Community 1 - "i"
Cohesion: 0.06
Nodes (88): Aa(), ap(), bD(), bT(), c1(), Cg(), cT(), Dd() (+80 more)

### Community 2 - "web/package.json"
Cohesion: 0.09
Nodes (29): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, jsdom@^31.0.1, openapi-typescript@^7.13.0, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3 (+21 more)

### Community 3 - "plan"
Cohesion: 0.15
Nodes (15): check_plan(), add(), figure_problem(), resolve_source(), _sources(), codes(), plan(), test_close_slide_needs_two_to_four_figures() (+7 more)

### Community 4 - "react"
Cohesion: 0.06
Nodes (18): AppLayout(), metadata, ShareLayout(), AppShell(), Brand(), BudgetMeter(), NAV_ITEMS, NavItem (+10 more)

### Community 5 - "Tasks"
Cohesion: 0.06
Nodes (33): File map, Global constraints, Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues) (+25 more)

### Community 6 - "runs-view.tsx"
Cohesion: 0.10
Nodes (29): RunsPage(), durationMs(), formatDuration(), formatUsd(), formatWhen(), matchesFilter(), matchesQuery(), PLACEHOLDER (+21 more)

### Community 7 - "_t"
Cohesion: 0.11
Nodes (20): ao(), CO(), Da(), Dv(), dx(), e3(), f1(), hx() (+12 more)

### Community 8 - "test_manager.py"
Cohesion: 0.08
Nodes (25): Entry, launch_next(), PreviewError, PreviewManager, loop(), _ensure(), PreviewInfo, redirect_preview() (+17 more)

### Community 10 - "api.ts"
Cohesion: 0.23
Nodes (12): DeckPage(), DeckPanel(), DeckView(), DocsPanel(), ErrorBanner(), formatTime(), VideoPanel(), VideoState (+4 more)

### Community 11 - "steps"
Cohesion: 0.08
Nodes (25): runs-on, steps, timeout-minutes, env, APP_ENV, GITHUB_MODE, LLM_PROVIDER, jobs (+17 more)

### Community 12 - "brief-view.tsx"
Cohesion: 0.13
Nodes (30): BriefPage(), BriefFeatures(), PRIORITIES, Props, BriefGoalsPanel(), Props, BriefSide(), Props (+22 more)

### Community 13 - "BuildError"
Cohesion: 0.11
Nodes (13): PortFailed, BuildError, build(), BuildResult, install(), prepare(), StepResult, _tail() (+5 more)

### Community 14 - "test_run_eval.py"
Cohesion: 0.27
Nodes (10): _load(), restore_env(), test_dry_eval_restores_the_env_and_the_runner(), test_dry_eval_two_fixtures(), test_dry_full_stage_two_fixtures(), test_full_live_is_refused_without_the_flag(), test_github_is_forced_to_mock_and_video_to_fake_even_when_live(), test_live_is_refused_inside_run_eval_without_the_flag() (+2 more)

### Community 16 - "open_session"
Cohesion: 0.09
Nodes (24): _factory(), open_session(), event_name(), load_events(), to_event(), _drive(), _reports(), _steps() (+16 more)

### Community 17 - "validate.py"
Cohesion: 0.12
Nodes (18): DeckPlanInvalid, ScreenPackInvalid, Anchor, Screen, _anchor_issues(), _css_url_issues(), _defined_classes(), _html_issues() (+10 more)

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
Cohesion: 0.13
Nodes (35): assemble(), _check_css(), _check_html(), fail(), _check_script(), DeckNotSelfContained, _json_for_script(), _read() (+27 more)

### Community 23 - "get_settings"
Cohesion: 0.04
Nodes (70): Task 6: Run engine, events, SSE, gates  [after: 4, 5], build_prompt(), _latest_requirements(), persist_architecture(), render_markdown(), run_architect(), run_assemble(), _run_assemble() (+62 more)

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.18
Nodes (10): 7 agents, Commands, Core tech stack (budget build, decided at intake), graphify, Human approval gates, Knowledge graph (graphify), Mission, PoC Studio — Developer Guidelines & Architecture Rules (+2 more)

### Community 25 - "test_settings.py"
Cohesion: 0.17
Nodes (9): env_file_path(), _gateway_mode(), secrets_set(), test_key_not_set_reads_false(), test_put_never_writes_env(), test_put_updates_the_budget_and_persists(), test_test_gateway_failure_is_reported_without_the_key(), test_test_gateway_in_mock_mode_makes_no_network_call() (+1 more)

### Community 26 - "github/publish.py"
Cohesion: 0.12
Nodes (16): _copy(), _git(), git_auth_header(), _git_env(), _latest_path(), latest_qa_report(), NothingToPublish, prepare_repo_dir() (+8 more)

### Community 27 - "checks.py"
Cohesion: 0.14
Nodes (36): build_passed(), Check, costs_consistent(), _css_problems(), deck_present(), deck_self_contained(), _deck_text(), _fail() (+28 more)

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
Nodes (22): _assignment_is_secret(), env_hashes(), _files(), Finding, _hashes_of(), _kind(), _line_at(), _name_forms() (+14 more)

### Community 35 - "timeline-view.tsx"
Cohesion: 0.08
Nodes (48): RunTimelinePage(), CostByModel(), COPY, GateRow(), NextForYou(), CLASS, elapsed(), PipelineStep() (+40 more)

### Community 36 - "revise-button.tsx"
Cohesion: 0.12
Nodes (24): BannerProps, BudgetBanner(), RunBudgetBanner(), RequestChanges(), RequestChangesProps, ReviseButton(), Props, StepActions() (+16 more)

### Community 37 - "re"
Cohesion: 0.22
Nodes (15): test_no_external_src_or_href(), _defined_classes(), _fragment(), _kit(), _strip_comments(), _strip_urls(), test_anchors(), test_app_kit_copies_match() (+7 more)

### Community 38 - "parse.py"
Cohesion: 0.09
Nodes (33): Task 5: Ingest parsers and eval fixtures  [after: 1, parallel with 4], build_prompt(), format_ts(), load_transcript(), render_transcript(), Segment, Transcript, FileTooLarge (+25 more)

### Community 39 - "share.py"
Cohesion: 0.19
Nodes (11): create_share_token(), download_share_zip(), export_share(), get_share_deck(), get_share_page(), get_share_video(), _shareable_run(), ShareExportOut (+3 more)

### Community 40 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, dev, lint, test, typecheck, version (+1 more)

### Community 41 - "run-context.tsx"
Cohesion: 0.11
Nodes (23): RunLayout(), Props, RunContext, RunContextValue, RunProvider(), useRun(), RunFrame(), RunSubnav() (+15 more)

### Community 42 - "fintech/app/package.json"
Cohesion: 0.11
Nodes (23): dependencies, next@16.4.6, react@19.3.0, react-dom@19.3.0, devDependencies, @types/node@^20, @types/react@^19, @types/react-dom@^19 (+15 more)

### Community 43 - "test_timeout.py"
Cohesion: 0.26
Nodes (7): GatewayProvider, _call(), test_explicit_timeout_wins(), test_gateway_sdk_does_not_retry(), test_setting_defaults_to_300_and_reads_env(), test_timeout_defaults_to_settings(), TimeoutRecorder

### Community 44 - "t"
Cohesion: 0.07
Nodes (38): Be(), bg(), c2(), cl(), cx(), DM(), fa(), fx() (+30 more)

### Community 45 - "test_validate.py"
Cohesion: 0.10
Nodes (22): codes(), mutated(), test_anchors_must_be_unique_per_screen(), test_app_class_must_equal_the_kit(), test_at_least_three_play_screens(), test_classes_must_be_defined(), test_event_handler_attributes_are_rejected(), test_exactly_one_home() (+14 more)

### Community 46 - "settings-form.tsx"
Cohesion: 0.13
Nodes (16): SettingsPage(), KeyStatus(), buildPatch(), Draft, SettingsForm(), save(), toDraft(), settingsApi (+8 more)

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
Cohesion: 0.17
Nodes (18): PrototypePage(), BuildLog(), BuildStatus(), Device, DeviceFrame(), DeviceToggle(), FileTree(), Nodes() (+10 more)

### Community 62 - "wait_status"
Cohesion: 0.13
Nodes (26): _finish(), step_scope(), BudgetExceeded, with_node(), run_with_budget(), spender(), fn(), test_charges_of_a_failed_attempt_stay_in_paid_usd() (+18 more)

### Community 64 - "settings.py"
Cohesion: 0.11
Nodes (19): BudgetPatch, BudgetSettings, _client(), current(), GatewayPatch, GatewaySettings, GatewayTest, get_current_settings() (+11 more)

### Community 67 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 68 - "media/video.py"
Cohesion: 0.11
Nodes (23): Chapter, _deck_slides(), fake_record(), _ffmpeg(), _finish(), plan_holds(), probe(), record() (+15 more)

### Community 69 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "PageHead"
Cohesion: 0.22
Nodes (12): Page(), TemplatesPage(), PublishFailed(), Message(), PublishView(), PageHead(), PageHeadProps, LABELS (+4 more)

### Community 71 - "ref_node_path"
Cohesion: 0.08
Nodes (14): SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, SAMPLE, @playwright/test@^1.65.1 (+6 more)

### Community 72 - "run_eval.py"
Cohesion: 0.11
Nodes (25): _clear_caches(), client_name_from(), configure_env(), feature_found(), _finish_full(), _fmt_time(), _isolated(), LiveRefused (+17 more)

### Community 73 - "_make_binary_fixtures.py"
Cohesion: 0.24
Nodes (3): _esc(), make_docx(), make_pdf()

### Community 74 - "build.py"
Cohesion: 0.13
Nodes (8): after_gate1(), after_gate2(), after_qa(), build_graph(), collect_nodes(), state(), test_default_app_has_no_stub_nodes(), test_send_back_cap_is_at_most_two()

### Community 75 - "PoC Studio: design spec"
Cohesion: 0.12
Nodes (16): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+8 more)

### Community 76 - "tests/conftest.py"
Cohesion: 0.29
Nodes (4): _create_tables(), _no_real_npm(), fake_build(), _no_real_recorder()

### Community 79 - "seed_run"
Cohesion: 0.16
Nodes (15): build_share_zip(), ShareBlocked, ShareUnavailable, external_refs(), _names(), test_export_is_recorded_once_per_path(), test_external_assets_are_refused(), test_index_is_self_contained() (+7 more)

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
Cohesion: 0.11
Nodes (18): apply_owner_input(), _client_name(), next_requirements_version(), _norm(), _project_input(), _record_usage(), run_intelligence(), save_requirements() (+10 more)

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

### Community 92 - "wait_status"
Cohesion: 0.04
Nodes (65): AgentStep, count_tokens(), _resolve(), Result, set_provider(), ChatProvider, ChatReply, get_provider() (+57 more)

### Community 93 - "share-api.ts"
Cohesion: 0.08
Nodes (29): SharePage(), ShareRoute(), ShareView(), State, ApiError, ArtifactJson, BASE_URL, failure() (+21 more)

### Community 94 - "db/models.py"
Cohesion: 0.04
Nodes (34): run_migrations_offline(), run_migrations_online(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), options_from_state() (+26 more)

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

### Community 111 - "Answer"
Cohesion: 0.33
Nodes (4): Answer, test_fast_model_live(), test_mask_applied_to_user_text(), test_wrap_untrusted_neutralises_wrapper_tags()

### Community 112 - "client"
Cohesion: 0.06
Nodes (64): record(), Approval, _fixture(), test_graph_run_writes_architecture(), test_markdown_download_rejects_other_types(), test_mermaid_must_be_a_diagram(), test_mock_output_validates(), test_total_must_match_lines() (+56 more)

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
Cohesion: 0.09
Nodes (45): ConfirmPublish(), Props, DeliveredView(), InAppItem(), ItemProps, summary(), Gate2View(), Qa (+37 more)

### Community 117 - "FakeProvider"
Cohesion: 0.53
Nodes (7): FakeProvider, _call(), test_caller_note_replaces_the_default(), test_other_broken_json_gets_a_short_note(), test_retries_do_not_grow_after_repeated_truncation(), test_schema_errors_still_show_the_reply_for_repair(), test_truncated_reply_is_not_echoed_back()

### Community 118 - "_latest_file"
Cohesion: 0.12
Nodes (13): download_markdown_artifact(), FileNode, get_build(), get_deck_html(), get_deck_pptx(), get_doc(), get_file_tree(), get_json_artifact() (+5 more)

### Community 119 - "test_publish.py"
Cohesion: 0.12
Nodes (19): _check_clean(), _file_count(), publish(), PublishBlocked, PublishOptions, _artifact_json(), _git(), _qa_report() (+11 more)

### Community 122 - "decide"
Cohesion: 0.27
Nodes (14): decide(), Decision, bad(), ok(), test_after_two_send_backs_none_are_made_but_secrets_still_block(), test_all_passing_sends_nothing_back(), test_assemble_and_video_owners_are_never_sent_back(), test_build_failure_is_report_only() (+6 more)

### Community 123 - "tokens.py"
Cohesion: 0.29
Nodes (5): ShareToken, create_token(), hash_token(), resolve_token(), _utcnow()

### Community 126 - "build.mjs"
Cohesion: 0.27
Nodes (7): SAMPLE, status(), waitFor(), build(), here, orderScripts(), read()

### Community 127 - "json"
Cohesion: 0.08
Nodes (20): polish_input(), mask_for_run(), mask_pii(), _options_path(), run_masks_pii(), write_run_options(), _first_time_ok(), _kits() (+12 more)

### Community 128 - "architecture-view.tsx"
Cohesion: 0.13
Nodes (21): ArchitecturePage(), ArchitectureView(), Load, CostTable(), MermaidDiagram(), Result, themeVariables(), token() (+13 more)

### Community 129 - "RunService"
Cohesion: 0.06
Nodes (26): lifespan(), decide_gate(), _publish_options(), BudgetRequest, _fail(), _port_failed(), raise_budget(), retry_run() (+18 more)

### Community 130 - "schemas.py"
Cohesion: 0.05
Nodes (32): EventBus, Subscription, event_stream(), _sse(), stream_events(), health(), get_run(), list_runs() (+24 more)

### Community 132 - "_run"
Cohesion: 0.21
Nodes (15): child_env(), _command(), container_name(), _run(), sandbox_mode(), _python(), test_child_env_has_no_secrets_and_keeps_path(), test_child_env_points_home_dirs_at_the_run_folder() (+7 more)

### Community 133 - "TestClient"
Cohesion: 0.28
Nodes (10): test_a_bad_host_is_400(), test_a_post_without_origin_passes(), test_gets_are_never_blocked(), test_json_post_from_a_foreign_origin_is_403(), test_json_post_from_the_app_origin_passes(), test_local_hosts_are_allowed(), test_multipart_run_creation_from_the_app_origin_passes(), test_put_and_delete_are_guarded_too() (+2 more)

### Community 134 - "requirements.py"
Cohesion: 0.10
Nodes (14): exec_summary(), user_flows(), Component, CostLine, ModelPick, MonthlyCost, Phase, ActionItem (+6 more)

### Community 136 - "test_full_run.py"
Cohesion: 0.30
Nodes (9): _agents(), _artifacts(), _assert_order(), _drive(), _reports(), test_failed_port_still_reaches_gate2_with_a_report_only_build_failure(), test_full_run_through_both_gates_to_delivered(), test_planted_secret_sends_back_port_only_and_blocks_publish() (+1 more)

### Community 138 - "eo"
Cohesion: 0.08
Nodes (32): $d(), eo(), ey(), Fh(), Fv(), hc(), hE(), hp() (+24 more)

### Community 142 - "page.py"
Cohesion: 0.31
Nodes (3): ShareContent, render_index(), _tokens()

### Community 144 - "app.js"
Cohesion: 0.22
Nodes (8): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T

### Community 145 - "test_jsx.py"
Cohesion: 0.05
Nodes (35): _fix(), layout_source(), nav_source(), _read_failing(), route_file(), _write(), write_app(), node_access_problem() (+27 more)

### Community 146 - "complete_json"
Cohesion: 0.17
Nodes (13): RunBudget, complete_json(), cost_usd(), is_claude(), prices(), test_polish_raises_budget_exceeded_on_a_tenth_of_a_cent(), test_claude_cost_nonzero(), test_claude_input_over_12k_tokens() (+5 more)

### Community 148 - "Settings"
Cohesion: 0.17
Nodes (3): Settings, test_production_refuses_mock_github(), test_production_refuses_mock_llm()

### Community 149 - "el"
Cohesion: 0.40
Nodes (8): build(), buildClose(), buildPlay(), buildWelcome(), el(), header(), spot(), txt()

### Community 150 - "test_drift.py"
Cohesion: 0.24
Nodes (8): _codes(), _product_css(), _screen_html(), change(), _script(), test_style_is_forbidden_by_the_validator_only(), test_the_baseline_is_clean_on_both_sides(), test_validate_and_assemble_reject_the_same_bad_pack()

### Community 151 - "Settings"
Cohesion: 0.12
Nodes (17): get_github(), GitHubError, GitHubNotConfigured, RepoNameTaken, http_ready(), get_user(), _client(), wrapped() (+9 more)

### Community 152 - "test_tokens.py"
Cohesion: 0.23
Nodes (9): _fixture(), seed_run(), test_expired_token_is_404_on_a_fake_clock(), test_public_json(), test_run_must_be_delivered_or_at_gate2_with_a_deck(), test_share_export_route_and_download(), test_share_export_with_a_secret_is_422_without_the_value(), test_token_is_stored_hashed_only() (+1 more)

### Community 154 - "web/app/layout.tsx"
Cohesion: 0.28
Nodes (6): metadata, RootLayout(), AppToaster(), TOAST_OPTIONS, sileo@^0.1.6, sileo

### Community 156 - "Path"
Cohesion: 0.29
Nodes (3): render_pdf(), _zip(), write_pdf()

### Community 158 - "dev.mjs"
Cohesion: 0.16
Nodes (10): @vitejs/plugin-react@^6.3.0, @vitejs/plugin-react, children, kill(), root, shutdown(), start(), api (+2 more)

### Community 159 - "mountScreen"
Cohesion: 0.40
Nodes (4): 7a. Deck and prototype output contract (amendment 8), show(), mountScreen(), toast()

### Community 160 - "MockProvider"
Cohesion: 0.13
Nodes (5): MockProvider, _reskin_screens(), Recorder, test_fixture_is_a_port_fix(), Recorder

### Community 161 - "routes/publish.py"
Cohesion: 0.25
Nodes (6): PublishResult, _approved_options(), _failure(), get_publish(), PublishStatus, _result()

### Community 165 - "healthcare kit: selector and anchor guide"
Cohesion: 0.40
Nodes (4): Anchors, Example screens, healthcare kit: selector and anchor guide, Scoping

### Community 167 - "test_schemas.py"
Cohesion: 0.23
Nodes (11): test_deck_contract(), test_anchor_matching_nothing_fails_the_schema(), _pack(), _plan(), _screen(), _slide(), test_deckplan_too_few_slides_fails(), test_deckplan_valid() (+3 more)

### Community 168 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, gen:types, lint, start, test (+1 more)

### Community 171 - "os"
Cohesion: 0.13
Nodes (8): write_requirements_file(), strip_ansi(), kill_pid_tree(), pid_alive(), process_image(), _docker_kill(), _kill_tree(), shared_npm_cache()

### Community 173 - "Eval"
Cohesion: 0.22
Nodes (8): Dry mode, Eval, Flags, Isolation, Live mode, Measures, Stages, Success measures (full summary)

### Community 174 - "build_fixture.py"
Cohesion: 0.38
Nodes (5): Task 11: Prototype Builder: ScreenPack  [after: 9, 10], Task 14: Vendored deck engine and assembler  [after: 1, parallel with 4-13; runs on the owner's machine, where `reference/` exists], anchors_of(), build_pack(), step_css()

### Community 177 - "loose_match"
Cohesion: 0.50
Nodes (3): loose_match(), _words(), test_loose_match_is_60_percent_of_long_words()

### Community 190 - "0005_repo_artifact.py"
Cohesion: 0.83
Nodes (3): downgrade(), _swap(), upgrade()

### Community 199 - "now"
Cohesion: 0.39
Nodes (8): now(), on_startup(), apply_retention(), run_dir(), test_default_is_off_and_startup_deletes_nothing(), test_old_inputs_are_deleted_and_artifacts_kept(), test_zero_days_turns_it_off(), _with_input()

## Knowledge Gaps
- **1 isolated node(s):** `poc-studio-api`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1169 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `up()` connect `bT` to `toast.js`, `i`, `A`, `app.js`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **What connects `poc-studio-api` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013941543353308059 - nodes in this community are weakly interconnected._
- **Why does `steps()` connect `app.js` to `healthcare kit: selector and anchor guide`, `ScreenPack`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.06256384065372829 - nodes in this community are weakly interconnected._
- **Why does `build_plan()` connect `ScreenPack` to `app.js`, `build_fixture.py`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Should `web/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.09247311827956989 - nodes in this community are weakly interconnected._