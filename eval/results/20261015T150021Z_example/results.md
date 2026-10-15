# Eval results: example

- date: 2026-10-15T15:00:21+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: c3d283be5b8f, code commit: c0560e10bfea50d53ef7eb25d979c65d19e145d7 (uncommitted changes)
- **passed: 5/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | done | 4 | 79.72 | 5388/379 | check failed: ...==================== short test summary info =========================== ERROR test_check_config.py - ValueError: mutable default <class 'list'> for f... !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!! 1 error in 0.41s |
| add_lines_flag | boilerplate | no | max_steps | 15 | 211.93 | 39755/778 | agent max_steps: stopped after 15 steps |
| add_version_route | boilerplate | no | max_steps | 15 | 136.91 | 28240/774 | agent max_steps: stopped after 15 steps |
| answer_db_config | explain | no | done | 6 | 96.72 | 7796/592 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | done | 4 | 68.95 | 4758/396 |  |
| explain_order_sync | explain | no | done | 3 | 31.79 | 3712/119 | check failed: ...FAIL: ANSWER.json was not created |
| extract_tax_rate | multi_file_refactor | no | done | 6 | 159.88 | 10342/1029 | check failed: ...======== short test summary info =========================== FAILED test_check_tax_rate.py::test_no_hardcoded_rate_left - AssertionError: ... FAILED test_check_tax_rate.py::test_all_modules_follow_the_constant - assert ... 2 failed, 5 passed in 0.10s |
| fix_from_traceback | debug | no | invalid_output | 5 | 204.31 | 9243/1281 | agent invalid_output: invalid tool call: tool call block is not valid JSON. Use valid JSON: double-quoted strings, newlines written as \n, inner double quotes escaped as \". Got: {"tool": "edit_file", "args": {"path": "metrics.py", "old": "return round(total / len(orders) |
| fix_median | debug | no | max_steps | 15 | 198.86 | 28305/1183 | agent max_steps: stopped after 15 steps |
| fix_mutable_default | debug | yes | done | 4 | 58.85 | 4988/336 |  |
| fix_pagination | debug | yes | done | 4 | 48.02 | 4901/243 |  |
| fix_restock_big_module | long_context | no | done | 8 | 197.02 | 20567/288 | check failed: ...stock.py::test_restock_new_sku_and_validation - Assertion... FAILED test_inventory.py::test_restock_new_sku - AssertionError: assert {'A1'... FAILED test_inventory.py::test_restock_existing_sku - AssertionError: assert ... 4 failed, 4 passed in 0.20s |
| print_to_logging | small_edit | no | max_steps | 15 | 300.69 | 34952/1547 | agent max_steps: stopped after 15 steps |
| remove_unused_function | long_context | no | done | 3 | 31.6 | 3139/124 | check failed: ...in items), 2)}', ...} test_check_unused.py:14: AssertionError =========================== short test summary info =========================== FAILED test_check_unused.py::test_exactly_the_unused_function_was_removed - A... 1 failed, 2 passed in 0.18s |
| rename_calc_total | multi_file_refactor | yes | done | 14 | 154.32 | 26770/734 |  |
| test_parse_duration | tests | no | timeout | 0 | 300.24 | None/None | agent timeout: model call timed out |
| test_slugify | tests | no | max_steps | 15 | 286.4 | 33638/1589 | agent max_steps: stopped after 15 steps |
| test_stack | tests | no | done | 3 | 68.64 | 3566/366 | check failed: ...FAIL: the tests did not catch a Stack that returns None when peeking empty |
| trace_retry_default | long_context | no | done | 5 | 43.47 | 5768/190 | check failed: ...FAIL: expected 4 as the first number in ANSWER.txt, got ['5'] |
| validate_withdraw | small_edit | yes | done | 4 | 42.61 | 4631/200 |  |

| class | passed |
|---|---|
| boilerplate | 0/3 |
| debug | 2/4 |
| explain | 0/2 |
| long_context | 0/3 |
| multi_file_refactor | 1/2 |
| small_edit | 2/3 |
| tests | 0/3 |
