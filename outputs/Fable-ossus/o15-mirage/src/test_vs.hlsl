// Ossus O15 harness (Claude, 18 Oct 2026): a stand-in for the client's blade vertex program (a_nolighting.vsh):
// the same mul(position, objectWorldCameraProjectionMatrix) with the default column-major packing, so c0-c3 and
// c4-c7 come out packed as in game (step 0 capture).
float4x4 objectWorldCameraProjectionMatrix : register(c0);

struct InputVertex
{
	float4 position : POSITION0;
	float4 color    : COLOR0;
	float2 uv       : TEXCOORD0;
};

struct OutputVertex
{
	float4 position : POSITION;
	float2 uv       : TEXCOORD0;
};

OutputVertex main(InputVertex i)
{
	OutputVertex o;
	o.position = mul(i.position, objectWorldCameraProjectionMatrix);
	o.uv = i.uv;
	return o;
}
