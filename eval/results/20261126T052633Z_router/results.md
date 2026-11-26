# Eval results: router

- date: 2026-11-26T05:26:33+00:00
- agent: ferrule, model: router (digest None)
- config hash: d9d7c181d7e4, code commit: dfd03669f1afb30ba451834186b55dee3c01a694 (uncommitted changes)
- **passed: 0/6**

| task | class | passed | agent status | steps | seconds | tokens in/out | failure |
|---|---|---|---|---|---|---|---|
| add_config_loader | boilerplate | no | provider_error | 0 | 67.69 | 1812/105 | agent provider_error: no usable model for boilerplate (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling dow |
| add_lines_flag | boilerplate | no | provider_error | 0 | 67.12 | 817/48 | agent provider_error: no usable model for boilerplate (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling dow |
| add_version_route | boilerplate | no | provider_error | 0 | 66.47 | None/None | agent provider_error: no usable model for boilerplate (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling dow |
| explain_order_sync | explain | no | provider_error | 0 | 66.39 | None/None | agent provider_error: no usable model for explain (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down af |
| extract_tax_rate | multi_file_refactor | no | provider_error | 0 | 66.41 | None/None | agent provider_error: no usable model for small_edit (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down |
| fix_mutable_default | debug | no | provider_error | 0 | 65.81 | None/None | agent provider_error: no usable model for debug (qwen2.5-coder:1.5b: not installed; qwen2.5-coder:3b: not installed; deepseek-coder:6.7b: no native tool calling; qwen2.5-coder:7b: not installed; qwen2.5-coder:14b: not installed; openai/gpt-oss-120b: groq cooling down afte |

| class | passed |
|---|---|
| boilerplate | 0/3 |
| debug | 0/1 |
| explain | 0/1 |
| multi_file_refactor | 0/1 |
