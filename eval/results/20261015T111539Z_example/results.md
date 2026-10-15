# Eval results: example

- date: 2026-10-15T11:15:39+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: c3d283be5b8f, code commit: c0560e10bfea50d53ef7eb25d979c65d19e145d7 (uncommitted changes)
- **passed: 0/5**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_lines_flag | boilerplate | no | done | 5 | 64.69 | 5654/269 | check failed: ...nes.py::test_lines_flag[--lines] - subprocess.CalledProce... FAILED test_check_lines.py::test_lines_flag[-l] - subprocess.CalledProcessErr... FAILED test_check_lines.py::test_help_mentions_option - AssertionError: asser... 3 failed, 2 passed in 1.16s |
| explain_order_sync | explain | no | done | 2 | 21.94 | 2033/60 | check failed: ...FAIL: ANSWER.json was not created |
| fix_mutable_default | debug | no | done | 1 | 37.05 | 843/185 | check failed: ... Use -v to get more diff test_check_cart.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AssertionError: asser... 1 failed, 3 passed in 0.09s |
| print_to_logging | small_edit | no | done | 5 | 50.28 | 6145/232 | check failed: ...======== short test summary info =========================== FAILED test_check_logging.py::test_log_records - NameError: name 'logger' is ... FAILED test_importer.py::test_parse_rows - NameError: name 'logger' is not de... 2 failed, 1 passed in 0.09s |
| test_parse_duration | tests | no | timeout | 0 | 300.35 | None/None | agent timeout: model call timed out |

| class | passed |
|---|---|
| boilerplate | 0/1 |
| debug | 0/1 |
| explain | 0/1 |
| small_edit | 0/1 |
| tests | 0/1 |
