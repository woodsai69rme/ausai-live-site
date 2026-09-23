# Graph Report - tests  (2026-08-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 713 nodes · 855 edges · 50 communities (41 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `373cdf5f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _patch_snapshot_dir
- TestBomQuoteSanitization
- conftest.py
- TestPlanActionRouting
- _ns
- test_war_room_section_helpers.py
- TestCmdLaunchTrendCompare
- TestPluginManager
- _patch_snapshot_dir
- TestExamplePlugins
- FullStackytFreebuffTests
- _ns
- _patch_snapshot_dir
- _write_snapshot_via_mock
- SnapshotVerificationTests
- test_openrouter_lockstep.py
- test_free_resources_stack.py
- TestBasePlugin
- TestPluginRegistry
- _patch_snapshot_dir
- TestValidateTools9State
- test_mvs_model_aliases_lockstep.py
- test_revenue_packs.py
- TestParseRouterJson
- RefreshFullStackTests
- test_full_stackyt_dashboard_chrome.py
- test_freebuff_session_scan.py
- test_env_bridge.py
- TestEdgeCases
- test_start_offline_services.py
- test_plugins.py
- TestPluginMetadata
- TestHookResult
- TestPluginIntegration
- test_zeroone_watchdog.py
- test_automation_scheduler.py
- DashboardBrowserSmokeTests
- test_mcp_docker_lazy_init.py
- TestPluginType
- TestPluginHook
- TestVideoInfo
- test_preflight_path_creds.py
- SavedViewTests
- TestAnalysisResult
- TestUploadResult
- test_service_watchdog.py
- test_auth_dev_bypass.py
- tests/__init__.py
- unit/__init__.py
- test_security_controls.py

## God Nodes (most connected - your core abstractions)
1. `_patch_snapshot_dir()` - 26 edges
2. `FullStackytFreebuffTests` - 18 edges
3. `TestPlanActionRouting` - 17 edges
4. `TestPluginManager` - 14 edges
5. `SnapshotVerificationTests` - 12 edges
6. `TestExamplePlugins` - 12 edges
7. `_seed_snapshot()` - 12 edges
8. `_ns()` - 11 edges
9. `TestBomQuoteSanitization` - 11 edges
10. `TestSlugPatterns` - 11 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (50 total, 9 thin omitted)

### Community 0 - "_patch_snapshot_dir"
Cohesion: 0.08
Nodes (20): _patch_snapshot_dir(), Unit tests for cont.15 ws-doctor-trend additions to war_room.py.  Module-level i, MINOR #4 (cont.15): typing a DATE prefix with multiple same-day snapshots, cont.22: two writes within the same second must not overwrite., MINOR #2 (cont.15): detect --a == --b so operator doesn't mistake no-op for stab, MINOR #5 (cont.15): when only ONE snapshot exists, --b (default = most recent), Lock the schema_version read-time validation contract: missing/legacy OK,     un, Snapshots WITHOUT schema_version field (pre-cont.16 legacy) -> no [WARN]. (+12 more)

### Community 1 - "TestBomQuoteSanitization"
Cohesion: 0.06
Nodes (10): We don't shell out -- instead we verify the source of     cmd_validate_mobile co, Verify that the dynamic reader produces stable unique slugs     when MOBILE_FILT, Verify the slug-derivation logic in war_room.py produces stable unique slugs, Verify the .strip('\"\\ufeff') pattern handles every     combination of BOM + qu, Verify war_room.py imports cleanly, the auto-extension     call ran, and at leas, TestBomQuoteSanitization, TestSlugDerivation, TestSlugPatterns (+2 more)

### Community 2 - "conftest.py"
Cohesion: 0.06
Nodes (35): Any, mock_downloader_plugin(), mock_hook_plugin(), mock_logger(), mock_processor_plugin(), plugin_config(), plugin_manager_with_plugins(), plugin_with_mocked_logger() (+27 more)

### Community 3 - "TestPlanActionRouting"
Cohesion: 0.06
Nodes (7): Routing invariants for voice_ai_assistant — cross-file drift detection., TestHermesRegistry, TestOllamaFallback, TestPlanActionRouting, TestRule8PathFence, TestSearchKnowledge, TestSearchPlans

### Community 4 - "_ns"
Cohesion: 0.08
Nodes (24): _ns(), Unit tests for war_room.cmd_doctor (added cont.13).  cmd_doctor aggregates 7 sec, --json emits parseable dict with aggregate_ok + sections list of dicts., --json + one FAIL section -> aggregate_ok == False, rc=1., cmd_doctor --quiet mode detail suppression., --quiet only emits section badge + 1-line summary; hides multi-line detail., Without --quiet, multi-line detail IS emitted., cmd_doctor safety: missing/informational files must NOT bump aggregate to FAIL. (+16 more)

