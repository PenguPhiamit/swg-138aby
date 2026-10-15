# Ollama model options for the idle research (15 Oct 2026)

Research only. Nothing was pulled, downloaded, installed or changed, and no model was loaded. Figures are the vendors' own (Ollama library pages and Hugging Face model cards) unless marked **est.**, which is arithmetic from their config files. Written by Claude (Haiku 5.5) at the owner's request: "maybe swap ollama's model? maybe see if haiku can find something better across the nets".

## Recommendation

**Switch to `qwen3.5:9b` with a 32,768-token window, after the short test in section 5. Keep `qwen3:8b` installed as the fallback.**

- **Fits the 12 GB card entirely on the GPU** at 32K, and by estimate at 64K (est. 9–11 GB of about 11 GB free). No CPU split, so less pressure on the 32 GB of RAM that ran out on 15 Oct.
- **Smaller memory growth per request.** Its KV cache is 32 KB per token against 144 KB for `qwen3:8b` (section 2). The prompt-cache growth that [memguard.py](../tools/agents/local/memguard.py) guards against should be about a quarter of today's (est.: about 0.13 GB per 4K-token request, against about 0.5 GB per request recorded for `qwen3:8b` in [memguard.py](../tools/agents/local/memguard.py)).
- **Tool use has the best-documented numbers of the candidates that fit.** The card says it "excels in tool calling" and reports BFCL-V4 66.1 and TAU2-Bench 79.1 (vendor numbers). Apache 2.0.
- **Twice the source per topic.** `source_cap()` in [idle_research.py](../tools/agents/local/idle_research.py) gives 30,000 characters at 16K (today), 60,000 at 32K, 120,000 at 64K.

**Not yet established:** no benchmark compares it with `qwen3:8b` on our tasks, and speed is unmeasured. The test in section 5 settles both. If it fails, `gemma4:12b` is the next choice. If neither beats `qwen3:8b`, keep the current model.

## 1. What runs now

| Setting | Value | Where |
|---|---|---|
| Model | `qwen3:8b` (5.2 GB on disk) | [ollama-model.txt](../tools/agents/local/ollama-model.txt) |
| Context window | 16,384 tokens | [ollama-ctx.txt](../tools/agents/local/ollama-ctx.txt) |
| Server | this PC, `127.0.0.1:11434` (no `ollama-url.txt`) | [ollama_url.py](../tools/agents/local/ollama_url.py) |
| Code defaults | `gpt-oss:20b`, 65,536 tokens; used only if the two files are missing | [ollama_url.py:25-26](../tools/agents/local/ollama_url.py) |

- The Modelfile [Modelfile.gpt-oss-20b-64k](../tools/agents/local/Modelfile.gpt-oss-20b-64k) (14 Oct) and the `gpt-oss:20b` defaults describe an older setup. The two text files override them, so `gpt-oss:20b` is not what runs now. It is still installed (13 GB).
- **Idle research** ([idle_research.py](../tools/agents/local/idle_research.py)): each topic copies up to `source_cap(ctx)` characters of Core3 source and project files, then [local_agent.py](../tools/agents/local/local_agent.py) runs a tool loop (list, read, write inside one folder) and writes `report.md`. Needs **tool calling** and enough window for source.
- **Chunk jobs** ([local_map.py](../tools/agents/local/local_map.py)): one chunk per request, `format: json`, `temperature 0`, `think: false`, `num_predict 1536`. Needs **reliable JSON output**; each request is short.
- **Hardware** (checked 15 Oct): RTX 5070, 12,227 MiB total, 1,398 MiB in use at the check (so about 11 GB free for a model); Ryzen 5 5600X; 32 GB RAM. `ollama --version` reports **0.40.4**. [memguard.py](../tools/agents/local/memguard.py) keeps 6 GB of commit headroom and idle research needs 8 GB to start a topic.
- **Installed** (`ollama list`): `qwen3:8b` 5.2 GB, `gpt-oss:20b` 13 GB. `ollama ps`: nothing loaded.

## 2. Memory arithmetic (est.)

KV cache per token at Ollama's default f16 = 2 × (layers with a full KV cache) × (KV heads) × (head dim) × 2 bytes. Layer counts and head sizes come from each model's `config.json` (sources in section 7). Sliding-window layers stop growing at their window; linear-attention layers keep a fixed-size state, which I assume is small.

| Model | Layers with full KV cache | KV heads × head dim | KV per token | KV at 32K | KV at 64K |
|---|---|---|---|---|---|
| `qwen3:8b` (today) | 36 of 36 | 8 × 128 | 144 KB | 4.8 GB | 9.7 GB |
| `qwen3.5:9b` | 8 of 32 (rest linear, fixed) | 4 × 256 | 32 KB | 1.1 GB | 2.1 GB |
| `gemma4:12b` | 8 of 48 global (rest 1,024-token sliding window) | global 1 × 512; sliding 8 × 256 | 16 KB + ~0.34 GB fixed | 0.9 GB | 1.4 GB |
| `gpt-oss:20b` | 12 of 24 (rest 128-token sliding window) | 8 × 64 | 24 KB | 0.8 GB | 1.6 GB |
| `qwen3.6:35b` (3B active) | 10 of 40 (rest linear, fixed) | 2 × 256 | 20 KB | 0.7 GB | 1.3 GB |

