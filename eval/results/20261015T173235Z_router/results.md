# Eval results: router

- date: 2026-10-15T17:32:35+00:00
- agent: ferrule, model: router (digest None)
- config hash: d9d7c181d7e4, code commit: 50fd14405aa0a7ef9ecb1e89f8b665364ef719f8 (uncommitted changes)
- **passed: 5/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | done | 4 | 77.52 | 4548/358 | check failed: ...==================== short test summary info =========================== ERROR test_check_config.py - ValueError: mutable default <class 'list'> for f... !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!! 1 error in 0.19s |
| add_lines_flag | boilerplate | no | timeout | 0 | 567.72 | 18346/532 | agent timeout: model call timed out |
| add_version_route | boilerplate | yes | done | 5 | 61.16 | 5260/266 |  |
| answer_db_config | explain | no | done | 4 | 53.57 | 3595/269 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | done | 7 | 54.52 | 8007/285 |  |
| explain_order_sync | explain | yes | done | 5 | 40.31 | 5613/162 |  |
| extract_tax_rate | multi_file_refactor | no | timeout | 0 | 436.67 | 19883/645 | agent timeout: model call timed out |
| fix_from_traceback | debug | no | done | 4 | 45.81 | 4084/180 | check failed: ...======== short test summary info =========================== FAILED test_check_empty_day.py::test_empty_day_report - ZeroDivisionError: di... FAILED test_check_empty_day.py::test_root_cause_fixed_in_metrics - ZeroDivisi... 2 failed, 3 passed in 0.08s |
| fix_median | debug | no | timeout | 0 | 475.76 | 9600/200 | agent timeout: model call timed out |
| fix_mutable_default | debug | no | done | 3 | 32.77 | 2663/82 | check failed: ...e' object has no attribute 'append' cart.py:3: AttributeError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AttributeError: 'None... 1 failed, 3 passed in 0.08s |
| fix_pagination | debug | yes | done | 4 | 35.42 | 3915/132 |  |
| fix_restock_big_module | long_context | no | max_steps | 15 | 95.1 | 17199/442 | agent max_steps: stopped after 15 steps |
| print_to_logging | small_edit | no | done | 6 | 48.49 | 6225/213 | check failed: ...======== short test summary info =========================== FAILED test_check_logging.py::test_log_records - AssertionError: assert [] ==... FAILED test_check_logging.py::test_no_print_and_no_logging_config - Assertion... 2 failed, 1 passed in 0.08s |
| remove_unused_function | long_context | no | done | 5 | 26.47 | 4343/91 | check failed: ...in items), 2)}', ...} test_check_unused.py:14: AssertionError =========================== short test summary info =========================== FAILED test_check_unused.py::test_exactly_the_unused_function_was_removed - A... 1 failed, 2 passed in 0.13s |
| rename_calc_total | multi_file_refactor | no | done | 6 | 65.36 | 6537/332 | check failed: ...======== short test summary info =========================== FAILED test_check_rename.py::test_renamed_without_alias - AssertionError: ass... FAILED test_check_rename.py::test_old_name_gone_everywhere - AssertionError: ... 2 failed, 3 passed in 0.08s |
| test_parse_duration | tests | no | timeout | 0 | 300.41 | None/None | agent timeout: model call timed out |
| test_slugify | tests | no | done | 6 | 99.85 | 7554/482 | check failed: ...FAIL: need at least two test functions |
| test_stack | tests | no | done | 2 | 110.15 | 1878/550 | check failed: ...FAIL: test_stack.py was not created |
| trace_retry_default | long_context | no | done | 5 | 35.07 | 4751/143 | check failed: ...FAIL: expected 4 as the first number in ANSWER.txt, got ['10'] |
| validate_withdraw | small_edit | yes | done | 4 | 34.71 | 3770/142 |  |

| class | passed |
|---|---|
| boilerplate | 1/3 |
| debug | 1/4 |
| explain | 1/2 |
| long_context | 0/3 |
| multi_file_refactor | 0/2 |
| small_edit | 2/3 |
| tests | 0/3 |
