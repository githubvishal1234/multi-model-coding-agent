# Eval results: native

- date: 2026-10-15T15:28:46+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: b94ccfa767c9, code commit: c0560e10bfea50d53ef7eb25d979c65d19e145d7 (uncommitted changes)
- **passed: 6/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | done | 4 | 60.62 | 4550/361 | check failed: ...==================== short test summary info =========================== ERROR test_check_config.py - ValueError: mutable default <class 'list'> for f... !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!! 1 error in 0.20s |
| add_lines_flag | boilerplate | no | max_steps | 15 | 196.67 | 38668/750 | agent max_steps: stopped after 15 steps |
| add_version_route | boilerplate | yes | done | 5 | 46.65 | 5255/266 |  |
| answer_db_config | explain | no | done | 4 | 32.17 | 3550/155 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | done | 7 | 53.74 | 7551/284 |  |
| explain_order_sync | explain | yes | done | 5 | 37.37 | 5613/162 |  |
| extract_tax_rate | multi_file_refactor | no | max_steps | 15 | 119.43 | 24419/571 | agent max_steps: stopped after 15 steps |
| fix_from_traceback | debug | no | done | 4 | 37.6 | 4080/180 | check failed: ...======== short test summary info =========================== FAILED test_check_empty_day.py::test_empty_day_report - ZeroDivisionError: di... FAILED test_check_empty_day.py::test_root_cause_fixed_in_metrics - ZeroDivisi... 2 failed, 3 passed in 0.10s |
| fix_median | debug | yes | done | 12 | 78.84 | 17376/338 |  |
| fix_mutable_default | debug | no | done | 3 | 22.41 | 2669/82 | check failed: ...e' object has no attribute 'append' cart.py:3: AttributeError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AttributeError: 'None... 1 failed, 3 passed in 0.08s |
| fix_pagination | debug | yes | done | 4 | 31.21 | 3919/132 |  |
| fix_restock_big_module | long_context | no | max_steps | 15 | 86.8 | 17169/442 | agent max_steps: stopped after 15 steps |
| print_to_logging | small_edit | no | done | 6 | 45.2 | 6231/213 | check failed: ...======== short test summary info =========================== FAILED test_check_logging.py::test_log_records - AssertionError: assert [] ==... FAILED test_check_logging.py::test_no_print_and_no_logging_config - Assertion... 2 failed, 1 passed in 0.09s |
| remove_unused_function | long_context | no | done | 5 | 26.41 | 4347/101 | check failed: ...in items), 2)}', ...} test_check_unused.py:14: AssertionError =========================== short test summary info =========================== FAILED test_check_unused.py::test_exactly_the_unused_function_was_removed - A... 1 failed, 2 passed in 0.13s |
| rename_calc_total | multi_file_refactor | no | done | 6 | 58.56 | 6549/332 | check failed: ...======== short test summary info =========================== FAILED test_check_rename.py::test_renamed_without_alias - AssertionError: ass... FAILED test_check_rename.py::test_old_name_gone_everywhere - AssertionError: ... 2 failed, 3 passed in 0.10s |
| test_parse_duration | tests | no | timeout | 0 | 300.2 | None/None | agent timeout: model call timed out |
| test_slugify | tests | no | max_steps | 15 | 138.95 | 26807/809 | agent max_steps: stopped after 15 steps |
| test_stack | tests | no | done | 2 | 90.96 | 1880/550 | check failed: ...FAIL: test_stack.py was not created |
| trace_retry_default | long_context | no | done | 5 | 35.09 | 4751/144 | check failed: ...FAIL: expected 4 as the first number in ANSWER.txt, got ['10'] |
| validate_withdraw | small_edit | yes | done | 4 | 29.83 | 3762/142 |  |

| class | passed |
|---|---|
| boilerplate | 1/3 |
| debug | 2/4 |
| explain | 1/2 |
| long_context | 0/3 |
| multi_file_refactor | 0/2 |
| small_edit | 2/3 |
| tests | 0/3 |
