# Ollama model options for the idle research (15 Oct 2026)

Research only. Nothing was pulled, downloaded, installed or changed, and no model was loaded. Figures are the vendors' own (Ollama library pages and Hugging Face model cards) unless marked **est.**, which is arithmetic from their config files. Written by Claude (Haiku 5.5) at the owner's request: "maybe swap ollama's model? maybe see if haiku can find something better across the nets".

## Recommendation

**Switch to `qwen3.5:9b` with a 32,768-token window, after the short test in section 5. Keep `qwen3:8b` installed as the fallback.**

- **Fits the 12 GB card entirely on the GPU** at 32K, and by estimate at 64K (est. 9–11 GB of about 11 GB free). No CPU split, so less pressure on the 32 GB of RAM that ran out on 15 Oct.
- **Smaller memory growth per request.** Its KV cache is 32 KB per token against 144 KB for `qwen3:8b` (section 2). The prompt-cache growth that [memguard.py](../tools/agents/local/memguard.py) guards against should be about a quarter of today's (est.: about 0.13 GB per 4K-token request, against about 0.5 GB per request recorded for `qwen3:8b` in [memguard.py](../tools/agents/local/memguard.py)).
- **Tool use has the best-documented numbers of the candidates that fit.** The card says it "excels in tool calling" and reports BFCL-V4 66.1 and TAU2-Bench 79.1 (vendor numbers). Apache 2.0.
- **Twice the source per topic.** `source_cap()` in [idle_research.py](../tools/agents/local/idle_research.py) gives 30,000 characters at 16K (today), 60,000 at 32K, 120,000 at 64K.

**Not yet established:** no benchmark compares it with `qwen3:8b` on our tasks, and speed is unmeasured. The test in section 5 settles both. If it fails, `gemma4:12b` is the next choice. If neither beats `qwen3:8b`, keep the current model. Six models the owner and a peer session suggested were checked in sections 3b and 3c: none beats the recommendation.

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

## 3b. Owner-suggested candidates (added 15 Oct)

Three models suggested after the table above. Same rules: research only, nothing downloaded. The GGUF sizes come from third-party listings and were not checked against the files. Per-token KV figures use the config values in section 2.

| Model | Ollama or GGUF | Size and context | Licence | Tool calling | What the card says it is good at | Jobs it could take |
|---|---|---|---|---|---|---|
| `nvidia/Nemotron-Research-Reasoning-Qwen-1.5B` | No official tag. The Ollama `nemotron` page lists only 70B tags (2 of 17 shown). No community GGUF verified. Importing one means a download, which needs the owner's OK. | 1.5B by name; the card header says "2B params" (F32). Qwen2 architecture, 28 layers, 2 KV heads × 128 dim, so 28 KB per token (est.); config max positions 131,072; the card does not state a native context. | CC-BY-NC-4.0 (non-commercial). The card says "for research and development only". | Not stated | Math and reasoning (v1): AIME24 48.13, AIME25 33.33, GPQA 41.78, IFEval 66.02, Reasoning Gym 59.06. Code average 37.49 (v1). Trained with ProRL; fine-tuned from DeepSeek-R1-Distill-Qwen-1.5B. | Probably none on this PC. A reasoning-distilled model usually writes a long reasoning trace before its answer. That could use up `num_predict 1536` and break the JSON in `local_map.py`. Untested. Not for reading Core3 C++. |
| `ozone-research/0x-lite` | No official tag. A GGUF by bartowski (`ozone-ai_0x-lite-GGUF`) is listed by a third-party aggregator. | 15B per the page (about 14.8B per another listing). Qwen2 architecture, 48 layers, 8 KV heads × 128 dim, so 192 KB per token (est.). Config max positions 32,768. Q4_K_M about 9.0 GB (third-party listing). | Apache 2.0 | Not stated | No benchmarks on the card. Listed uses are text completion, summaries, chat and education, and the card calls it suited to "resource-constrained settings". | None on this PC. At 32K it needs about 16 GB of VRAM (est.); at 8K about 12 GB (est.). |
| `vanta-research/wraith-8b` | `vanta-research/wraith-8b:1.0` on Ollama, 4.9 GB, 128K per a search listing (publisher namespace, not the official library). A third-party GGUF (mradermacher, Q4_K_M) is 4.7 GB. | 8.03B dense Llama 3.1 fine-tune (QLoRA). 32 layers, 8 KV heads × 128 dim, so 128 KB per token (est.). Config max positions 131,072; the card recommends an 8,192 window. | Llama 3.1 Community Licence (commercial use allowed with attribution) | Not mentioned on the card | Math and STEM tutoring, logic and technical writing (self-reported): GSM8K 70.0 (base 51.0); TruthfulQA MC2 58.5; MMLU 66.4 (base 66.6); ARC-Challenge 50.0 (base 52.9); HellaSwag 70.0 (base 73.0). | Not a fit. Tool calling isn't stated, MMLU shows no gain, ARC and HellaSwag fall, and there is no code benchmark. Same memory class as `qwen3:8b` (about 10 GB at 32K, est.). |

