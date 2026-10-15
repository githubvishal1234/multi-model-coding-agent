# Eval results: example

- date: 2026-10-15T11:58:07+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: c3d283be5b8f, code commit: c0560e10bfea50d53ef7eb25d979c65d19e145d7 (uncommitted changes)
- **passed: 5/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | max_steps | 15 | 401.49 | 39325/1260 | agent max_steps: stopped after 15 steps |
| add_lines_flag | boilerplate | no | done | 7 | 71.11 | 8825/330 | check failed: ...nes.py::test_lines_flag[--lines] - subprocess.CalledProce... FAILED test_check_lines.py::test_lines_flag[-l] - subprocess.CalledProcessErr... FAILED test_check_lines.py::test_help_mentions_option - AssertionError: asser... 3 failed, 2 passed in 0.83s |
| add_version_route | boilerplate | no | done | 3 | 37.79 | 2895/166 | check failed: ...e -v to get more diff test_check_version.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_version.py::test_version_route - AssertionError: assert (40... 1 failed, 3 passed in 0.12s |
| answer_db_config | explain | no | done | 6 | 141.21 | 7490/810 | check failed: ...FAIL: ANSWER.md does not mention load_database_url |
| docstring_area | small_edit | yes | done | 5 | 68.38 | 5302/389 |  |
| explain_order_sync | explain | no | done | 3 | 29.79 | 3277/98 | check failed: ...FAIL: ANSWER.json was not created |
| extract_tax_rate | multi_file_refactor | no | done | 13 | 101.2 | 18362/439 | check failed: ...x_rate.py::test_no_hardcoded_rate_left - AssertionError: ... FAILED test_check_tax_rate.py::test_behaviour_unchanged - NameError: name 'TA... FAILED test_check_tax_rate.py::test_all_modules_follow_the_constant - NameErr... 6 failed, 1 passed in 0.11s |
| fix_from_traceback | debug | yes | done | 5 | 81.05 | 6263/417 |  |
| fix_median | debug | yes | done | 10 | 121.23 | 13326/667 |  |
| fix_mutable_default | debug | no | done | 2 | 63.26 | 1930/324 | check failed: ... Use -v to get more diff test_check_cart.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AssertionError: asser... 1 failed, 3 passed in 0.10s |
| fix_pagination | debug | no | max_steps | 15 | 189.19 | 25737/1074 | agent max_steps: stopped after 15 steps |
| fix_restock_big_module | long_context | yes | done | 7 | 50.56 | 7699/243 |  |
| print_to_logging | small_edit | no | max_steps | 15 | 177.6 | 35815/552 | agent max_steps: stopped after 15 steps |
| remove_unused_function | long_context | no | done | 4 | 37.89 | 3786/182 | check failed: ...in items), 2)}', ...} test_check_unused.py:14: AssertionError =========================== short test summary info =========================== FAILED test_check_unused.py::test_exactly_the_unused_function_was_removed - A... 1 failed, 2 passed in 0.20s |
| rename_calc_total | multi_file_refactor | no | max_steps | 15 | 166.31 | 28357/857 | agent max_steps: stopped after 15 steps |
| test_parse_duration | tests | no | timeout | 0 | 301.45 | None/None | agent timeout: model call timed out |
| test_slugify | tests | no | max_steps | 15 | 141.45 | 25961/679 | agent max_steps: stopped after 15 steps |
| test_stack | tests | no | done | 4 | 73.73 | 4471/382 | check failed: ...FAIL: the tests did not catch a Stack that miscounts len after pops |
| trace_retry_default | long_context | no | invalid_output | 7 | 44.52 | 7887/208 | agent invalid_output: invalid tool call: invalid arguments for edit_file: old: String should have at least 1 character |
| validate_withdraw | small_edit | yes | done | 4 | 38.92 | 4006/179 |  |

| class | passed |
|---|---|
| boilerplate | 0/3 |
| debug | 2/4 |
| explain | 0/2 |
| long_context | 1/3 |
| multi_file_refactor | 0/2 |
| small_edit | 2/3 |
| tests | 0/3 |
