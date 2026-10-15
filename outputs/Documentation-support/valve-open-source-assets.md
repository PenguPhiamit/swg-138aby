# Valve free and open-source items for the SWG emulator project (research, 15 Oct 2026)

Written by a Claude Haiku research agent on 15 Oct 2026 (owner: "Have an agent take a look at valve and their free use and open sources assets and programs"); saved by Claude. No downloads were made.

**Sourcing:** I read the GitHub repo pages and the Steam Subscriber Agreement directly. The Valve developer wiki and partner.steamgames.com returned 403 to my fetches, so those claims come from search snippets and are marked. Wine's official licence page was blocked, so its licence comes from Debian packaging and mirrored copies. This is research, not legal advice.

## 1. Short answer

Most useful:
1. **Wine + DXVK** (the same pieces Proton bundles) to run the original Windows client on Linux or WSL for bot and real-client tests. Free and open source, and no Steam login is needed if Wine is used directly. Wine is LGPL-2.1+, DXVK is zlib.
2. **Valve Developer Community wiki** as a reference for Valve file formats (VTF/VMT, MDL) for the art pipeline. Reference only; verify its licence first.
3. **GameNetworkingSockets** (BSD-3-Clause) if the LAN group needs an encrypted relay or tunnel for tools. It cannot replace Core3's own SWG protocol.
4. Minor: **Fossilize** (MIT) to share Vulkan shader caches, and **gamescope** for fixed-size test windows on a Linux desktop.

Hard no's:
- Valve game models, textures, sounds or maps in SWG or the art pipeline.
- Source SDK 2013 or Half-Life 1 SDK code in Core3 or the bots.
- The Steamworks SDK, which is built for Steam titles.
- Steam or Valve logos and names as project branding.
- Reverse engineering Valve's Steam content, or hosting Valve-game matchmaking or servers outside Valve.

## 2. Table