**What this means.** None of the three beats `qwen3.5:9b` for this PC. `0x-lite` does not fit the card at any useful window. `wraith-8b` has no tool-calling statement and no coding numbers. The Nemotron 1.5B is the only one small enough to be a cheap-job candidate, and only if a test shows it returns the short JSON answer `local_map.py` asks for. Its non-commercial licence is fine for private research but worth noting.

## 3c. Three more owner-suggested links (15 Oct)

Same rules: research only, nothing downloaded. Sizes come from GGUF listings or Q4 estimates (est.). Per-token KV figures come from the config values.

| Model | Ollama or GGUF | Size and context | Licence | Tool calling | What the card says it is good at | Jobs it could take |
|---|---|---|---|---|---|---|
| `Merlin-Research/Qwen3.5-4B-Safety-Thinking` | The card says GGUF builds are "in active development and validation" and recommends the BF16 checkpoint, loaded with `ollama create` from a local Modelfile. The Hugging Face "Use this model" panel lists `ollama run hf.co/Merlin-Research/...:Q4_K_M`. That panel is not card text and the Q4 build is not validated. | 4B dense, fine-tuned from Qwen3.5-4B (LoRA SFT). 32 layers, 8 with full attention, 4 KV heads × 256 dim, so 32 KB per token (same as `qwen3.5:9b`). Config max positions 262,144. A search listing says 32K, and the card header says "1M context possible". Q4_K_M about 2.5–3 GB (est.); BF16 about 8 GB (est.). | Apache 2.0 | Not mentioned | Safety-oriented reasoning, strict instruction-following, alignment and safety research. No numeric benchmarks. Writes a `<think>…</think>` reasoning block before each answer. | Poor fit for either job. The reasoning block risks breaking the JSON in `local_map.py`. No tool-calling statement for `local_agent.py`. Tuned for safety, not proofreading or code. |
| `Venastine-Research/Xing4.0-29B-A4B-GGUF` (original: `XingChen-AGI/Xing4.0-29B-A4B`, China Telecom; the GGUF is a third-party repackage) | No official Ollama tag found. A guide dated 2026 says llama.cpp support was still an unmerged PR (#29012, opened 17 Sep 2026) with a fork as a workaround. Not verified. | 29B MoE, 4B active (64 routed experts, 4 active, 1 shared). GGUF: IQ2_M 9.9 GB, IQ3_XXS 11.6 GB, Q4_K_M 19 GB. 256K native (card), extensible to 512K. Uses multi-latent attention (kv_lora_rank 512, rope dim 64), so about 45 KB per token (est.), or 1.5 GB at 32K (est.). | Apache 2.0 (card) | Card: "tool calling" under an agent architecture | Agent workflows, complex engineering and coding. Self-reported: SWE-bench Verified 75.00; Terminal-Bench 2.1 57.50; Tau3-Bench 64.63; IFBench 69.67. The card gives Qwen3.6-35B-A3B 76.00 on SWE-bench Verified; Qwen's own card reports 73.4, so the harnesses differ. | Only if it runs at all. IQ2_M plus KV is about 1 GB over the ~11 GB free (est.), so part would run on CPU. IQ2 and IQ3 quants cost quality. Not for now; revisit when an Ollama build supports it. |
| `ibm-research/granite-vision-3.2-2b-GGUF` | Official Ollama tag `granite3.2-vision`: 2.4 GB, 16K context, vision and tools badges. This GGUF is a Q4_K_M at 1.55 GB. | 2B-class (the GGUF section says 3B). Text decoder: 40 layers, 8 KV heads × 64 dim, so 80 KB per token (est.). The card gives no native context; the Ollama tag caps at 16K. | Apache 2.0 | Ollama tag shows tools; card does not mention tool calling | Enterprise visual document understanding: tables, charts, OCR and questions about document images. The card says text-only tasks should go to the Granite LLMs. | Not research chunks or Core3 source. Could help if you ever need OCR of screenshots, scanned tables or a PDF page. |

**What this means.** None of the three beats `qwen3.5:9b` for the research jobs. The Merlin model is small and fits easily, but it is a safety-tuned reasoning model with no tool-calling statement. Xing 4.0 has the strongest agent numbers of the batch, but it has no confirmed Ollama path and a 29B quant would spill to CPU. Granite Vision is a document-image model, so it is a different job.

## 4. Why this order

- **`qwen3.5:9b` over `gemma4:12b`.** They are close. `gemma4:12b` has the higher LiveCodeBench (72.0 against 65.6). `qwen3.5:9b` has the stronger tool-use evidence (TAU2 79.1 against 69.0, and a BFCL figure that `gemma4:12b`'s card doesn't give), and it leaves more room at 64K. `local_agent.py` leans on tool calls, so `qwen3.5:9b` goes first.
- **`qwen3.6:35b` is not for now.** It has the best coding numbers in the table, but 23–24 GB will not stay on a 12 GB card. On this PC that means ~14 GB in RAM on 32 GB, the SWG client running, and the 15 Oct crash. Revisit it only after a memory test, or on a machine with more RAM.
- **`gpt-oss:20b` is not better on the numbers we have.** It is the code default and already installed, and it runs partly on CPU at any window above 16K. Keep it installed for now; deleting it is an owner decision.
- **`devstral-small-2:24b`** has a good tool number, but as a dense 24B it would be slow here (speed not measured).
- **Owner-suggested models (sections 3b and 3c)** do not beat the recommendation on card numbers, fit, or tool calling. Nemotron 1.5B is the only one worth a test for the cheapest chunk jobs.
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

Section 3b (owner-suggested):
- https://huggingface.co/nvidia/Nemotron-Research-Reasoning-Qwen-1.5B (config: https://huggingface.co/nvidia/Nemotron-Research-Reasoning-Qwen-1.5B/raw/main/config.json)
- https://ollama.com/library/nemotron (checked for a 1.5B tag)
- https://huggingface.co/ozone-research/0x-lite (config: https://huggingface.co/ozone-research/0x-lite/raw/main/config.json)
- https://www.promptlayer.com/models/ozone-ai0x-lite-gguf (third-party GGUF listing, not verified against the files)
- https://huggingface.co/vanta-research/wraith-8b (config: https://huggingface.co/vanta-research/wraith-8b/raw/main/config.json)
- https://ollama.com/vanta-research/wraith-8b/tags (seen in a search listing, not fetched directly)

Section 3c (owner-suggested):
- https://huggingface.co/Merlin-Research/Qwen3.5-4B-Safety-Thinking (config: https://huggingface.co/Merlin-Research/Qwen3.5-4B-Safety-Thinking/raw/main/config.json)
- https://huggingface.co/Venastine-Research/Xing4.0-29B-A4B-GGUF
- https://huggingface.co/XingChen-AGI/Xing4.0-29B-A4B (config: https://huggingface.co/XingChen-AGI/Xing4.0-29B-A4B/raw/main/config.json)
- https://www.mindstudio.ai/blog/xing4-29b-a4b-benchmarks and https://andrew.ooo/answers/what-is-xing4-0-29b-a4b-china-telecom-single-gpu-agent-model-september-2026/ (secondary guides, for the llama.cpp PR status; not verified)
- https://huggingface.co/ibm-research/granite-vision-3.2-2b-GGUF
- https://huggingface.co/ibm-granite/granite-vision-3.2-2b (config: https://huggingface.co/ibm-granite/granite-vision-3.2-2b/raw/main/config.json)
- https://ollama.com/library/granite3.2-vision

Local files: [ollama-model.txt](../tools/agents/local/ollama-model.txt), [ollama-ctx.txt](../tools/agents/local/ollama-ctx.txt), [REMOTE-OLLAMA.md](../tools/agents/local/REMOTE-OLLAMA.md), [idle_research.py](../tools/agents/local/idle_research.py), [local_agent.py](../tools/agents/local/local_agent.py), [local_map.py](../tools/agents/local/local_map.py), [memguard.py](../tools/agents/local/memguard.py), [ollama_url.py](../tools/agents/local/ollama_url.py).
