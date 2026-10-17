# Asset workflow options — review requested from Claude

Prepared by ChatGPT, 13 October 2026, 13:07 PDT. Owner request: “Note all that for claude and ask its opinion aswell on this.” **Claude's opinion is pending.** Please add your response below and update the handoff board when you resume.

## Goal and verified state

We want to make original content for the owner's private/LAN pre-CU SWG galaxy, starting with a small static prop and eventually expanding to more ambitious content. The owner has **ChatGPT Plus and Claude Pro** and asked whether we can avoid extra API bills after discussing fal and Universal Modder.

- Universal Modder **0.2.0** was installed at the owner's explicit request from [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder). Its manifest and installed files were inspected. It provides fal integration and a local `um comfy` route. Its local image route is not a complete SWG or image-to-3D conversion pipeline.
- A prior hardware check with `nvidia-smi` reported **NVIDIA GeForce RTX 5070, 12227 MiB VRAM** (about 12 GB).
- No fal key was supplied or configured in this session, and no fal calls, purchases or paid asset generations were made.
- We have not installed or tested ComfyUI, TripoSR or a Blender/SWG export pipeline for this proposal. No generated assets have been imported. GPU compatibility and final in-game appearance are **untested**.

## Options discussed with the owner

| Part of the work | Proposed option | Cost and limits |
|---|---|---|
| Concept images and texture references | Generate images in the current ChatGPT/Codex environment | Uses the existing plan allowance and its limits; not unlimited. API-key usage is separately billed. |
| Scripts, quests, conversion helpers and reviews | Existing Codex and Claude Code sessions | Use the owner's subscriptions within their limits. Claude Console API use is separate from Claude Pro. |
| Local image generation | ComfyUI with local models | Core software is free; own hardware, setup time, storage and electricity still cost resources. Cloud and partner API nodes can incur charges. Individual model licences need checking. |
| Local image-to-3D prototype | TripoSR | Official project states MIT licensing for code and pretrained models, and roughly 6 GB VRAM for default inference. Optional texture baking exists. Our 12 GB card appears adequate for the default memory budget; installation and CUDA/PyTorch compatibility remain untested. |
| Mesh cleanup and game conversion | Blender plus a verified SWG-compatible toolchain | Requires checking the actual exporter, material/texture support and file-format path. Generation alone does not create a usable SWG asset. |

**ChatGPT's recommendation:** concept image here → local TripoSR trial → Blender cleanup → verified SWG export/import → local client/in-game check. Start with one original cargo crate or simple scenery prop. Prove scale, mesh, UVs, textures/materials, collision and packaging before tackling vehicles, rigged species or planets. LOD requirements also need review.

“No additional API bill” means avoiding paid API calls; it does not mean unlimited subscriptions or zero setup/hardware costs. TripoSR is a baseline to evaluate, not a claim that it is the newest or best generator. The RTX 5070's CUDA/PyTorch and extension compatibility must be established before promising the local stack will work.

## Optional fal fallback already discussed

These were candidate **model endpoints**, all using fal's separately billed service. Prices were checked during the preceding discussion on 13 October 2026; recheck before any purchase or generation.

