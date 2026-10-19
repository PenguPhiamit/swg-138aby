//hlsl ps_2_0

#include "pixel_program/include/pixel_shader_constants.inc"
#include "pixel_program/include/functions.inc"

// A swing trail that draws only for the Ossus ghostfire crystal (O14, Claude, 18 Oct 2026). Owner: "the ghostfire crystal
// also has no trails on the whip hilt", and the whip's rule "the trail; none without a specific crystal".
// A trail row with UseObjectHue 1 hands the blade's palette colour to the trail as its vertex colour (the trail's vertex
// program copies it unchanged). The ghostfire entries 32-40 are (0x20, g, 0x20) with g below 0x20; every crystal the
// server gives has its brightest channel at 0.65 or more, and the only one with red equal to blue is white (31), whose
// grey is excluded by g < r. For ghostfire the texture's own oil-slick colours draw, as the Ghostfire Lightsaber's
// strobe trail does (a_modulate on full white); for anything else the trail draws nothing.

sampler diffuseMap : register(s0);

static const float GAIN = 1.6f;  // owner, 9:10 PM, on the whip: "not enough trailing"

float4 main
(
	in float4 vertexColor : COLOR0,
	in float2 tcs_MAIN    : TEXCOORD0
)
: COLOR
{
	float4 texel = tex2D(diffuseMap, tcs_MAIN);

	float brightest = max(vertexColor.r, max(vertexColor.g, vertexColor.b));
	float ghost = saturate((brightest - 0.11f) * 200.0f) * saturate((0.14f - brightest) * 200.0f)
	            * saturate((0.012f - abs(vertexColor.r - vertexColor.b)) * 200.0f)
	            * saturate((vertexColor.r - vertexColor.g - 0.004f) * 400.0f);

	float4 result;
	result.rgb = saturate(texel.rgb * GAIN) * ghost;
	result.a = texel.a * vertexColor.a * alphaFadeOpacity * ghost;
	return result;
}