Total VRAM (est.) = weights from the Ollama library + KV cache + about 1 GB for compute buffers (an assumption).

| Model and window | Weights on disk | Est. total VRAM | Fit on this card (about 11 GB free) |
|---|---|---|---|
| `qwen3:8b` at 16K (today) | 5.2 GB | ~8.6 GB | fits |
| `qwen3:8b` at 32K | 5.2 GB | ~11 GB | borderline |
| `qwen3:8b` at 64K | 5.2 GB | ~16 GB | no: ~5 GB runs on CPU |
| `qwen3.5:9b` at 32K | 6.6–7.6 GB | 8.7–9.7 GB | fits |
| `qwen3.5:9b` at 64K | 6.6–7.6 GB | 9.7–10.7 GB | fits, tight |
| `gemma4:12b` at 32K | 7.7–8.0 GB | 9.6–9.9 GB | fits (vision and audio encoders not counted) |
| `gemma4:12b` at 64K | 7.7–8.0 GB | 10.1–10.4 GB | fits, tight |
| `gpt-oss:20b` at 32K / 64K | 13–14 GB | ~15 / ~16 GB | no: ~4–5 GB runs on CPU |
| `qwen3.6:35b` at 32K / 64K | 23–24 GB | ~25 / ~26 GB | no: ~14 GB in system RAM |

**Two checks on these numbers.**
- The `gemma4:12b` row assumes Ollama keeps the sliding-window layers to their 1,024-token window. If it allocates them at full length, the same formula gives ~10.7 GB of KV at 32K and the model would not fit. The first load will show which it is.
- Run `ollama ps` after the first load. Its PROCESSOR column gives the real GPU/CPU split, which replaces these estimates.

## 3. Candidates

Sizes and tags are from the Ollama library pages. Licence, context and tool calling are from the model cards. Benchmark numbers are vendor-reported, each with its own harness and version, so compare within a row rather than across rows. None was measured here.

