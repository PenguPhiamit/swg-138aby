//hlsl ps_2_0

#include "pixel_program/include/pixel_shader_constants.inc"
#include "pixel_program/include/functions.inc"

// The light whip's blade pixel program (L1, Claude, 18 Oct 2026). It is the O14 lightsaber blade program (the stock
// maths for every crystal colour, the ghostfire opal for palette entries 32-40) with one change: the white-hot core of
// a normal crystal is WHIP_CORE of the stock one, so a thin strand reads more in the crystal's colour. That change also
// gives the whip its own instruction stream, so the graphics hook (O15 effects layer) can tell a whip blade from a
// saber blade by the program's id.

sampler diffuseMap : register(s0);

static const float WHIP_CORE = 0.75f;    // white core of a normal crystal (stock is 1)
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

	//hue with texture factor 1, add the white-hot core (thinner than a saber's)
	float3 stockColor = saturate(diffuseColor.rgb * textureFactor.rgb + diffuseColor.a * WHIP_CORE);

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
