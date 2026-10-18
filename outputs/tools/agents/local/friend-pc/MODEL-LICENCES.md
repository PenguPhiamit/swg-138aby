# Licences of the models the installer downloads

Checked by Claude on 17 Oct 2026, before the owner's OK to pull them on the friend's PC (AGENTS.md, Ethics check 1:
honour licences). We run the weights privately and never redistribute them. Model output is used only as drafts that
Claude or ChatGPT checks.

| Model (Ollama tag) | Maker | Licence | Where it says so |
|---|---|---|---|
| `qwen3.6:35b-a3b` | Qwen (Alibaba) | Apache 2.0 | https://huggingface.co/Qwen/Qwen3.6-35B-A3B (read for Documentation-support/ollama-model-options.md, 15 Oct; the Qwen3.6-27B card read 17 Oct also says Apache-2.0) |
| `qwen3.5:9b` | Qwen (Alibaba) | Apache 2.0 | https://huggingface.co/Qwen/Qwen3.5-9B (Documentation-support/ollama-model-options.md, 15 Oct) |
| `qwen3:8b` | Qwen (Alibaba) | Apache 2.0 | https://huggingface.co/Qwen/Qwen3-8B |
| `gpt-oss:20b`, and `gpt-oss-20b-64k` built from it | OpenAI | Apache 2.0 | https://huggingface.co/openai/gpt-oss-20b |
| `hf.co/hiwaifu-research/WaifuGemma4-26b-a4b-v1-i1-GGUF:IQ4_XS` (WaifuGemma4 26B-A4B v1, imatrix IQ4_XS, 13.9 GB) | hiwaifu-research, a role-play fine-tune of Google's Gemma 4 26B-A4B-it | Apache 2.0, "as inherited from the base model" | https://huggingface.co/hiwaifu-research/WaifuGemma4-26b-a4b-v1-i1-GGUF (read 17 Oct; licence field `apache-2.0`; not gated) |
| `gemma4:12b` | Google | Apache 2.0 | https://huggingface.co/google/gemma-4-12b (licence field `apache-2.0`) and https://ai.google.dev/gemma/docs/gemma_4_license (the "Gemma 4 license" page, last updated 2026-04-01, is the Apache License 2.0) |
| `saluki` (Underdog Saluki 27B 1.0, IQ2 mix, 7.9 GB, plus its Q8_0 vision projector, 0.63 GB; on both PCs since 18 Oct, the projector on Miniverse only) | ConwayResearch, from ISTA-DASLab's Qwen3.8-27B GSQ quant | Apache 2.0 | https://huggingface.co/ConwayResearch/Underdog-Saluki-27B-1.0 (read 18 Oct through the Hub API: licence `apache-2.0`, LICENSE and NOTICE files; sha256 of both files checked against the Hub) |

## Gemma (the options doc said to read its terms first)

- **Gemma 4 is Apache 2.0.** The older **Gemma Terms of Use** (https://ai.google.dev/gemma/terms, last modified
  1 April 2026) cover Gemma 1, 1.1, 2, 3 and 3n and their variants. They do not list Gemma 4, and they point to the
  Gemma 4 licence instead.
- Google's legal menu also lists a **Prohibited Use Policy** and an intended-use statement next to the Gemma 4 licence.
  The pages read do not say whether they bind Gemma 4 on top of Apache 2.0. Drafting NPC chat lines and proofreading
  for a private game server is far from anything such a policy targets, and we follow it anyway.
- **What Apache 2.0 asks:** keep the licence and notices **if we redistribute** the weights or a modified copy. We
  don't: the weights stay on the friend's PC, and `ollama-url.txt` points at them over the home network. The licence
  sets no conditions on output. The older Gemma terms also say Google "claims no rights in Outputs".

## WaifuGemma4 (owner's OK, 17 Oct, after reading its card; the friend knows)

- Its card: a role-play model trained on arena votes. "No safety tuning beyond base Gemma 4; 18+ use only." Mature
  content "follows your system prompt", so every job that uses it sets the content rules in its system prompt (game
  text for a private server, no explicit content).
- Settings from the card: non-thinking (reasoning budget 0, which is `think: false` in Ollama), trained on 8K-token
  chats, so topics give it `"ctx": 8192`; temperature 0.8-1.0; replies run 400-500 tokens unless the prompt asks
  for less.
- Its only job is drafting role-play and NPC dialogue. It never checks anything, and Claude or ChatGPT reviews every
  line before it goes into the game.

## gpt-oss-20b-64k

`gpt-oss-20b-64k` is built from gpt-oss:20b with a two-line Modelfile (`FROM gpt-oss:20b`, `PARAMETER num_ctx 65536`).
That is a configuration change on the same weights: no new file and nothing redistributed.