### Community 5 - "test_war_room_section_helpers.py"
Cohesion: 0.07
Nodes (10): Direct-IO unit tests for war_room's 7 _section_* helpers (added cont.14).  The c, cmd_health emits 5 lines; grades each via parts[2]., # NOTE: latency must use `{42:<10}` not `{'':>5}` -- an empty-string latency in, cmd_health prints 'HEALTH PROBE' header -- parts[2] won't be 'up'/'down'., TestSectionGit, TestSectionHealth, TestSectionMobileCsv, TestSectionPython (+2 more)

### Community 6 - "TestCmdLaunchTrendCompare"
Cohesion: 0.11
Nodes (19): _make_payload(), _patch_outbox_dir(), _patch_trend_compare(), Unit tests for cont.22 launch-trend-compare subcommand.  Covers (no live servi, All sections STABLE -> subprocess.run NOT called, alert NOT fired., At least one section MORE_FLAPPING -> subprocess.run IS called with opt_d_alerts, --emit-report writes .md + .json files to outbox/trend_reports/ with correct con, --a 0d (or any invalid format) -> rc=1, no subprocess, no file writes, no trend- (+11 more)

### Community 7 - "TestPluginManager"
Cohesion: 0.08
Nodes (14): Tests for PluginManager class., Test creating a PluginManager., Test creating manager with custom search paths., Test loading plugin configuration., Test saving plugin configuration., Test discovery in empty directory., Test discovering plugin files., Test loading a plugin. (+6 more)

### Community 8 - "_patch_snapshot_dir"
Cohesion: 0.11
Nodes (13): _patch_snapshot_dir(), Unit tests for cont.19 launch-trend subcommand.  Covers (no live services, real, If snapshot A fails, return rc=1 immediately (no diff/trend attempted)., Return code is max(snapshot_rc, diff_rc, trend_rc) - propagates hard failures., MINOR #2 (cont.19): --sleep must be >= 0; negative values are rejected at the, Locks the 3 invariants of _capture_stdout():       1. captures sys.stdout writes, Write a fake snapshot to fake_dir with explicit mtime + schema_version., snapshot A + sleep + snapshot B + diff + trend runs without error. (+5 more)

### Community 9 - "TestExamplePlugins"
Cohesion: 0.09
Nodes (12): Tests for example plugins., Test creating Vimeo downloader., Test Vimeo URL detection., Test creating Twitch downloader., Test Twitch URL detection., Test creating silence remover., Test creating watermark processor., Test creating Discord notifier. (+4 more)

### Community 11 - "_ns"
Cohesion: 0.16
Nodes (12): _ns(), Unit tests for war_room.cmd_archive_outbox (added cont.14).  cmd_archive_outbox, --json output shape contract., Edge cases that must NOT escalate to FAIL., Build SLEEP_TRIPLE/outbox/<subdir>/<file> layout from spec dict.      spec = {"a, Happy-path + core behavior., --keep-last and --category filters., _seed_outbox() (+4 more)

### Community 12 - "_patch_snapshot_dir"
Cohesion: 0.18
Nodes (11): _patch_snapshot_dir(), Unit tests for cont.21 trend-compare subcommand.  Covers (no live services, real, Bad --a or --b format -> [FAIL] + rc=1 (strict Nd format like cmd_trend_doctor)., Both windows empty (no snapshots) -> [INFO] no sections to compare + rc=0., Equal transition rates across equal-length windows -> STABLE., Section appears only in --b baseline window -> ta=0, tb>0 -> rate_a < rate_b ->, Write a fake snapshot__<stamp>.json with the given sections + mtime., 1d with 2 transitions vs 7d with 2 transitions -> MORE_FLAPPING (rate 2/day vs 0 (+3 more)

### Community 13 - "_write_snapshot_via_mock"
Cohesion: 0.20
Nodes (11): _fake_cmd_doctor_payload(), _patch_snapshot_dir(), End-to-end smoke test for cont.16 trending pipeline (synthetic data).  Exercises, Pipeline: A has 3 sections, B has 2 (one removed) -> 'tools' shows OK -> MISSING, Build a fake cmd_doctor --json payload (matches real schema)., Patch cmd_doctor + invoke cmd_snapshot_doctor. Returns the file written., Pipeline: write A (health=FAIL), write B (health=OK), diff -> 1 transition., Pipeline: write A, write B (same), diff -> PASS no transitions. (+3 more)

### Community 14 - "SnapshotVerificationTests"
Cohesion: 0.12
Nodes (3): DashboardAccessibilityTests, Tests for immutable snapshot verification and dashboard accessibility contracts., SnapshotVerificationTests

### Community 15 - "test_openrouter_lockstep.py"
Cohesion: 0.14
Nodes (14): _parse_canonical_ids_from_txt(), Path, tests/unit/test_openrouter_lockstep.py  Lockstep-invariant guard for the OpenRou, N must be in [1, 50]; catches accidental wipe or wildcard bloat., Every entry must end with ':free' -- router only dispatches :free tags., Router must signal 'cloud dispatch' for every FREE_MODELS entry., The ## \u2705 FREE OPENROUTER MODELS section header must exist     (format invar, Parse the ## ✅ FREE OPENROUTER MODELS section of the operator-discovery file. (+6 more)

### Community 16 - "test_free_resources_stack.py"
Cohesion: 0.18
Nodes (6): free_master(), _parse_canonical_openrouter_ids(), Path, Invariant tests for Free Resources catalog + Drive RAG lean backup + War Room fr, test_master_doc_has_start_here_table(), test_openrouter_operator_list_in_registry_matches_txt()

### Community 17 - "TestBasePlugin"
Cohesion: 0.14
Nodes (8): Tests for BasePlugin class., Test creating a concrete plugin implementation., Test plugin initialization lifecycle., Test plugin shutdown., Test configuration validation., Test plugin state transitions., Test is_initialized property., TestBasePlugin

### Community 18 - "TestPluginRegistry"
Cohesion: 0.14
Nodes (8): Tests for PluginRegistry class., Test registering a plugin., Test unregistering a plugin., Test getting plugins by type., Test registering a hook., Test disabling a plugin., Test getting registry statistics., TestPluginRegistry

### Community 19 - "_patch_snapshot_dir"
Cohesion: 0.31
Nodes (5): _patch_snapshot_dir(), Unit tests for cont.18 trend-doctor subcommand.  Covers (no live services, real, Write a fake snapshot__<stamp>.json with the given sections + mtime., _seed(), TestCmdTrendDoctor

### Community 20 - "TestValidateTools9State"
Cohesion: 0.18
Nodes (5): _bi_side_effect(), Verify that apktool/jadx versions are read from META-INF/MANIFEST.MF         (Im, Build an os.path.exists side_effect function from a set of substrings     that,, 9-state machine test via unittest.mock on subprocess.run + os.path.exists + shut, TestValidateTools9State

### Community 21 - "test_mvs_model_aliases_lockstep.py"
Cohesion: 0.23
Nodes (11): _parse_alias_dict_from_source(), tests/unit/test_mvs_model_aliases_lockstep.py  Lockstep-invariant guard for the, For every shared key, both dicts must map to the SAME canonical Ollama tag., N must be in [1, 20]; catches accidental wipe or pragma bloat., Every aliased tag must classify into ONE of the 3 valid routing categories., Statically parse a top-level dict literal from a Python source file.      We use, Both alias dicts must share the exact same set of keys., test_lockstep_invariant_mvs_model_aliases_all_classify_into_valid_category() (+3 more)

### Community 22 - "test_revenue_packs.py"
Cohesion: 0.17
Nodes (5): Invariant tests for Gumroad / n8n revenue packs + free_local_registry status., build() produces a non-empty zip containing workflow.json files., Empty GUMROAD_API_KEY must not count as configured., test_gumroad_api_key_empty_not_configured(), test_n8n_zip_buildable()

### Community 24 - "RefreshFullStackTests"
Cohesion: 0.25
Nodes (3): capture(), Tests for the metadata-only Full Stack refresh and drift tool., RefreshFullStackTests

### Community 25 - "test_full_stackyt_dashboard_chrome.py"
Cohesion: 0.27
Nodes (10): _chrome_candidates(), _find_chrome(), Path, Chrome smoke test for the generated Full Stack YouTube dashboard.  This test int, Run the temporary dashboard copy in headless Chrome and return its DOM., Verify search, select filtering, and detail interactions in Chrome., Return common Chrome/Chromium executable locations for this host., Find an installed Chrome/Chromium executable without installing anything. (+2 more)

### Community 26 - "test_freebuff_session_scan.py"
Cohesion: 0.40
Nodes (9): Path, _session(), test_cli_rejects_missing_source_without_echoing_path(), test_scan_classifies_session_storage_states(), test_scan_does_not_include_message_content(), test_scan_omits_absolute_source_path_by_default(), test_scan_reports_only_safe_parse_error_type(), test_scan_streams_large_chat_array() (+1 more)

### Community 27 - "test_env_bridge.py"
Cohesion: 0.20
Nodes (3): Invariant tests for SLEEP_TRIPLE env_bridge., Path in env alone must NOT mark youtube_oauth configured., test_credential_report_youtube_requires_file()

### Community 28 - "TestEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and error handling., Test plugin without proper name., Test plugin with None config., Test manager operations on nonexistent plugin., Test hook execution when callback raises exception., TestEdgeCases

### Community 29 - "test_start_offline_services.py"
Cohesion: 0.31
Nodes (7): Invariants for start_offline_services orchestrator., _source(), test_docker_probe_has_short_timeout(), test_docker_stale_cli_cleanup(), test_exit_code_scoped_to_target_ports(), test_n8n_has_native_fallback_when_docker_fails(), test_n8n_uses_docker_desktop_autostart()

### Community 30 - "test_plugins.py"
Cohesion: 0.31
Nodes (6): Path, Regression tests for repository security guardrails., test_scanner_allows_explicit_placeholder_without_suppressing_other_content(), test_scanner_detects_real_credential_without_printing_value(), test_scanner_rejects_paths_outside_repository(), test_scanner_reports_missing_paths_instead_of_skipping_them()

### Community 31 - "TestPluginMetadata"
Cohesion: 0.25
Nodes (7): plugin_config(), Unit Tests for YouTube Enhancement Tools Plugin System  This module contains com, Create a temporary directory for tests., Sample plugin configuration., Sample video info for testing., sample_video_info(), temp_dir()

### Community 32 - "TestHookResult"
Cohesion: 0.25
Nodes (5): Tests for PluginMetadata class., Test creating plugin metadata., Test converting metadata to dictionary., Test creating metadata from dictionary., TestPluginMetadata

### Community 33 - "TestPluginIntegration"
Cohesion: 0.25
Nodes (5): Tests for HookResult class., Test creating successful hook result., Test creating error hook result., Test creating skip result., TestHookResult

### Community 34 - "test_zeroone_watchdog.py"
Cohesion: 0.25
Nodes (5): Integration tests for the plugin system., Test complete plugin lifecycle., Test executing multiple hooks in chain., Test plugin error handling., TestPluginIntegration

### Community 35 - "test_automation_scheduler.py"
Cohesion: 0.25
Nodes (3): ZeroOne watchdog invariants — webhook URL + SQL splitter., TestSplitSql, TestWebhookUrl

### Community 36 - "DashboardBrowserSmokeTests"
Cohesion: 0.38
Nodes (6): _load_scheduler_module(), Regression tests for the standalone automation scheduler., Omitting run_at means a one-time task runs now, not TypeError., Recurring tasks continue to use the interval scheduler path., test_add_task_without_run_at_executes_immediately(), test_recurring_task_without_run_at_is_registered()

### Community 38 - "TestPluginType"
Cohesion: 0.40
Nodes (3): _init_body_source(), MCPServerManager must not block on Docker during __init__., test_mcp_manager_init_is_lazy_docker()

### Community 39 - "TestPluginHook"
Cohesion: 0.33
Nodes (4): Tests for PluginType enum., Test plugin type enum values., Test creating PluginType from string., TestPluginType

### Community 40 - "TestVideoInfo"
Cohesion: 0.33
Nodes (4): Tests for PluginHook enum., Test hook descriptions., Test that all expected hooks are defined., TestPluginHook

### Community 41 - "test_preflight_path_creds.py"
Cohesion: 0.33
Nodes (4): Tests for VideoInfo dataclass., Test creating VideoInfo., Test converting VideoInfo to dictionary., TestVideoInfo

### Community 44 - "TestUploadResult"
Cohesion: 0.50
Nodes (3): Tests for AnalysisResult dataclass., Test creating AnalysisResult., TestAnalysisResult

### Community 45 - "test_service_watchdog.py"
Cohesion: 0.50
Nodes (3): Tests for UploadResult dataclass., Test creating UploadResult., TestUploadResult

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestPluginManager` connect `TestPluginManager` to `TestPluginMetadata`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `TestExamplePlugins` connect `TestExamplePlugins` to `TestPluginMetadata`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `TestBasePlugin` connect `TestBasePlugin` to `TestPluginMetadata`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Should `_patch_snapshot_dir` be split into smaller, more focused modules?**
  _Cohesion score 0.0797872340425532 - nodes in this community are weakly interconnected._
- **Should `TestBomQuoteSanitization` be split into smaller, more focused modules?**
  _Cohesion score 0.05853658536585366 - nodes in this community are weakly interconnected._
- **Should `conftest.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06190476190476191 - nodes in this community are weakly interconnected._
- **Should `TestPlanActionRouting` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._