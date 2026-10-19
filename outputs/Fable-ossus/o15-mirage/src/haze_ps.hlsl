// Ossus O15 mirage, pass 2 (Claude, 18 Oct 2026): bend the scene behind the ghostfire blade.
// Drawn as one screen quad (pre-transformed, so TEXCOORD0 is the screen position) before the blade itself draws.
// s0 is a copy of the scene so far, s1 the blade mask, s2 a tiling noise texture (rg one layer, ba another).
// Pixels outside the widened mask are discarded, so nothing else on screen changes.

sampler sceneMap : register(s0);
sampler maskMap  : register(s1);
sampler noiseMap : register(s2);

float4 haze0 : register(c0);   // xy: bend at full mask (screen uv), z: time x speed, w: colour split
float4 haze1 : register(c1);   // xy: mask spread (screen uv), z: mask gain, w: unused
float4 haze2 : register(c2);   // xy: noise tiles across the screen (aspect kept), z: 1 shows the mask in red (debug_view), w: 1 keeps every pixel (debug_view 2)

float4 main(in float2 uv : TEXCOORD0) : COLOR
{
	// widen and soften the mask so the haze reaches past the blade's edge
	float m = tex2D(maskMap, uv).r * 2.0f;
	m += tex2D(maskMap, uv + float2(haze1.x, 0.0f)).r;
	m += tex2D(maskMap, uv - float2(haze1.x, 0.0f)).r;
	m += tex2D(maskMap, uv + float2(0.0f, haze1.y)).r;
	m += tex2D(maskMap, uv - float2(0.0f, haze1.y)).r;
	m = saturate(m * (haze1.z / 6.0f));
	clip(m + haze2.w - 0.004f);

	// two noise layers: one rising like heat, one drifting across it
	float2 nuv = uv * haze2.xy;
	float2 n1 = tex2D(noiseMap, nuv + float2(0.0f, haze0.z)).rg;
	float2 n2 = tex2D(noiseMap, nuv * 1.7f + float2(haze0.z * 0.37f, haze0.z * -0.61f)).ba;
	float2 off = (n1 + n2 - 1.0f) * haze0.xy * m;

	// a slight colour split along the bend: the opal fringe
	float3 c;
	c.r = tex2D(sceneMap, uv + off * (1.0f + haze0.w)).r;
	c.g = tex2D(sceneMap, uv + off).g;
	c.b = tex2D(sceneMap, uv + off * (1.0f - haze0.w)).b;
	c = lerp(c, float3(m, n1.x, n2.y), haze2.z);
	return float4(c, 1.0f);
}