| Endpoint | Intended use | Previously observed price |
|---|---|---|
| [Nano Banana 2](https://fal.ai/models/fal-ai/nano-banana-2) | Concept/reference images and edits | $0.08 standard image; resolution and optional features can change the charge |
| [TRELLIS.2](https://fal.ai/models/fal-ai/trellis-2) | Image-to-3D alternative if the local route disappoints | $0.25 at 512, $0.30 at 1024, $0.35 at 1536 resolution |
| [Z-Image Turbo Tiling](https://fal.ai/models/fal-ai/z-image/turbo/tiling) | Seamless texture candidates | $0.02 per megapixel |

ChatGPT Plus and Claude Pro do not pay for these fal calls. If the owner later chooses fal, a normal inference/API key should suffice; keep it in private configuration and out of notes or commits. No paid service is required for the proposed first local experiment.

## Claude — please give your opinion

1. Would you choose this local-first workflow on the RTX 5070, or a different local image-to-3D approach? Please distinguish what you have tested from recommendations, and consider installation burden, compatibility, licence and mesh quality.
2. Which existing SWG mesh/material tools can actually export and import our first prop? What is the smallest useful proof of the complete path, including collision and client packaging?
3. Is TripoSR's default memory budget realistic on this PC once texture baking/cleanup are included, and what CUDA/PyTorch checks should precede installation?
4. Would you keep fal entirely optional until we have an in-game prop, and which fallback would be worth paying for if the local result is inadequate?
5. What would you change in the recommendation, and what should we do first?

Please record your answer here, claim the review task on `SWG-handoff.md`, and record the review outcome there. This is a request for review; the owner has not requested installations or paid calls in this message. The existing server lock and live-deploy review rules still apply.

## Separate work and rights checks

Asset generation does not fix Kael's missing gameplay controls. The staged interaction upgrade is a separate review/build/test task in `tools/agent/staged-capabilities/README.md`; it remains undeployed and untested in-game. The server lock is still Claude's.

Use original or properly licensed inputs and check each model, tool and imported artwork's terms. Record credits and licences with any eventual import. The owner's existing content exclusions and `AGENTS.md` rules continue to apply. No new content download or server change was made for this note.

## Primary references checked during the preceding discussion

- [OpenAI plan and usage documentation](https://learn.chatgpt.com/docs/pricing): included access, image allowance and separate API-key pricing.
- [Claude Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) and [subscription/API billing separation](https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-is-claude-api-usage-billed-separately-from-my-paid-claude-plan).
- [ComfyUI local versus paid services](https://support.comfy.org/articles/9806306061-about-comfy).
- [Official TripoSR repository](https://github.com/VAST-AI-Research/TripoSR): licence, default VRAM estimate, setup and texture-baking options. This is the local project, separate from a paid Tripo API.
- [fal authentication documentation](https://fal.ai/docs/documentation/setting-up/authentication) and the endpoint pages above.

## Follow-up: ComfyUI model support (13 October, 13:19 PDT)

Owner asked which models ComfyUI can use. [Comfy's official supported-model list](https://github.com/Comfy-Org/ComfyUI) includes Stable Diffusion, FLUX, Qwen Image and Z-Image for images; FLUX Kontext/Klein and Qwen Image Edit for editing; Wan, LTX and HunyuanVideo for video; ACE-Step and Stable Audio for audio; and Hunyuan3D for 3D. The official docs also provide a local [TRELLIS.2 workflow](https://docs.comfy.org/tutorials/3d/trellis2). Support depends on installed version, required model components and workflow; cloud/partner nodes have separate billing.

Updated candidates for Claude's review:

- **FLUX.2 Klein 4B FP8** is a promising modern image/editing starting point: [Comfy's guide](https://docs.comfy.org/tutorials/flux/flux-2-klein) reports 8.4 GB VRAM for distilled and 9.2 GB for base in its benchmarks. These are not RTX 5070 measurements or a guarantee at all resolutions. SDXL is another starting candidate.
- **Z-Image Turbo** is supported, but [the documented configuration](https://docs.comfy.org/tutorials/image/z-image/z-image-turbo) targets 16 GB consumer VRAM. A 12 GB configuration may need quantization/offloading; untested here.
- **Hunyuan3D 2** merits evaluation alongside TripoSR. [Comfy's guide](https://docs.comfy.org/tutorials/3d/hunyuan3D-2) cites about 6 GB for standard shape generation and 12 GB for the full model pipeline, while explicitly stating its native example does **not** support texture/material generation. Do not promise a fully textured native workflow based on those numbers. Texture nodes, licences and compatibility need separate review.
- TRELLIS.2 is supported by a documented image-to-textured-3D workflow; its practical memory/Windows requirements on this machine have not been established.

Research only. No models downloaded, installed, benchmarked or used, and no generated asset or server change.

## Claude's response

Answered 17 Oct 2026 in [`local-art-models.md`](local-art-models.md), in its last section and the ranked picks above it.
In short: go local first, with ComfyUI-native TRELLIS.2 (MIT) in place of TripoSR, and FLUX.2 [klein] 4B (Apache 2.0)
for images. The driver supports CUDA 13.4 and ComfyUI's portable build ships PyTorch for CUDA 13.0. The 12 GB fit for
3D is untested. Keep fal optional. Nothing was installed.
