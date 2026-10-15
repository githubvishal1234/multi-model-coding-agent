# Eval results: example

- date: 2026-10-15T09:19:58+00:00
- agent: ferrule, model: qwen2.5-coder:7b (digest dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364)
- config hash: c3d283be5b8f, code commit: None (uncommitted changes)
- **passed: 2/5**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_version_route | boilerplate | no | done | 1 | 35.77 | 827/122 | check failed: ...e -v to get more diff test_check_version.py:6: AssertionError =========================== short test summary info =========================== FAILED test_check_version.py::test_version_route - AssertionError: assert (40... 1 failed, 3 passed in 0.10s |
| docstring_area | small_edit | yes | done | 3 | 34.28 | 2851/159 |  |
| fix_median | debug | yes | done | 10 | 124.5 | 13346/664 |  |
| rename_calc_total | multi_file_refactor | no | done | 5 | 49.07 | 5135/239 | check failed: ...1bvs7sk\repo\pricing.py) =========================== short test summary info =========================== ERROR test_check_rename.py ERROR test_orders.py !!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!! 2 errors in 0.32s |
| test_slugify | tests | no | max_steps | 15 | 129.62 | 25709/637 | agent max_steps: stopped after 15 steps |

| class | passed |
|---|---|
| boilerplate | 0/1 |
| debug | 1/1 |
| multi_file_refactor | 0/1 |
| small_edit | 1/1 |
| tests | 0/1 |