| Model (Ollama tag) | Size on disk | Native context | Licence | Tool calling | Vendor-reported coding and agent numbers | Fit on this PC |
|---|---|---|---|---|---|---|
| **`qwen3.5:9b`** (dense, text and image) | 6.6–7.6 GB | 256K | Apache 2.0 | Card: "excels in tool calling"; Ollama tag: tools | LiveCodeBench v6 65.6; BFCL-V4 66.1; TAU2-Bench 79.1. No SWE-bench on the card. | Fits fully at 32K–64K (est.) |
| **`gemma4:12b`** (text, image, audio) | 7.7–8.0 GB | 256K | Apache 2.0 (card links Gemma's terms; read them before use) | Card: "Native support for structured tool use"; Ollama tag: tools | LiveCodeBench v6 72.0%; Codeforces 1659; Tau2 69.0%. No SWE-bench or BFCL on the card. | Fits; tight at 64K |
| **`qwen3.6:35b`** (MoE, 35B total, 3B active) | 23–24 GB | 256K | Apache 2.0 | Card: tool calling supported; Ollama tag: tools | SWE-bench Verified 73.4; SWE-bench Pro 49.5; Terminal-Bench 2.0 51.5; LiveCodeBench v6 80.4; TAU3-Bench 67.2 | Does not fit the card; ~14 GB in RAM. Needs a memory test first. |
| **`gpt-oss:20b`** (MoE, 21B total, 3.6B active; installed) | 13–14 GB | 128K | Apache 2.0 | Card: function calling with defined schemas; Ollama tag: tools | No coding-agent number on the card (MMLU-Pro 73.6; GPQA Diamond 58.59) | Splits between GPU and CPU at any window above 16K |
| **`devstral-small-2:24b`** (dense) | about 13–14 GB (third-party; not read from the library page) | 256K | Apache 2.0 | Card: tool calling supported; Ollama tag: tools | SWE-bench Verified 68.0%; SWE-bench Multilingual 55.7%; Terminal-Bench 2 22.5% | Dense, so every token touches all the weights and most run on CPU. Not for unattended runs here. |
| *Current:* `qwen3:8b` | 5.2 GB | 32K (card); config max 40,960; 131K with YaRN | Apache 2.0 | Card: tool calling supported | Not in the fetched card text | Fits at 16K; borderline at 32K |

## 4. Why this order

- **`qwen3.5:9b` over `gemma4:12b`.** They are close. `gemma4:12b` has the higher LiveCodeBench (72.0 against 65.6). `qwen3.5:9b` has the stronger tool-use evidence (TAU2 79.1 against 69.0, and a BFCL figure that `gemma4:12b`'s card doesn't give), and it leaves more room at 64K. `local_agent.py` leans on tool calls, so `qwen3.5:9b` goes first.
- **`qwen3.6:35b` is not for now.** It has the best coding numbers in the table, but 23–24 GB will not stay on a 12 GB card. On this PC that means ~14 GB in RAM on 32 GB, the SWG client running, and the 15 Oct crash. Revisit it only after a memory test, or on a machine with more RAM.
- **`gpt-oss:20b` is not better on the numbers we have.** It is the code default and already installed, and it runs partly on CPU at any window above 16K. Keep it installed for now; deleting it is an owner decision.
- **`devstral-small-2:24b`** has a good tool number, but as a dense 24B it would be slow here (speed not measured).
- **`qwen3:8b`** stays as the fallback. Its 16K window is what limits source, and it fits 32K only borderline.

## 5. Steps the owner would approve (none done)

Each step needs the owner's OK. Run them in order.

1. **Ollama version.** This PC runs 0.40.4. The library pages do not state a minimum version for the new tags. If the pull or the first load says it needs a newer Ollama, update Ollama first (a separate approval).
2. **Download** (about 7.6 GB; keep about 8 GB free on the model disk):

   ```bash
   ollama pull qwen3.5:9b
   ```

3. **Test without changing any file.** `local_agent.py` takes `--model` and `--ctx`, which override the two text files. Use an empty scratch folder with one short text file in it as the workspace; do not use the research folder. In another window, run `ollama ps` during the run to see the GPU/CPU split.

   ```bash
   python3 -I /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/local_agent.py --workspace /mnt/c/Users/Pengw/AppData/Local/Temp/ollama-test --task "Read notes.txt and write answer.md with a two-line summary." --model qwen3.5:9b --ctx 32768
   ```

   Pass if the tool calls parse (no errors in `agent-log.jsonl`), the window loads fully on the GPU, and the summary is sensible. Then compare one real topic report from `qwen3.5:9b` with a `qwen3:8b` report on the same topic.

4. **Switch** (only if the test passes). Edit two one-line files:
   - [ollama-model.txt](../tools/agents/local/ollama-model.txt): `qwen3.5:9b`
   - [ollama-ctx.txt](../tools/agents/local/ollama-ctx.txt): `32768`

   Then, in WSL, `python3 idle_research.py status` should report the model as on the server with a 32,768 window. Leave the Modelfile and the defaults in `ollama_url.py` alone.
5. **Roll back**: put back `qwen3:8b` and `16384`. Nothing is deleted, so there is no re-download.

## 6. Not measured or open

- Speed, VRAM and RAM use: none measured. No model was loaded here.
- The Gemma sliding-window allocation in Ollama (section 2).
- Qwen3.5-9B's linear-attention state (assumed small) and whether its `think: false` and tool-call output match what `local_agent.py` and `local_map.py` expect. The test covers both.
- Vendor benchmarks were not reproduced, and none was run on Core3 source.
- Qwen3-8B's own coding and tool numbers were not in the fetched card text, so the quality gap against today's model is unmeasured.
- The Ollama minimum version for these tags (step 1).

## 7. Sources

Ollama library:
- https://ollama.com/library (tags and the "tools" capability)
- https://ollama.com/library/qwen3.5
- https://ollama.com/library/qwen3.6
- https://ollama.com/library/gemma4
- https://ollama.com/library/gpt-oss

Hugging Face model cards and configs (`config.json` read from each `raw/main` path):
- https://huggingface.co/Qwen/Qwen3.5-9B (config: https://huggingface.co/Qwen/Qwen3.5-9B/raw/main/config.json)
- https://huggingface.co/Qwen/Qwen3.6-35B-A3B (config: https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/config.json)
- https://huggingface.co/google/gemma-4-12b (config: https://huggingface.co/google/gemma-4-12b/raw/main/config.json)
- https://huggingface.co/openai/gpt-oss-20b (config: https://huggingface.co/openai/gpt-oss-20b/raw/main/config.json)
- https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512
- https://huggingface.co/Qwen/Qwen3-8B (config: https://huggingface.co/Qwen/Qwen3-8B/raw/main/config.json)

Local files: [ollama-model.txt](../tools/agents/local/ollama-model.txt), [ollama-ctx.txt](../tools/agents/local/ollama-ctx.txt), [REMOTE-OLLAMA.md](../tools/agents/local/REMOTE-OLLAMA.md), [idle_research.py](../tools/agents/local/idle_research.py), [local_agent.py](../tools/agents/local/local_agent.py), [local_map.py](../tools/agents/local/local_map.py), [memguard.py](../tools/agents/local/memguard.py), [ollama_url.py](../tools/agents/local/ollama_url.py).