| Item | What it is | Licence (official URL) | Use here? | Catch |
|---|---|---|---|---|
| Proton | Steam's Wine-based compatibility tool; bundles Wine, DXVK, vkd3d-proton and more | BSD-3-Clause for Valve's wrapper; each component keeps its own licence. https://github.com/ValveSoftware/Proton | Indirect: runs the old client on Linux. Steam's copy needs the owner's own Steam login. | The README describes it as a tool for use with the Steam client. Standalone use is not documented. |
| Wine (Valve fork) | Windows API layer for Linux | LGPL-2.1+ (Debian packaging and a mirrored LICENSE; official page blocked). https://github.com/ValveSoftware/wine | Yes: run the client in a Wine prefix with no Steam. The most direct route. | Keep LGPL notices if shipping binaries. The Wine name is a trademark (not checked). |
| DXVK | Direct3D 8/9/10/11 to Vulkan. Not Valve-written; Proton ships it. | zlib. https://github.com/doitsujin/dxvk | Yes if the client uses D3D8 or D3D9. Expected for a 2003-era client but not checked. | Needs a working Vulkan driver. Documented for Wine prefixes. |
| vkd3d-proton | Direct3D 12 to Vulkan | LGPL-2.1. https://github.com/HansKristian-Work/vkd3d-proton | No: D3D12 only, and the old client likely does not use it. | None relevant. |
| GameNetworkingSockets | Game transport: reliable and unreliable UDP messages, encryption, P2P, NAT traversal | BSD-3-Clause. https://github.com/ValveSoftware/GameNetworkingSockets | Maybe: an encrypted link for bot control or a friends' relay. | Steam Datagram Relay is Steam-only. Adds a C++ dependency. |
| Fossilize | Records and replays Vulkan pipeline objects for shader cache warm-up | MIT. https://github.com/ValveSoftware/Fossilize | Low: share shader caches in the LAN group if DXVK stutter matters. | Helps only the Vulkan path. |
| gamescope | Micro-compositor for fixed-size game sessions | Licence not named on the page; a LICENSE file exists. https://github.com/ValveSoftware/gamescope | Low: fixed-size windows for test capture on Linux. | Needs Wayland, X11 or DRM. WSL is not mentioned. |
| Steam Audio | Spatial audio SDK | Apache-2.0 (repo listing; full source open from v4.5.2, Feb 2024, per news). https://github.com/ValveSoftware/steam-audio | Low: only for audio tools. | Apache 2.0 grants no trademark rights. |
| OpenVR | VR API | BSD-3-Clause. https://github.com/ValveSoftware/openvr | No. | VR only. |
| Source SDK 2013 | Source engine code and tools | "Source 1 SDK License", non-commercial (README). https://github.com/ValveSoftware/source-sdk-2013 | No for code. Reading only. | Modify and redistribute free of charge, only to build a modified Valve game (summary of the LICENSE). |
| Half-Life 1 SDK | HL1 engine code | Valve licence: free for modified Valve games; commercial use needs Valve's consent. Repo not fetched; text from a mirror. https://github.com/ValveSoftware/halflife | No. | Same scope limit. |
| Steamworks SDK | Steam APIs (achievements, auth, networking) | Partner access agreement, not retrieved. https://partner.steamgames.com/doc/sdk | No. | For Steam titles. The emulator is not on Steam. Partner onboarding required. |
| Hammer, Source SDK Base 2013 | Source level editor and SDK base | Free on Steam (per wiki snippet). Developer tools are non-commercial; commercial use needs Valve's OK (Subscriber Agreement 2.C). https://store.steampowered.com/subscriber_agreement/ | No for SWG. Reference only. | Windows-only; runs under Wine or Proton. Built for Source games. |
| Source Filmmaker | Animation tool for films using Valve assets | Free beta on Steam (https://store.steampowered.com/app/1840/). The software may be used commercially; Valve assets for personal non-commercial use. https://www.sourcefilmmaker.com/sfm_subscription_agreement | Low: storyboarding or animation reference only. | A credit line is required. Assets stay Valve's. |
| Steam Runtime | Linux runtime for Steam apps | Licence not named on the page. https://github.com/ValveSoftware/steam-runtime | Low: only if using Proton through Steam. | Standalone use not documented. |
| Valve Developer Community wiki | Community Valve developer reference (formats, tools) | Not verified: the site returned 403. Possibly CC BY-NC-SA 3.0 (from memory); check the footer. https://developer.valvesoftware.com/wiki/Main_Page | Yes, for format reference. | Community content, not official policy. |

## 3. Game content terms

**Official text:**
- Steam Subscriber Agreement (https://store.steampowered.com/subscriber_agreement/). Valve owns the content (2.F). Fan art, including audio-visual work that references Valve games, may be distributed only non-commercially, except through Workshop or a Subscription Marketplace (2.D). Third-party material needs your own rights. Copying, modifying, reverse engineering or decompiling Valve content needs written consent (2.G). Hosting or matchmaking for it outside Valve's systems is barred (2.G).
- Source Filmmaker terms: Valve assets are for personal, non-commercial use with the games, and works carry a Source Filmmaker credit line.
- Source 1 SDK licence: free to modify and redistribute, but only to build modified Valve games.

**Community wiki (unverified, from snippets):** first-party Valve models, textures and sounds may be ported to non-commercial mods and fangames, including non-Valve engines. Commercial use needs Valve's OK. Other publishers' assets need that publisher's licence. Extracting and redistributing raw archive files is a separate problem.

**Answer:** Valve's terms do not grant permission to use Valve game assets outside Valve games or engines. The closest clause is the fan-art one, which is non-commercial only. SWG is not a Valve game, so the only route is a non-commercial reading or written permission. For this project, keep Valve art out of the pipeline. SWG's own content belongs to Sony and Lucasfilm and is outside Valve's terms. The only public discussion found is a 2009 forum thread and a 2015 controversy; there is no official ruling.

## 4. Next steps and cost

1. Run the client with plain Wine and DXVK on a Linux box, or WSL with WSLg. Cost: 2 to 4 hours, free, no Valve permission, no Steam login. First check the client's Direct3D version (`dumpbin /imports` on the exe, about 10 minutes); this decides whether DXVK covers it.
2. For Steam's Proton, the owner installs Steam and logs in personally. Cost: about 30 minutes, free.
3. Read each repo's LICENSE before bundling any binary. Cost: about 1 hour.
4. Check the Valve wiki footer licence before quoting or copying any page. Cost: 5 minutes.
5. GameNetworkingSockets for an encrypted LAN relay: 1 to 3 days of integration, no permission needed.
6. Ask Valve (the contact address in the HL1 SDK text) only if a Valve asset or code use is wanted beyond the non-commercial scope. Cost: weeks and uncertain. Probably not needed.
7. Skip the Steamworks SDK and any Valve asset import.

## 5. Open questions

- Which Direct3D version does the client use (D3D8, D3D9 or other)? Decides the DXVK route.
- Which host will run the client: native Linux, WSL with WSLg, or a VM?
- Not verified in this run: gamescope and Steam Runtime licence files, Wine's official licence page, the Valve wiki licence, the Steamworks access agreement text, and the Half-Life SDK repo LICENSE.
- Core3's own licence was not checked. It matters before importing LGPL or zlib code.
- The legal status of SWG emulation is outside Valve's terms and is unresolved. This is general information, not legal advice.
