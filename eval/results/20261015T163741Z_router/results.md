# Eval results: router

- date: 2026-10-15T16:37:41+00:00
- agent: ferrule, model: router (digest None)
- config hash: d9d7c181d7e4, code commit: 50fd14405aa0a7ef9ecb1e89f8b665364ef719f8
- **passed: 4/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | done | 4 | 91.99 | 4536/360 | check failed: ...==================== short test summary info =========================== ERROR test_check_config.py - ValueError: mutable default <class 'list'> for f... !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!! 1 error in 0.22s |
| add_lines_flag | boilerplate | no | done | 5 | 64.96 | 5440/306 | check failed: ...nes.py::test_lines_flag[--lines] - subprocess.CalledProce... FAILED test_check_lines.py::test_lines_flag[-l] - subprocess.CalledProcessErr... FAILED test_check_lines.py::test_help_mentions_option - AssertionError: asser... 3 failed, 2 passed in 0.70s |
| add_version_route | boilerplate | yes | done | 5 | 61.09 | 5255/266 |  |
| answer_db_config | explain | no | done | 4 | 53.43 | 3546/242 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | provider_error | 0 | 57.0 | 6249/241 |  |
| explain_order_sync | explain | yes | done | 5 | 43.03 | 5613/164 |  |
| extract_tax_rate | multi_file_refactor | no | provider_error | 0 | 109.16 | 18284/446 | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: already tried; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: no API key (G |
| fix_from_traceback | debug | no | done | 4 | 45.63 | 4080/180 | check failed: ...======== short test summary info =========================== FAILED test_check_empty_day.py::test_empty_day_report - ZeroDivisionError: di... FAILED test_check_empty_day.py::test_root_cause_fixed_in_metrics - ZeroDivisi... 2 failed, 3 passed in 0.09s |
| fix_median | debug | no | provider_error | 0 | 57.34 | 7325/177 | agent provider_error: no usable model for debug (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: already tried; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: no API key (GROQ_A |
| fix_mutable_default | debug | no | provider_error | 0 | 1.83 | None/None | agent provider_error: no usable model for debug (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| fix_pagination | debug | no | provider_error | 0 | 1.5 | None/None | agent provider_error: no usable model for debug (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| fix_restock_big_module | long_context | no | provider_error | 0 | 1.29 | None/None | agent provider_error: no usable model for debug (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| print_to_logging | small_edit | yes | provider_error | 0 | 15.49 | 2316/297 |  |
| remove_unused_function | long_context | no | provider_error | 0 | 4.46 | 1022/89 | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versati |
| rename_calc_total | multi_file_refactor | no | provider_error | 0 | 1.3 | None/None | agent provider_error: no usable model for multi_file_refactor (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70 |
| test_parse_duration | tests | no | provider_error | 0 | 1.17 | None/None | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| test_slugify | tests | no | provider_error | 0 | 7.2 | 1017/64 | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| test_stack | tests | no | provider_error | 0 | 1.85 | None/None | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: n |
| trace_retry_default | long_context | no | provider_error | 0 | 1.1 | None/None | agent provider_error: no usable model for explain (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versatile: |
| validate_withdraw | small_edit | no | provider_error | 0 | 1.16 | None/None | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: does not fit the memory budget; qwen2.5-coder:14b: not installed; llama-3.3-70b-versati |

| class | passed |
|---|---|
| boilerplate | 1/3 |
| debug | 0/4 |
| explain | 1/2 |
| long_context | 0/3 |
| multi_file_refactor | 0/2 |
| small_edit | 2/3 |
| tests | 0/3 |
