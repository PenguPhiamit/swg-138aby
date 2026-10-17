# ComfyUI on the friend's PC: the setup prompt

For the owner, at the friend's PC (Claude, 17 Oct 2026; owner: "get me a prompt to set this all up on the homies pc
to. maybe we can get a bunch of the heavy lifting of the art done"). Paste the prompt below into Claude on the friend's
PC. It sets up the same free art tools as Miniverse (ComfyUI with FLUX.2 [klein] 4B for images and TRELLIS.2 for
image-to-3D, about 23.4 GB), reachable from Miniverse only, the way Ollama already is ([README.md](README.md)).
Licences and sizes: [Documentation-support/local-art-models.md](../../../../Documentation-support/local-art-models.md).

The friend's PC has an RTX 4070 Super (12 GB) and 32 GB RAM. The card can't hold an art model and the big Ollama
model at once, so Miniverse pauses the research queue while it sends an art batch, and frees ComfyUI's memory
afterwards.

## The prompt

```text
You're helping set up a local art server on this Windows PC. It's a friend's PC on my home network, and I'm the
owner of a private game-modding project. My own PC will send image and 3D jobs here over the home network, the same
way it already sends text jobs to Ollama on this PC. Ask me before every download, install or system change, and show
the file name, source and size first.

Before anything:
1. Confirm with me that the friend has agreed to: about 25 GB more disk, the graphics card running art jobs (the
   image model uses about 8 GB of VRAM; the 3D model may use most of the 12 GB), and a second firewall rule. Stop if not.
2. Report: Windows version, GPU, driver version and "CUDA Version" from nvidia-smi, free RAM, free space on C:, the
   network profile (it must be Private), and whether Ollama has a model loaded (ollama ps).
3. Find my PC's address from the existing rule:
   Get-NetFirewallRule -Name SWG-Ollama-OwnerPC | Get-NetFirewallAddressFilter   (RemoteAddress). If it's missing, ask me.

Install, one step at a time, with my yes for each download:
4. ComfyUI portable for NVIDIA from the official releases, github.com/Comfy-Org/ComfyUI/releases: the newest
   ComfyUI_windows_portable_nvidia.7z (v0.41.0 or later, about 2 GB). It ships PyTorch for CUDA 13.0, which needs a
   driver whose nvidia-smi shows CUDA 13.0 or later. If the driver is older, don't update it: tell me, and look for a
   portable build for an older CUDA on the same release page. Check the SHA-256 if the release lists one. Extract to
   %USERPROFILE%\Tools\ComfyUI_windows_portable.
5. These model files into ComfyUI\models\<folder>, from Hugging Face (no login; find each file on its repo's Files
   page and download its resolve/main link):
   - diffusion_models\flux-2-klein-4b-fp8.safetensors: black-forest-labs/FLUX.2-klein-4b-fp8, 4.07 GB, Apache 2.0.
     Only the 4B; the 9B needs a separate agreement, so not that one.
   - text_encoders\qwen_3_4b.safetensors: Comfy-Org/vae-text-encorder-for-flux-klein-4b (split_files/text_encoders),
     8.04 GB, Apache 2.0
   - vae\flux2-vae.safetensors: the same repo (split_files/vae), 0.34 GB
   - diffusion_models\trellis_2_int8_convrot.safetensors: Comfy-Org/TRELLIS.2, 5.25 GB, MIT
   - vae\trellis_2_shape_vae_bf16.safetensors: Comfy-Org/TRELLIS.2, 1.10 GB
   - vae\trellis_2_texture_vae_bf16.safetensors: Comfy-Org/TRELLIS.2, 0.95 GB
   - clip_vision\dino_v3_vit_l.safetensors: Comfy-Org/TRELLIS.2, 1.21 GB
   - background_removal\birefnet.safetensors: Comfy-Org/BiRefNet, 0.44 GB, MIT
   Nothing else: no Pixal3D, no custom nodes, no ComfyUI-Manager installs.
6. Two scripts in the ComfyUI_windows_portable folder, plus desktop shortcuts to them named "SWG art server - start"
   and "SWG art server - stop":
   - start-swg-art.bat: the same command and flags as advanced\run_nvidia_gpu_disable_api_nodes.bat (it uses
     --offline, which turns off paid API nodes), plus --listen 0.0.0.0 --port 8188 --disable-auto-launch.
   - stop-swg-art.bat: ends only the python process running ComfyUI\main.py.
   Don't make it start at logon unless I say so.
7. One inbound firewall rule named SWG-ComfyUI-OwnerPC: TCP port 8188, program = the full path of
   python_embeded\python.exe, remote address = my PC's address from step 3, Private profile only. It needs an
   administrator once. If PowerShell says Access is denied, tell me, and I'll run that one command in an administrator
   PowerShell. ComfyUI has no password: never forward port 8188 on the router. If Windows asks to allow it on networks,
   tick Private only.

Test:
8. First make sure no game is running and Ollama has no model loaded (ollama ps; if one is loaded, ollama stop <name>).
   The card can't hold both.
9. Run the start script.
   - Check that curl.exe http://127.0.0.1:8188/system_stats shows the GPU.
   - In the browser at http://127.0.0.1:8188, load the FLUX.2 klein 4B text-to-image template. Make one 1024 px image
     of "a weathered stone shrine on a forest hill, concept art". Note the seconds and the peak VRAM from nvidia-smi.
   - Load the TRELLIS.2 image-to-3D template with its switch on TRELLIS.2, not Pixal3D. Run it on that image at the
     512 preset. Note the seconds, the peak VRAM, whether it finishes, and where the .glb lands.
   - Then free the memory:
     curl.exe -X POST http://127.0.0.1:8188/free -H "Content-Type: application/json" -d "{\"unload_models\":true,\"free_memory\":true}"
10. Print a summary for the Claude on my PC:
    - "ComfyUI on the friend's PC: http://<this PC's home-network IPv4>:8188";
    - the ComfyUI version, the driver and CUDA versions;
    - each file with its folder and size;
    - both test timings and VRAM peaks;
    - anything that failed.
    Save the same summary to %LOCALAPPDATA%\swg-comfy-lan\last-run.txt.

Rules:
- Ask before every download, install or system change.
- No driver updates, no custom nodes, no other models.
- Don't change Ollama's settings or its firewall rule. Never forward ports. Don't sign in to anything.
- If something fails, report the error; don't work around it with other downloads.
- Tell the friend: before gaming, double-click "SWG art server - stop", as with quitting Ollama.
```

## After it runs (Miniverse)

- Give Claude the printed address. It goes in a `comfy-url.txt` next to `ollama-url.txt`. `um comfy --url <address>`
  (or `COMFYUI_URL`) sends jobs there.
- Before an art batch: pause the research queue (`Agent/local-research/STOP`) and wait for the running topic to end,
  so Ollama unloads. After it: POST `/free` to ComfyUI, then delete STOP.
- Input images (TRELLIS.2 needs one) are uploaded with ComfyUI's `/upload/image` before the run, because the friend's
  ComfyUI can't see this PC's files.
