# Eval results: router

- date: 2026-11-26T04:36:33+00:00
- agent: ferrule, model: router (digest None)
- config hash: d9d7c181d7e4, code commit: dfd03669f1afb30ba451834186b55dee3c01a694 (uncommitted changes)
- **passed: 6/20**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | done | 12 | 139.05 | 16806/598 | check failed: ... ModuleNotFoundError: No module named 'config' =========================== short test summary info =========================== ERROR test_check_config.py !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!! 1 error in 0.61s |
| add_lines_flag | boilerplate | no | done | 12 | 73.39 | 10323/590 | check failed: ...nes.py::test_lines_flag[--lines] - subprocess.CalledProce... FAILED test_check_lines.py::test_lines_flag[-l] - subprocess.CalledProcessErr... FAILED test_check_lines.py::test_help_mentions_option - AssertionError: asser... 3 failed, 2 passed in 0.60s |
| add_version_route | boilerplate | no | done | 5 | 68.77 | 2379/161 | check failed: ...e -v to get more diff test_check_version.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_version.py::test_version_route - AssertionError: assert (40... 1 failed, 3 passed in 0.08s |
| answer_db_config | explain | yes | done | 6 | 9.65 | 5807/426 |  |
| docstring_area | small_edit | yes | done | 6 | 70.37 | 5457/551 |  |
| explain_order_sync | explain | no | done | 3 | 8.11 | 794/52 | check failed: ...FAIL: ANSWER.json was not created |
| extract_tax_rate | multi_file_refactor | no | max_steps | 15 | 197.38 | 18373/1306 | agent max_steps: stopped after 15 steps |
| fix_from_traceback | debug | yes | done | 5 | 9.07 | 5508/386 |  |
| fix_median | debug | yes | done | 5 | 71.05 | 5184/365 |  |
| fix_mutable_default | debug | no | done | 7 | 9.08 | 4337/199 | check failed: ... Use -v to get more diff test_check_cart.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_cart.py::test_new_cart_on_each_call - AssertionError: asser... 1 failed, 3 passed in 0.07s |
| fix_pagination | debug | yes | done | 7 | 71.54 | 7065/417 |  |
| fix_restock_big_module | long_context | yes | done | 8 | 254.65 | 34919/486 |  |
| print_to_logging | small_edit | no | provider_error | 0 | 128.05 | 822/44 | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down |
| remove_unused_function | long_context | no | provider_error | 0 | 66.36 | None/None | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down |
| rename_calc_total | multi_file_refactor | no | provider_error | 0 | 66.9 | 727/53 | agent provider_error: no usable model for multi_file_refactor (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq coo |
| test_parse_duration | tests | no | provider_error | 0 | 66.41 | None/None | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down afte |
| test_slugify | tests | no | provider_error | 0 | 66.42 | None/None | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down afte |
| test_stack | tests | no | provider_error | 0 | 66.42 | None/None | agent provider_error: no usable model for tests (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down afte |
| trace_retry_default | long_context | no | provider_error | 0 | 66.4 | None/None | agent provider_error: no usable model for explain (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down af |
| validate_withdraw | small_edit | no | provider_error | 0 | 66.39 | None/None | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down |

| class | passed |
|---|---|
| boilerplate | 0/3 |
| debug | 3/4 |
| explain | 1/2 |
| long_context | 1/3 |
| multi_file_refactor | 0/2 |
| small_edit | 1/3 |
| tests | 0/3 |
