// SpeciesColorLock.fx: keep the game's own colours through DLSS 5 neural rendering.
// SWG sandbox project, 14 Oct 2026 (Claude). Our own code; see README.md in this folder.
//
// DLSS 5's neural pass tends to pull skin toward human tones, which washes out Chiss blue, Rodian green and Twi'lek
// colours. This pair of techniques remembers the game's frame before the neural pass and, after it, keeps the neural
// frame's brightness and detail but puts back the game's own hue and saturation.
//
// Technique order in the ReShade overlay (top runs first):
//   SpeciesColorLock_Save    (above everything that changes colour)
//   LUMENITE: Kernel 2.0     (the Feeder's motion-vector provider)
//   DLSS 5 Feed              (directly below the Kernel, as the Feeder asks)
//   SpeciesColorLock_Apply   (directly below DLSS 5 Feed)
//   ... your other effects (colour grading, bloom) after these

#include "ReShade.fxh"

uniform float Strength <
	ui_type = "slider"; ui_min = 0.0; ui_max = 1.0;
	ui_label = "Colour lock strength";
	ui_tooltip = "0 = DLSS's colours, 1 = the game's own colours (hue and saturation). Brightness and detail stay DLSS's.";
> = 0.85;

uniform bool ColouredOnly <
	ui_label = "Only strongly coloured areas";
	ui_tooltip = "Lock only pixels that were clearly coloured before DLSS (blue, green or red skin, painted armour); "
	             "grey and neutral areas keep DLSS's colour and lighting.";
> = true;

uniform float SatLow <
	ui_type = "slider"; ui_min = 0.0; ui_max = 1.0;
	ui_label = "Lock starts at saturation";
> = 0.12;

uniform float SatHigh <
	ui_type = "slider"; ui_min = 0.0; ui_max = 1.0;
	ui_label = "Fully locked at saturation";
> = 0.35;

uniform bool OneFrameDelay <
	ui_label = "Match the Feeder's one-frame delay";
	ui_tooltip = "On when the Feeder's async_home = 1 (its default): its neural frame belongs to the previous frame, "
	             "so the lock uses the previous frame's colours. Off if you set async_home = 0.";
> = true;

uniform bool ShowMask <
	ui_label = "Show the lock mask";
	ui_tooltip = "White = fully locked to the game's colours, black = DLSS's colours.";
> = false;

texture SCL_Before { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
texture SCL_Prev { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
sampler sSCL_Before { Texture = SCL_Before; };
sampler sSCL_Prev { Texture = SCL_Prev; };

static const float3 LUMA = float3(0.2126, 0.7152, 0.0722);

float Saturation(float3 c)
{
	float hi = max(c.r, max(c.g, c.b));
	float lo = min(c.r, min(c.g, c.b));
	return hi > 1e-4 ? (hi - lo) / hi : 0.0;
}

// Save, pass 1: last frame's copy moves to SCL_Prev (for the one-frame delay).
float4 PS_KeepPrevious(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
	return tex2D(sSCL_Before, uv);
}

// Save, pass 2: this frame before the neural pass.
float4 PS_Save(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
	return float4(tex2D(ReShade::BackBuffer, uv).rgb, 1.0);
}

float4 PS_Apply(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
	float3 now = tex2D(ReShade::BackBuffer, uv).rgb;
	float3 before = OneFrameDelay ? tex2D(sSCL_Prev, uv).rgb : tex2D(sSCL_Before, uv).rgb;

	float yNow = dot(now, LUMA);
	float yBefore = dot(before, LUMA);

	// The game's colour without its brightness, scaled to DLSS's brightness so lit and shaded areas keep their strength.
	// Adding it to DLSS's brightness leaves the brightness exactly DLSS's (the chroma term has zero luma).
	float3 chroma = before - yBefore;
	float scale = yBefore > 1e-4 ? clamp(yNow / yBefore, 0.0, 4.0) : 1.0;
	float3 locked = saturate(yNow + chroma * scale);

	float weight = Strength;
	if (ColouredOnly)
		weight *= smoothstep(SatLow, max(SatHigh, SatLow + 1e-3), Saturation(before));

	if (ShowMask)
		return float4(weight.xxx, 1.0);

	return float4(lerp(now, locked, weight), 1.0);
}

technique SpeciesColorLock_Save <
	ui_tooltip = "Place ABOVE DLSS 5 Feed (and above any colour effects): remembers the game's frame before the neural pass.";
>
{
	pass KeepPrevious { VertexShader = PostProcessVS; PixelShader = PS_KeepPrevious; RenderTarget = SCL_Prev; }
	pass Save { VertexShader = PostProcessVS; PixelShader = PS_Save; RenderTarget = SCL_Before; }
}

technique SpeciesColorLock_Apply <
	ui_tooltip = "Place directly BELOW DLSS 5 Feed: puts the game's own colours back on the neural frame.";
>
{
	pass { VertexShader = PostProcessVS; PixelShader = PS_Apply; }
}
