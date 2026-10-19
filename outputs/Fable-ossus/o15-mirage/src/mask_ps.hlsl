// Ossus O15 mirage, pass 1 (Claude, 18 Oct 2026): the ghostfire blade's own draw, replayed into a screen-sized mask.
// The game's vertex stage and blade texture stay bound, so the blade lands on the same pixels it is about to light;
// rasterising into a screen-sized target is what gives ps_2_0 (no screen position) a screen-space mask.
// Mask = glow (texture rgb) plus white core (texture alpha), times the gain and the game's fade opacity (c7.a, which
// the blade program multiplies its own colour by). Blended with MAX.

sampler bladeMap : register(s0);
float4 maskParams : register(c0);              // x: gain (ours)
float4 alphaFadeOpacityHolder : register(c7);  // the game's: a = fade opacity

float4 main(in float2 tcs_MAIN : TEXCOORD0) : COLOR
{
	float4 t = tex2D(bladeMap, tcs_MAIN);
	float m = saturate((max(t.r, max(t.g, t.b)) + t.a) * maskParams.x) * alphaFadeOpacityHolder.a;
	return float4(m, m, m, m);
}
