//hlsl ps_2_0

#include "pixel_program/include/pixel_shader_constants.inc"
#include "pixel_program/include/functions.inc"

// The stock lightsaber blade pixel program (patch_11_02), with one addition for the Ossus ghostfire crystal (O14, Claude,
// 18 Oct 2026). For every blade colour a crystal can give on this server (palette entries 0-11 and 31, brightest channel
// 0.65 or more) ghost is exactly 0 and the result is the stock one. Palette entries 32-40 (ghostfire) keep every channel
// at 0.157 or less: ghost is 1, the white-hot core is cut almost away and the glow becomes milky pastel opal bands. The
// green channel carries the shimmer step the server sets every 150 ms (entry 32 + k: green = 4k/255), so the bands drift
// along the blade one wavelength per 8 steps.

sampler diffuseMap : register(s0);

static const float GHOST_GLOW = 0.18f;   // opal glow strength (stock glow is 1)
static const float GHOST_CORE = 0.04f;   // white core strength (stock core is 1)
static const float BANDS = 1.6f;         // opal bands along the blade

float4 main
(
	in float2 tcs_MAIN	: TEXCOORD0
)
: COLOR
{
	float4 result;

	//Sample color map
	float4 diffuseColor = tex2D(diffuseMap, tcs_MAIN);
	float  bloomStrength = 1.0f;

	//hue with texture factor 1, add white-hot core (stock)
	float3 stockColor = saturate(diffuseColor.rgb * textureFactor.rgb + diffuseColor.a);

	//ghostfire: 1 only for the dark ghostfire palette entries
	float brightest = max(textureFactor.r, max(textureFactor.g, textureFactor.b));
	float ghost = saturate((0.17f - brightest) * 100.0f);
	float phase = textureFactor.g * (255.0f / 32.0f);
	float angle = 6.2831853f * (tcs_MAIN.x * BANDS + phase);
	float s, c;
	sincos(angle, s, c);
	float3 opal = 0.65f + 0.35f * (c * float3(1.0f, -0.5f, -0.5f) + s * float3(0.0f, 0.8660254f, -0.8660254f));
	float glow = dot(diffuseColor.rgb, float3(0.3333333f, 0.3333333f, 0.3333333f));
	float3 ghostColor = saturate(glow * GHOST_GLOW * opal + diffuseColor.a * GHOST_CORE);

	diffuseColor.rgb = lerp(stockColor, ghostColor, ghost);
	diffuseColor.a = lerp(diffuseColor.a, diffuseColor.a * GHOST_CORE, ghost);

	//Bloom really blasts this so scale down the color
	if (bloomEnabled > 0.0f) 
		diffuseColor.rgb *= 0.6f;

	result.rgb = diffuseColor.rgb * alphaFadeOpacity;

	if (alphaFadeOpacityEnabled > 0.0f)
		result.a = bloomStrength * diffuseColor.a * alphaFadeOpacity;
	else
		result.a = bloomStrength * diffuseColor.a;

	return result;
}
