//hlsl ps_2_0

#include "pixel_program/include/pixel_shader_constants.inc"
#include "pixel_program/include/functions.inc"

// The saber swing trail every crafted saber shares (appearance/sw_light_saber_white.swh), for any crystal in any hilt
// (O14, Claude, 18 Oct 2026). Owner: "yes, it was supposed to be tied to the crystal, go in any hilt".
// The trail row's UseObjectHue 1 hands the crystal's palette colour to the trail as its vertex colour, and the trail
// fades its vertex alpha from the file's alpha to 0 over the file's life (its texture is the same all along the trail).
// The file now lasts 1.2 s at alpha 1 (stock: 0.06 s at alpha 0.5), and this program decides per crystal:
//  - every crystal the server gives (brightest channel 0.65 or more): the stock a_modulate2x result, drawn only over the
//    newest 5% of the trail (the stock 0.06 s) with the stock fade, so these trails look as before;
//  - the ghostfire crystal (palette 32-40, (0x20, g, 0x20) with g below r): the texture's own oil-slick strobe bars over
//    the whole 1.2 s, as the Ghostfire Lightsaber's strobe trail draws them.
// The texture keeps the stock trail's alpha (its profile across the blade); its colour holds the strobe bars. The stock
// texture's colour is white except in the faint edge texels, where it falls with the alpha: saturate(alpha * 6) here.

sampler diffuseMap : register(s0);

static const float STOCK_SHARE = 0.05f;  // 0.06 s of 1.2 s

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

	// stock: mul_x2 r0, t0, v0 with the file's alpha 0.5 fading over 0.06 s
	float3 stockRgb = saturate(saturate(texel.a * 6.0f) * vertexColor.rgb * 2.0f);
	float stockA = texel.a * saturate(1.0f - (1.0f - vertexColor.a) / STOCK_SHARE);

	float4 result;
	result.rgb = lerp(stockRgb, texel.rgb, ghost);
	result.a = lerp(stockA, texel.a * vertexColor.a, ghost) * alphaFadeOpacity;
	return result;
}
