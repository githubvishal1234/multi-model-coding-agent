# Eval results: example

- date: 2026-10-15T10:59:19+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: c3d283be5b8f, code commit: c0560e10bfea50d53ef7eb25d979c65d19e145d7
- **passed: 5/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | max_steps | 15 | 377.9 | 38535/1439 | agent max_steps: stopped after 15 steps |
| add_lines_flag | boilerplate | no | max_steps | 15 | 128.09 | 31237/580 | agent max_steps: stopped after 15 steps |
| add_version_route | boilerplate | no | max_steps | 15 | 116.26 | 25039/645 | agent max_steps: stopped after 15 steps |
| answer_db_config | explain | no | done | 6 | 131.4 | 7556/824 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | done | 3 | 33.19 | 2848/159 |  |
| explain_order_sync | explain | no | done | 2 | 22.39 | 2041/68 | check failed: ...FAIL: ANSWER.json was not created |
| extract_tax_rate | multi_file_refactor | no | done | 13 | 83.47 | 17825/460 | check failed: ...x_rate.py::test_no_hardcoded_rate_left - AssertionError: ... FAILED test_check_tax_rate.py::test_behaviour_unchanged - NameError: name 'TA... FAILED test_check_tax_rate.py::test_all_modules_follow_the_constant - NameErr... 6 failed, 1 passed in 0.14s |
| fix_from_traceback | debug | yes | done | 5 | 81.2 | 6264/469 |  |
| fix_median | debug | no | max_steps | 15 | 184.21 | 23122/1078 | agent max_steps: stopped after 15 steps |
| fix_mutable_default | debug | no | done | 1 | 36.38 | 841/185 | check failed: ... Use -v to get more diff test_check_cart.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AssertionError: asser... 1 failed, 3 passed in 0.09s |
| fix_pagination | debug | yes | done | 8 | 90.2 | 10208/527 |  |
| fix_restock_big_module | long_context | yes | done | 7 | 47.89 | 7685/241 |  |
| print_to_logging | small_edit | no | done | 5 | 48.39 | 6140/232 | check failed: ...======== short test summary info =========================== FAILED test_check_logging.py::test_log_records - NameError: name 'logger' is ... FAILED test_importer.py::test_parse_rows - NameError: name 'logger' is not de... 2 failed, 1 passed in 0.10s |
| remove_unused_function | long_context | no | done | 2 | 21.35 | 1726/86 | check failed: ...in items), 2)}', ...} test_check_unused.py:14: AssertionError =========================== short test summary info =========================== FAILED test_check_unused.py::test_exactly_the_unused_function_was_removed - A... 1 failed, 2 passed in 0.14s |
| rename_calc_total | multi_file_refactor | no | done | 3 | 24.65 | 2632/104 | check failed: ...======== short test summary info =========================== FAILED test_check_rename.py::test_renamed_without_alias - AssertionError: ass... FAILED test_check_rename.py::test_old_name_gone_everywhere - AssertionError: ... 2 failed, 3 passed in 0.09s |
| test_parse_duration | tests | no | timeout | 0 | 300.18 | None/None | agent timeout: model call timed out |
| test_slugify | tests | no | max_steps | 15 | 122.03 | 25934/665 | agent max_steps: stopped after 15 steps |
| test_stack | tests | no | done | 2 | 58.0 | 1971/323 | check failed: ...FAIL: the tests did not catch a Stack that miscounts len after pops |
| trace_retry_default | long_context | no | done | 4 | 24.18 | 3984/83 | check failed: ...FAIL: ANSWER.txt was not created |
| validate_withdraw | small_edit | yes | done | 4 | 35.54 | 3998/172 |  |

| class | passed |
|---|---|
| boilerplate | 0/3 |
| debug | 2/4 |
| explain | 0/2 |
| long_context | 1/3 |
| multi_file_refactor | 0/2 |
| small_edit | 2/3 |
| tests | 0/3 |
