/*=============================================================================
                                                           
 d8b 888b     d888 888b     d888 8888888888 8888888b.   .d8888b.  8888888888 
 Y8P 8888b   d8888 8888b   d8888 888        888   Y88b d88P  Y88b 888        
     88888b.d88888 88888b.d88888 888        888    888 Y88b.      888        
 888 888Y88888P888 888Y88888P888 8888888    888   d88P  "Y888b.   8888888    
 888 888 Y888P 888 888 Y888P 888 888        8888888P"      "Y88b. 888        
 888 888  Y8P  888 888  Y8P  888 888        888 T88b         "888 888        
 888 888   "   888 888   "   888 888        888  T88b  Y88b  d88P 888        
 888 888       888 888       888 8888888888 888   T88b  "Y8888P"  8888888888                                                                 
                                                                            
    Copyright (c) Pascal Gilcher. All rights reserved.
    
    * Unauthorized copying of this file, via any medium is strictly prohibited
 	* Proprietary and confidential

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.

===============================================================================

    RTGI 0.51

    Author:         Pascal Gilcher

    More info:      https://martysmods.com
                    https://patreon.com/mcflypg
                    https://github.com/martymcmodding  	

=============================================================================*/

/*=============================================================================
	Preprocessor settings
=============================================================================*/

/*=============================================================================
	UI Uniforms
=============================================================================*/

uniform int DIFFUSE_GI_Q <
	ui_type = "combo";
    ui_label = "Diffuse GI Quality";
	ui_items = "Off\0Low\0Medium\0High\0Ultra\0";
    ui_category = "Ray Tracing";
> = 3;

uniform int SPECULAR_GI_Q <
	ui_type = "combo";
    ui_label = "Specular GI Quality";
	ui_items = "Off\0Low\0Medium\0High\0Ultra\0";
    ui_category = "Ray Tracing";
> = 0;

uniform float RT_SAMPLE_RADIUS <
	ui_type = "drag";
	ui_min = 0.5; ui_max = 20.0;
    ui_step = 0.01;
    ui_label = "Diffuse GI Radius";
	ui_tooltip = "Maximum ray length, directly affects\nthe spread radius of shadows / bounce lighting";
    ui_category = "Ray Tracing";
> = 8.0;

uniform float RT_ROUGHNESS <
	ui_type = "drag";
	ui_min = 0.0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Surface Roughness";
	ui_tooltip = "BRDF surface roughness determines how glossy/matte the specular GI becomes.\nLower values result in more glossy reflections, higher values in more diffuse reflections.";
    ui_category = "Ray Tracing";
> = 0.2;

uniform float RT_Z_THICKNESS <
	ui_type = "drag";
	ui_min = 0.0; ui_max = 4.0;
    ui_step = 0.01;
    ui_label = "Z Thickness";
	ui_tooltip = "The shader can't know how thick objects are, since it only\nsees the side the camera faces and has to assume a fixed value.\n\nUse this parameter to remove halos around thin objects.";
    ui_category = "Ray Tracing";
> = 1.0;

uniform float RT_AO_AMOUNT <
	ui_type = "drag";
	ui_min = 0; ui_max = 10.0;
    ui_step = 0.01;
    ui_label = "Ambient Occlusion Intensity";
    ui_category = "Blending";
> = 10.0;

uniform float RT_IL_AMOUNT <
	ui_type = "drag";
	ui_min = 0; ui_max = 10.0;
    ui_step = 0.01;
    ui_label = "Diffuse Bounce Lighting Intensity";
    ui_category = "Blending";
> = 10.0;

uniform float RT_SPEC_AMOUNT <
	ui_type = "drag";
	ui_min = 0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Specular Lighting Intensity";
    ui_category = "Blending";
> = 1.0;

uniform float RT_AMBIENT_LEVEL <
	ui_type = "drag";
    ui_label = "Ambient Lighting Level";
	ui_min = 0.0; ui_max = 1.0;
	ui_tooltip = "Ambient Lighting intensity. Lower values remove constant light from the scene for RTGI to re-add dynamic light.";
    ui_category = "Blending";
> = 0.3;

uniform float RT_AMBIENT_SKY_MIX <
	ui_type = "drag";
    ui_label = "Ambient Lighting Sky Intensity";
	ui_min = 0.0; ui_max = 1.0;
	ui_tooltip = "How much of ambient is automatically detected skycolor.\nHigher values make the ambient color more dynamic.";
    ui_category = "Blending";
> = 0.5;

uniform float RT_FADE_DEPTH <
	ui_type = "drag";
    ui_label = "Fade Out Range";
	ui_min = 0.001; ui_max = 1.0;
	ui_tooltip = "Distance falloff, higher values increase RTGI draw distance.";
    ui_category = "Blending";
> = 0.3;

uniform bool ASSUME_SRGB_INPUT <
    ui_label = "Assume sRGB input";
    ui_tooltip = "Converts color to linear before converting to HDR.\nDepending on the game color format, this can improve light behavior and blending.";
    ui_category = "Experimental";
> = true;

uniform int RT_DEBUG_VIEW <
	ui_type = "combo";
    ui_label = "Enable Debug View";
	ui_items = "None\0Lighting Channel\0 3-Way Split\0";
	ui_tooltip = "Different debug outputs";
    ui_category = "Debug";
> = 0;

/*
uniform float4 tempF1 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF2 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF3 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF4 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF5 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF6 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);
uniform bool debug_key_down < source = "key"; keycode = 0x47; mode = ""; >;
*/

/*=============================================================================
	Textures, Samplers, Globals, Structs
=============================================================================*/

//do NOT change anything here. "hurr durr I changed this and now it works"
//you ARE breaking things down the line, if the shader does not work without changes
//here, it's by design.

uniform uint  FRAMECOUNT  < source = "framecount"; >;
uniform float FRAMETIME   < source = "frametime";  >;

texture ColorInputTex : COLOR;
texture DepthInputTex : DEPTH;
sampler ColorInput 	{ Texture = ColorInputTex; };
sampler DepthInput  { Texture = DepthInputTex; };

#include ".\MartysMods\mmx_global.fxh"
#include ".\MartysMods\mmx_depth.fxh"
#include ".\MartysMods\mmx_math.fxh"
#include ".\MartysMods\mmx_qmc.fxh"
#include ".\MartysMods\mmx_deferred.fxh"
#include ".\MartysMods\mmx_camera.fxh"
#include ".\MartysMods\mmx_sampling.fxh"
#include ".\MartysMods\mmx_noise.fxh"

//log2 macro for uints up to 16 bit, inefficient in runtime but preprocessor doesn't care
#define T1(x,n) ((uint(x)>>(n))>0)
#define T2(x,n) (T1(x,n)+T1(x,n+1))
#define T4(x,n) (T2(x,n)+T2(x,n+2))
#define T8(x,n) (T4(x,n)+T4(x,n+4))
#define LOG2(x) (T8(x,0)+T8(x,8))

//#undef _COMPUTE_SUPPORTED

#define CEIL_DIV(num, denom) ((((num) - 1) / (denom)) + 1)

texture RTGI_RadianceTex                     { Width = BUFFER_WIDTH/6;   Height = BUFFER_HEIGHT/6; Format = RGBA16F; };
sampler sRTGI_RadianceTex                    { Texture = RTGI_RadianceTex; };

texture RTGI_JitterTex                    < source = "iMMERSE_bluenoise_temporal.png"; > { Width = 128*30; Height = 128; Format = RGBA8; };
sampler	sRTGI_JitterTex                  { Texture = RTGI_JitterTex; AddressU = WRAP; AddressV = WRAP; };

texture RTGI_ZSrc                    { Width = BUFFER_WIDTH;     Height = BUFFER_HEIGHT;   Format = R16F; MipLevels = 3;   };
sampler sRTGI_ZSrc                   { Texture = RTGI_ZSrc; /*MinFilter=POINT; MipFilter=POINT; MagFilter=POINT;*/};
#define DEINT_TILES             uint2(1, 1)
#define ZTexture                sRTGI_ZSrc

texture RTGI_Aux0  { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
texture RTGI_Aux1  { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
texture RTGI_Aux2  { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
texture RTGI_Aux3  { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
texture RTGI_Accum { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };

texture RTGI_Guide      { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; MipLevels = 4; };//xy = m1, m2, history length, ggx roughness :yeahboii:
texture RTGI_GuidePrev  { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; MipLevels = 4; };

texture RTGI_RTGI_RadianceTex { Width = BUFFER_WIDTH/6;   Height = BUFFER_HEIGHT/6; Format = RGBA16F; };

sampler sRTGI_Aux0 { Texture = RTGI_Aux0; };
sampler sRTGI_Aux1 { Texture = RTGI_Aux1; MinFilter=POINT; MipFilter=POINT; MagFilter=POINT;}; //for demux, important for filter
sampler sRTGI_Aux2 { Texture = RTGI_Aux2; };
sampler sRTGI_Aux3 { Texture = RTGI_Aux3; };
sampler sRTGI_Accum { Texture = RTGI_Accum; };

sampler sRTGI_Guide { Texture = RTGI_Guide; };
sampler sRTGI_GuidePrev { Texture = RTGI_GuidePrev; };

sampler sRTGI_RTGI_RadianceTex { Texture = RTGI_RTGI_RadianceTex; };

#if _COMPUTE_SUPPORTED
storage stRTGI_Aux0 { Texture = RTGI_Aux0; };
storage stRTGI_ZSrc                  { Texture = RTGI_ZSrc;             };
#endif

texture RTGI_IBLTex { Width = 32; Height = 32; Format = RGBA16F; MipLevels = 6;};
sampler sRTGI_IBLTex { Texture = RTGI_IBLTex;};

struct VSOUT
{
    float4 vpos : SV_Position;
    float2 uv   : TEXCOORD0;
};

struct CSIN 
{
    uint3 groupthreadid     : SV_GroupThreadID;         
    uint3 groupid           : SV_GroupID;            
    uint3 dispatchthreadid  : SV_DispatchThreadID;     
    uint threadid           : SV_GroupIndex;
};

struct RayDesc 
{
    float3 origin;
    float3 pos;
    float3 dir;
    float2 uv;
    float length;    
};

/*=============================================================================
	Functions
=============================================================================*/

float2 pixel_idx_to_uv(uint2 pos, float2 texture_size)
{
    float2 inv_texture_size = rcp(texture_size);
    return pos * inv_texture_size + 0.5 * inv_texture_size;
}

bool check_boundaries(uint2 pos, uint2 dest_size)
{
    return all(pos < dest_size) && all(pos >= uint2(0, 0));
}

uint2 deinterleave_pos(uint2 pos, uint2 tiles, uint2 gridsize)
{
    int2 blocksize = CEIL_DIV(gridsize, tiles); 
    int2 block_id     = pos % tiles;
    int2 pos_in_block = pos / tiles;
    return block_id * blocksize + pos_in_block;
}

uint2 reinterleave_pos(uint2 pos, uint2 tiles, uint2 gridsize)
{
    int2 blocksize = CEIL_DIV(gridsize, tiles); 
    int2 block_id     = pos / blocksize;  
    int2 pos_in_block = pos % blocksize;
    return pos_in_block * tiles + block_id;
}

float3 srgb_to_acescg(float3 srgb)
{
    float3x3 m = float3x3(  0.613097, 0.339523, 0.047379,
                            0.070194, 0.916354, 0.013452,
                            0.020616, 0.109570, 0.869815);
    return mul(m, srgb);           
}

float3 acescg_to_srgb(float3 acescg)
{     
    float3x3 m = float3x3(  1.704859, -0.621715, -0.083299,
                            -0.130078,  1.140734, -0.010560,
                            -0.023964, -0.128975,  1.153013);                 
    return mul(m, acescg);            
}

float3 cone_overlap(float3 c)
{
    float k = 0.7 * 0.33;
    float2 f = float2(1 - 2 * k, k);
    float3x3 m = float3x3(f.xyy, f.yxy, f.yyx);
    return mul(c, m);
}

float3 cone_overlap_inv(float3 c)
{
    float k = 0.7 * 0.33;
    float2 f = float2(k - 1, k) * rcp(3 * k - 1);
    float3x3 m = float3x3(f.xyy, f.yxy, f.yyx);
    return mul(c, m);
}

float3 unpack_hdr(float3 color)
{
    color  = saturate(color);   
    if(ASSUME_SRGB_INPUT) color = color*0.283799*((2.52405+color)*color);    
    color = srgb_to_acescg(color);
    color = color * rcp(1.04 - saturate(color));    
    return color;
}

float3 pack_hdr(float3 color)
{
    color =  1.04 * color * rcp(color + 1.0);   
    color = acescg_to_srgb(color);    
    color  = saturate(color);   
    if(ASSUME_SRGB_INPUT) color = 1.14374*(-0.126893*color+sqrt(color));
    return color;     
}


float3 linear_to_ycocg(float3 color)
{
    float Y  = dot(color, float3(0.25, 0.5, 0.25));
    float Co = dot(color, float3(0.5, 0.0, -0.5));
    float Cg = dot(color, float3(-0.25, 0.5, -0.25));
    return float3(Y, Co, Cg);
}

float3 ycocg_to_linear(float3 color)
{
    float t = color.x - color.z;
    float3 r;
    r.y = color.x + color.z;
    r.x = t + color.y;
    r.z = t - color.y;
    return max(r, 0.0);
}

//Co Cg Y Y^2
float4 encode_hdr_to_filter(float3 color)
{
    color = acescg_to_srgb(color);
    color = linear_to_ycocg(color);
    return float4(color.gbr, color.r * color.r);
}

float3 decode_hdr_from_filter(float3 color)
{
    float3 res = color.brg;
    res = ycocg_to_linear(res);
    res = srgb_to_acescg(res);
    return res;
}

float3 convert_gi_to_lighting(float4 raw_data, bool is_spec)
{
    if(is_spec) return raw_data.rgb * RT_SPEC_AMOUNT * RT_SPEC_AMOUNT;

    float4 skytex = tex2Dlod(sRTGI_IBLTex, 0.5.xx, 7);
    float3 skylight = skytex.rgb / max(1e-5, skytex.w);
    skylight *= saturate(skytex.w / 0.1);

    float3 ambient = lerp(1.0, skylight, saturate(RT_AMBIENT_SKY_MIX)) * saturate(RT_AMBIENT_LEVEL);
    float3 lighting = ambient * (1.0 - raw_data.w * saturate(RT_AO_AMOUNT * 0.1)) + raw_data.rgb * RT_IL_AMOUNT * RT_IL_AMOUNT * 2;
    //lighting = rcp(1 + raw_data.w * RT_AO_AMOUNT * 2) * (1 + raw_data.rgb * RT_IL_AMOUNT * RT_IL_AMOUNT * 3);
    return lighting;
}

float2 get_jitter(uint2 texelpos, uint framecount)
{
    const uint dim_xy = 128;
    const uint dim_t = 30;
    uint2 texel_in_tile = texelpos % dim_xy;
    texel_in_tile.x += dim_xy * (framecount % dim_t);
    return tex2Dfetch(sRTGI_JitterTex, texel_in_tile).xy;
}

float4 get_gbuffer(float2 uv)
{
    return float4(Deferred::get_normals(uv), Camera::depth_to_z(Depth::get_linear_depth(uv)));
}

//do not call after temporal reproject
float4 get_gbuffer_prev(float2 uv)
{
    return tex2Dlod(sRTGI_Aux3, uv, 0);
}

struct TraceContext
{
    float4 uv;
    uint4 texel; //xy: working pos, zw: write pos
    uint2 tile;
    float3 pos; //view space position
    float3 normal;
    float3 viewdir;
    float depth;
};

TraceContext init(in uint2 working_pos, in uint2 working_size)
{
    const uint2 tile_size = CEIL_DIV(working_size, DEINT_TILES);

    TraceContext o;   
    o.texel.xy = working_pos;
    o.texel.zw = working_pos;
    o.tile = o.texel.xy / tile_size;
    o.uv.xy = pixel_idx_to_uv(o.texel.xy, working_size); 
    o.uv.zw = pixel_idx_to_uv(o.texel.zw, working_size); 

    o.depth = Depth::get_linear_depth(o.uv.zw);

    o.pos = Camera::uv_to_proj(o.uv.zw, Camera::depth_to_z(o.depth));
    o.normal = Deferred::get_normals(o.uv.zw);
    o.viewdir = normalize(o.pos);

    o.pos *= 0.996; //bias 
   // o.pos += o.normal * depth;

    return o;
}

// GGX NDF is sort of a probability density function for normals
// cos(theta) = microfacet normal Z
// Integral[GGX_NDF(alpha, theta) * cos(theta)] d theta from 0 to pi/2 = average .z of microfacet normal
// this yields a function that converts alpha to average .z of microfacet normal

// If we assume the normal map _being_ those microfacet normals, we can do the inverse, get alpha from normal.z
// Averaging a normal map yields a vector that should have N.xy = 0 (since the inclinations should cancel out)
// but N.z <= 1. For a perfect mirror the average normal is (0,0,1), for a rough surface, Z is shorter

// Inverting the function that converts alpha to average N.z yields the following snippet
// However the function seems to be not invertible, thus we need an approximation that we can invert
float normal_height_to_ggx_alpha(float z)
{
    //alpha to N.z approx: 
    // rsqrt(1 + 1.205 * alpha^2 + 0.278 * alpha^4)
    //inverse:

    z *= z;
    z = max(z, 1e-7);
    return 0.7071 * sqrt(sqrt(18.7882 - 14.3885 * (z - 1.0) / z) - 4.334532);
}

float spec_half_angle_from_alpha(float alpha)
{
    return PI * alpha / (1 + alpha);
}

float get_alpha()
{
    return saturate(RT_ROUGHNESS * RT_ROUGHNESS);
}

float3 ray_hemi_cosine(float2 u, float3 n)
{
    float3 dir;
    sincos(u.x * TAU,  dir.y,  dir.x);      
    dir.z = u.y * 2.0 - 1.0; 
    dir.xy *= sqrt(1.0 - dir.z * dir.z);
    return normalize(dir + n); 
}

float3 ggx_vndf(float2 u, float3 wi, float alpha)
{
    float3 wi_std = normalize(float3(wi.xy * alpha, wi.z));   
    float s = 1.0 + sqrt(saturate(1.0 - wi.z * wi.z)); //1 + length(wi.xy)

    float a2 = alpha * alpha;
    float s2 = s * s;
    float k = (s2 - s2 * a2) / (s2 + a2 * (wi.z * wi.z));//restructured to get MADDs in both numerator and denominator
    float b = wi.z > 0.0 ? k * wi_std.z : wi_std.z;  

    //b = wi_std.z; //old spherical cap sampling

    float3 c;
    c.z = mad(-u.y * 0.9, 1 + b, 1); //kill least likely samples
    sincos(TAU * u.x, c.y, c.x);
    c.xy *= sqrt(saturate(1.0 - c.z * c.z)); //sin theta
	
	float3 wm_std = c + wi_std;
    return normalize(float3(wm_std.xy * alpha, wm_std.z));
}

float lambda_smith(float ndotx, float alpha)
{    
    float alpha_sqr = alpha * alpha;
    float ndotx_sqr = ndotx * ndotx;
    return (-1.0 + sqrt(alpha_sqr * (1.0 - ndotx_sqr) / ndotx_sqr + 1.0)) * 0.5;
}

float smith_G1(float ndotv, float alpha)
{
	float lambda_v = lambda_smith(ndotv, alpha);
	return 1.0 / (1.0 + lambda_v);
}

float smith_G2(float ndotl, float ndotv, float alpha) //height correlated
{
	float lambda_v = lambda_smith(ndotv, alpha);
	float lambda_l = lambda_smith(ndotl, alpha);
	return 1.0 / (1.0 + lambda_v + lambda_l);
}

//Needs this because DX9 is a jackass and doesn't have bitwise ops... so emulate them with floats
bool bitfield_get(float bitfield, int bit)
{
    float state = floor(bitfield * exp2(-bit)); //"right shift"
    return frac(state * 0.5) > 0.25; //"& 1"
}

void bitfield_set(inout float bitfield, int bit, bool value)
{
    bool is_set = bitfield_get(bitfield, bit);
    bitfield += exp2(bit) * (value - is_set);    
}

//tried many things like LUTs, or'ing bits 4 at a time and what not, the stupid and straightforward approach is best
float bitfield_set_bits(float bitfield, int start, int stride, out float num_changed)
{ 
    num_changed = 0;
    [loop]
    for(int bit = start; bit < start + stride; bit++)
    {
        bool is_set = bitfield_get(bitfield, bit);
        num_changed += 1.0 - is_set;
        bitfield += exp2(bit) * (1.0 - is_set); 
    }
       
    return bitfield;
}

float bitfield_countones(float bitfield)
{  
    float sum = 0;
    [loop]
    for(int bit = 0; bit < 24; bit++)
        sum += bitfield_get(bitfield, bit);
    return sum;
}

float get_fade_factor(float depth)
{
    float fade = saturate(1 - depth * depth); //fixed fade that smoothly goes to 0 at depth = 1
    depth /= RT_FADE_DEPTH;
    fade *= saturate(depth * 1024.0);
    return fade * saturate(exp2(-depth * depth)); //overlaying regular exponential fade
}

float4 bilinear_split(float2 uv, float2 texsize)
{
    return float4(floor(uv * texsize - 0.5), frac(uv * texsize - 0.5));
}

float4 get_bilinear_weights(float4 bilinear)
{
    float4 w = float4(bilinear.zw, 1 - bilinear.zw);
    return w.zxzx * w.wwyy;
}

/*=============================================================================
	Shader Entry Points
=============================================================================*/

VSOUT MainVS(in uint id : SV_VertexID)
{
    VSOUT o;
    FullscreenTriangleVS(id, o.vpos, o.uv); 
    return o;
}

void AlbedoInputPS(in VSOUT i, out float4 o : SV_Target0)
{        
    o = 0;    
    [unroll]for(int x = -2; x <= 2; x++)
    [unroll]for(int y = -2; y <= 2; y++)
    {
        float2 tuv = i.uv + BUFFER_PIXEL_SIZE * 2 * float2(x, y);       
        float3 color = tex2D(ColorInput, tuv).rgb;
        o += color;
    }        
    o /= 25.0;     
    o.rgb = unpack_hdr(o.rgb);
    o.a = Depth::get_linear_depth(i.uv) < 0.999; //sky
}

#if _COMPUTE_SUPPORTED
void DepthLinearizeCS(in CSIN i)
{
    if(!check_boundaries(i.dispatchthreadid.xy * 2, BUFFER_SCREEN_SIZE)) return;

    float2 uv = pixel_idx_to_uv(i.dispatchthreadid.xy * 2, BUFFER_SCREEN_SIZE);
    float2 corrected_uv = Depth::correct_uv(uv); //fixed for lookup 

#if RESHADE_DEPTH_INPUT_IS_UPSIDE_DOWN
    corrected_uv.y -= BUFFER_PIXEL_SIZE.y * 0.5;    //shift upwards since gather looks down and right
    float4 depth_texels = tex2DgatherR(DepthInput, corrected_uv).wzyx;  
#else
    float4 depth_texels = tex2DgatherR(DepthInput, corrected_uv);
#endif

    depth_texels = Depth::linearize(depth_texels);
    depth_texels.x = Camera::depth_to_z(depth_texels.x);
    depth_texels.y = Camera::depth_to_z(depth_texels.y);
    depth_texels.z = Camera::depth_to_z(depth_texels.z);
    depth_texels.w = Camera::depth_to_z(depth_texels.w);

    //offsets for xyzw components
    const uint2 offsets[4] = {uint2(0, 1), uint2(1, 1), uint2(1, 0), uint2(0, 0)};

    [unroll]
    for(uint j = 0; j < 4; j++)
    {
        uint2 write_pos = i.dispatchthreadid.xy * 2 + offsets[j];
        tex2Dstore(stRTGI_ZSrc, write_pos, depth_texels[j]);
    }
}
#else
void DepthLinearizePS(in VSOUT i, out float o : SV_Target0)
{ 
    o = Camera::depth_to_z(Depth::get_linear_depth(i.uv));
}
#endif

float spline(float l)
{
    //return exp2(10.0 * (l - 1));
    return l * l * (2 - l);
    //return lerp(l, l*l*l*l, 0.75); 
    //return l;
}

float trace_ray_dda(inout RayDesc ray, inout TraceContext ctx, in float3 rand, in float maxT, bool do_backpass, int max_steps, float alpha)
{    
    float cosv = dot(ray.dir, ctx.viewdir);
    float hit_tolerance = RT_Z_THICKNESS * RT_Z_THICKNESS * (1 + abs(cosv)) * 8 + 2;
    hit_tolerance *= 1 + alpha * 3; //higher roughness, we want safer hits
    if(!do_backpass) hit_tolerance = 99999.0;  

    ray.origin = ctx.pos;
    float2 dir_uv = Camera::proj_to_uv(ray.origin + ray.dir * 0.05) - ctx.uv.xy;
    float2 limit_uv = Math::aabb_hit_01(ctx.uv.xy, dir_uv);

    float length_2D = length((limit_uv - ctx.uv.xy) * BUFFER_ASPECT_RATIO.yx);
    float incT = rcp(ceil(length_2D * max_steps));
    float curr_t = incT * rand.z; 

    float A = dot(ray.origin, ray.dir);

    int steps = ceil(length_2D * max_steps);
    bool hit = false;

    [loop]
    for(int j = 0; j < steps; j++)
    {
        float t = (j + rand.z) / steps;
        ray.uv = lerp(ctx.uv.xy, limit_uv, spline(t));

        float3 pos = Camera::uv_to_proj(ray.uv, tex2Dlod(ZTexture, ray.uv, int(log2(length_2D * BUFFER_WIDTH) - 10.0)).x);

        //Pascal's DDA v5 '23
        float B = dot(pos, ray.dir);
        float C = dot(pos, ray.origin);
        float D = dot(pos, pos);       

        ray.length = (B * C - D * A)  * rcp(D - B * B);

        float ray_z = ray.origin.z + ray.dir.z * ray.length;
        float delta = pos.z - ray_z;

        float z_tolerance = (ray.length + 0.1) * hit_tolerance; 
        if(abs(delta * 2.0 + z_tolerance + 0.05) < z_tolerance)
        {
            hit = true; 
            ray.dir = normalize(pos - ray.origin);
            break;
        }
    }

    return hit;
}

float4 trace_specular(TraceContext ctx)
{
    if(SPECULAR_GI_Q == 0 || get_fade_factor(ctx.depth) < 1e-5) return 0;

    float4 jitter;
    jitter.xy = get_jitter(ctx.texel.xy, FRAMECOUNT);
    jitter.zw = get_jitter(ctx.texel.xy + 64, FRAMECOUNT + 15); 

    float alpha = get_alpha(); 
    static const int quality_preset_rays[5] = {0, 1, 2, 3, 4};//you think you want to tamper with this, but you don't
    int num_rays = quality_preset_rays[SPECULAR_GI_Q];
    int num_steps = 32 + 64 * (1-alpha); //higher roughness means less accurate light but lower performance due to thread divergence, reduce samples     

    float maxT = RT_SAMPLE_RADIUS * RT_SAMPLE_RADIUS;
    float3 strat = QMC::get_stratificator(num_rays);    

    float3x3 tbn = Math::base_from_vector(ctx.normal);
    float3 v_t = mul(tbn, -ctx.viewdir);
    float ndotv = saturate(v_t.z - 0.001) + 0.001;
    float G1 = smith_G1(ndotv, alpha) + 1e-5; 

    float4 spec_sum = 0;

    [loop]
    for(int r = 0; r < num_rays; r++)    
    {
        float3 rand = QMC::roberts3(r, jitter.xyz);
        rand.xy = QMC::get_stratified_sample(rand.yx, strat, r);
        RayDesc ray;

        float3 h_t = ggx_vndf(rand.xy, v_t, alpha); //microfacet normal, ggx distribution
        float vdoth = dot(v_t, h_t);   
        //float fresnel = 0.04 + (1.0 - 0.04) * pow(saturate(1 - vdoth), 5); 
        float fresnel = 0.04 + (1.0 - 0.04) * exp2((-5.55473 * vdoth - 6.98316) * vdoth);

        //Specular
        {
            //reflect view dir over microfacet normal, then back from tangent space         
            float3 l_t = reflect(-v_t, h_t);
            ray.dir = mul(l_t, tbn);           

            //float hit = trace_ray_refine(ray, ctx, rand, maxT, true) * saturate(ray.dir.z + 1);  
            float hit = trace_ray_dda(ray, ctx, rand, maxT, true, num_steps, alpha) * saturate(ray.dir.z);

            float ndotl = saturate(l_t.z);
            float G2 = smith_G2(ndotl, ndotv, alpha);   //Masking-shadowing  
            float estimator = G2 * fresnel; // / G1 moved out of loop!

            if(isnan(estimator)) estimator = 0; 

            estimator *= saturate(1 + ray.dir.z);           

            [branch]
            if(hit > 0.01)
            {    
                float3 hit_n = Deferred::get_normals(ray.uv);
                float facing = saturate(dot(-hit_n, ray.dir) * 32);
               // float4 irradiance = float4(unpack_hdr(tex2Dlod(ColorInput, ray.uv, 0).rgb), 1); //
                float4 irradiance = tex2Dlod(sRTGI_RadianceTex, ray.uv, 0);
                irradiance.w = 1;
                spec_sum += float4(irradiance.rgb * irradiance.w * facing, 1.0) * estimator * hit;      
            }               
        }   
    }

    spec_sum /= num_rays;
    spec_sum /= G1;
    return spec_sum;
}

float spline2(float l)
{
    return exp2(10.0 * (l - 1));      
}

float4 trace_diffuse(TraceContext ctx)
{
    if(DIFFUSE_GI_Q == 0 || get_fade_factor(ctx.depth) < 1e-5) return 0;

    float4 jitter;
    jitter.xy = get_jitter(ctx.texel.xy, FRAMECOUNT);
    jitter.zw = get_jitter(ctx.texel.xy + 64, FRAMECOUNT + 15);

    float4 rtgi = 0;

    static const int quality_preset_rays[5] = {0, 1, 2, 4, 5};//you think you want to tamper with this, but you don't
    static const int quality_preset_steps[5] = {0, 16, 16, 24, 72};//you think you want to tamper with this, but you don't    
    
    uint slice_count  = quality_preset_rays[DIFFUSE_GI_Q];    
    uint sample_count = quality_preset_steps[DIFFUSE_GI_Q]; 

    float3 slice_dir = 0; sincos(jitter.x * PI / slice_count, slice_dir.x, slice_dir.y);  
    float4 slice_rotator = Math::get_rotator(PI / slice_count);

    float worldspace_radius = RT_SAMPLE_RADIUS * RT_SAMPLE_RADIUS * 0.5;
    float screenspace_radius = worldspace_radius / ctx.pos.z * 0.5;

    float visibility = 0;
    float slicesum = 0;  
    float T = 0.25 * worldspace_radius * RT_Z_THICKNESS * RT_Z_THICKNESS;  //arbitrary thickness that looks good relative to sample radius  
    float falloff_factor = rcp(worldspace_radius);
    falloff_factor *= falloff_factor;

    static const float4 texture_scale = float4(1.0.xx / DEINT_TILES, 1.0.xx) * BUFFER_ASPECT_RATIO.xyxy;

    float3 v = -ctx.viewdir;
    float3 n = ctx.normal;

    [loop]
    while(slice_count-- > 0) //1 less register and a bit faster
    {        
        slice_dir.xy = Math::rotate_2D(slice_dir.xy, slice_rotator);
        float3 ortho_dir = slice_dir - dot(slice_dir.xy, v.xy) * v; //z = 0 so no need for full dot3
        
        float3 slice_n = cross(slice_dir, v); 
        slice_n *= rsqrt(dot(slice_n, slice_n));   

        float4 scaled_dir = (slice_dir.xy * screenspace_radius).xyxy * texture_scale; 

        float3 n_proj_on_slice = n - slice_n * dot(n, slice_n);
        float sliceweight = sqrt(dot(n_proj_on_slice, n_proj_on_slice));
          
        float cosn = saturate(dot(n_proj_on_slice, v) * rcp(sliceweight));
        float normal_angle = Math::fast_acos(cosn) * Math::fast_sign(dot(ortho_dir, n_proj_on_slice));

#if _COMPUTE_SUPPORTED
        uint occlusion_bitfield = 0xFFFFFFFF;
#else
        float occlusion_bitfield = 0; 
#endif

        [unroll]
        for(int side = 0; side < 2; side++)
        {            
            [loop]         
            for(int _sample = 0; _sample < sample_count; _sample++)
            {
                float rand = QMC::roberts1(slice_count * 2 + side, jitter.y);
                float s = (_sample + rand) / sample_count;               
                s = spline2(s);

                int mip = min(3, int(log2(s * screenspace_radius * BUFFER_WIDTH) - 5.0));

                float4 tap_uv = ctx.uv + s * scaled_dir;
                if(!all(saturate(tap_uv.zw - tap_uv.zw * tap_uv.zw))) break;
                float zz = tex2Dlod(ZTexture, tap_uv.xy, mip).x;

                float3 deltavec = Camera::uv_to_proj(tap_uv.zw, zz) - ctx.pos;

                float ddotv = dot(deltavec, v);
                float ddotd = dot(deltavec, deltavec);
                float2 h_frontback = float2(ddotv, ddotv - T) * rsqrt(float2(ddotd, ddotd - 2 * T * ddotv + T * T));

                h_frontback = Math::fast_acos(h_frontback);
                h_frontback = side ? h_frontback : -h_frontback.yx;//flip sign and sort in the same cmov, efficiency baby!
                h_frontback = saturate((h_frontback + normal_angle) / PI + 0.5);
                //h_frontback = h_frontback * h_frontback * (3.0 - 2.0 * h_frontback);               
#if _COMPUTE_SUPPORTED
                uint a = uint(h_frontback.x * 32);
                uint b = ceil(saturate(h_frontback.y - h_frontback.x) * 32); //ceil? using half occlusion here
                uint occlusion = ((1 << b) - 1) << a;                
                
                uint local_bitfield = occlusion_bitfield & ~occlusion;
                uint changed_bits = local_bitfield ^ occlusion_bitfield;
#else 
                uint a = floor(h_frontback.x * 24);
                float changed_bits;
                uint b = floor(saturate(h_frontback.y - h_frontback.x) * 25.0); //haven't figured out why this needs to be one more (gives artifacts otherwise) but whatever, somethingsomething float inaccuracy
                float local_bitfield = bitfield_set_bits(occlusion_bitfield, a, b, changed_bits);
#endif
                [branch]
                if(changed_bits > 0)
                {
#if _COMPUTE_SUPPORTED
                    float hit = saturate(countbits(changed_bits) / 32.0) * sliceweight;
#else 
                    float hit = saturate(changed_bits / 24.0) * sliceweight;
#endif
                    rtgi.w += hit;
  
                    [branch]
                    if(dot(deltavec, ctx.normal) > 0)
                    {
                        float3 hit_n = Deferred::get_normals(tap_uv.zw);
                        float facing = saturate(dot(-hit_n, deltavec) * rsqrt(ddotd)); //horizon math does not include cosine term for emitter
                        float4 albedofetch = tex2Dlod(sRTGI_RadianceTex, tap_uv.zw, 0);
                        float3 albedo = albedofetch.rgb * albedofetch.a * facing; //mask out sky                         
                        rtgi.rgb += albedo * hit;
                    }                    
                }               
                occlusion_bitfield = local_bitfield;
            }        
            scaled_dir = -scaled_dir;
        }

        slicesum += sliceweight;
    }

    rtgi /= slicesum;
    return rtgi;
}


uint2 screen_to_checkerboard(uint2 p)
{
    p.x *= 2;
    p.x += p.y % 2;
    return p;
}

uint2 checkerboard_to_screen(uint2 p)
{
    p.x -= p.y % 2;
    p.x /= 2;
    return p;
}

#if _COMPUTE_SUPPORTED
void TraceWrapSpecularCS(in CSIN i)
{ 
    uint2 tpos = screen_to_checkerboard(i.dispatchthreadid.xy);

    if(!check_boundaries(tpos.xy, BUFFER_SCREEN_SIZE)) 
        return;

    TraceContext ctx = init(tpos, BUFFER_SCREEN_SIZE);
    float4 spec_sum = trace_specular(ctx);
    float4 tostore = float4(convert_gi_to_lighting(spec_sum,  true), ctx.depth);

    tex2Dstore(stRTGI_Aux0, i.dispatchthreadid.xy + uint2(BUFFER_WIDTH / 2, 0), tostore);
}   

void TraceWrapDiffuseCS(in CSIN i)
{
    uint2 tpos = screen_to_checkerboard(i.dispatchthreadid.xy);

    if(!check_boundaries(tpos, BUFFER_SCREEN_SIZE)) 
        return; 
    
    TraceContext ctx = init(tpos, BUFFER_SCREEN_SIZE);
    float4 diff_sum = trace_diffuse(ctx);
    float4 tostore = float4(convert_gi_to_lighting(diff_sum,  false), ctx.depth);
    tex2Dstore(stRTGI_Aux0, i.dispatchthreadid.xy, tostore);
}

#else  //_COMPUTE_SUPPORTED

void TraceWrapSpecularPS(in VSOUT i, out float4 o : SV_Target0)
{
    i.vpos.xy = floor(i.vpos.xy);
    i.vpos.x *= 2;

    i.vpos.x -= BUFFER_SCREEN_SIZE.x;

    if(i.vpos.x < 0) discard;

    TraceContext ctx = init(i.vpos.xy, BUFFER_SCREEN_SIZE);  

    float4 spec_sum = trace_specular(ctx);
    o = float4(convert_gi_to_lighting(spec_sum,  true), ctx.depth);
}

void TraceWrapDiffusePS(in VSOUT i, out float4 o : SV_Target0)
{
    i.vpos.xy = floor(i.vpos.xy);
    i.vpos.x *= 2;

    if(i.vpos.x >= BUFFER_SCREEN_SIZE.x) discard;

    TraceContext ctx = init(i.vpos.xy, BUFFER_SCREEN_SIZE);    

    float4 diff_sum = trace_diffuse(ctx);
    o = float4(convert_gi_to_lighting(diff_sum,  false), ctx.depth);
}

#endif //_COMPUTE_SUPPORTED

void AccumPS(in VSOUT i, out PSOUT2 o)
{
    uint2 p = uint2(i.vpos.xy);
    bool is_specular = p.x >= BUFFER_WIDTH/2;
    p.x %= BUFFER_WIDTH/2;

    p.x *= 2;
    p.x += p.y % 2;

    //fullscreen UV of checkerboarded grid
    float2 uv = pixel_idx_to_uv(p, BUFFER_SCREEN_SIZE);
    float4 curr_gbuffer = get_gbuffer(uv);  

    float2 prev_coord = p + Deferred::get_motion(uv) * BUFFER_SCREEN_SIZE + float2(0.5, 0);//I have no idea why the +0.5 is needed...
    float alpha = get_alpha();       

    bool valid_history = all(prev_coord > 0) && all(prev_coord < BUFFER_SCREEN_SIZE);
    valid_history = get_fade_factor(Camera::z_to_depth(curr_gbuffer.w)) < 1e-5 ? false : valid_history;

    float2 subpixel = frac(prev_coord);
    float4 w_bilinear = float4(subpixel, 1 - subpixel);
    w_bilinear = w_bilinear.zxzx * w_bilinear.wwyy;

    int2 shift = is_specular ? int2(BUFFER_WIDTH / 2, 0) : int2(0, 0);

    float4 prev_sample = 0;
    float2 prev_moments = 0;

    [branch]
    if(valid_history)
    {       
        float halfangle = spec_half_angle_from_alpha(alpha);
        float spec_relaxant = rcp(1 + degrees(halfangle)); 

        float sum_w = 0;       

        [unroll]for(int y = 0; y < 2; y++)
        [unroll]for(int x = 0; x < 2; x++)
        {
            int2 offset = int2(x, y);
            uint2 prev_coord = uint2(prev_coord) + offset;

            float4 tap_gbuffer = tex2Dfetch(sRTGI_Aux3,      prev_coord);
            float4 tap_sample  = tex2Dfetch(sRTGI_Accum,     checkerboard_to_screen(prev_coord) + shift);
            float2 tap_moments = tex2Dfetch(sRTGI_GuidePrev, checkerboard_to_screen(prev_coord) + shift).xy;

            float w_z = abs(tap_gbuffer.w - curr_gbuffer.w) / max3(tap_gbuffer.w, curr_gbuffer.w, 1e-6);
            w_z       = exp2(-w_z * 32.0);

            float w_n = dot(curr_gbuffer.xyz, tap_gbuffer.xyz);
            w_n       = Math::fast_acos(saturate(w_n));
            w_n       = smoothstep(1.0, 0.5, degrees(w_n) * spec_relaxant); 

            float w_geometry = is_specular ? w_n : w_z;
            prev_moments += tap_moments * w_bilinear[y * 2 + x]; //bilinear, no normalization needed
            prev_sample  += tap_sample  * w_bilinear[y * 2 + x] * w_geometry;
            sum_w        +=               w_bilinear[y * 2 + x] * w_geometry;
        }

        if(is_specular)
        {
            valid_history = sum_w < 0.45 ? false : valid_history; //must be lower than 0.5! BAK Test 6 Wayne Manor
        }
        else 
        {
            valid_history = sum_w < 0.1 ? false : valid_history;
        }

        prev_sample /= max(1e-7, sum_w);
    }

    float4 curr = tex2D(sRTGI_Aux0, i.uv); 

    float4 spatial_m1 = 0;
    float4 spatial_m2 = 0;

    float wsum = 0;
    [loop]for(int x = -2; x <= 2; x++)
    [loop]for(int y = -2; y <= 2; y++)
    {
        int2 pos = int2(i.vpos.xy) + int2(x, y);
        pos.x = is_specular ? max(pos.x, BUFFER_WIDTH / 2) : min(pos.x, BUFFER_WIDTH / 2 - 1);
        float4 tap = tex2Dfetch(sRTGI_Aux0, pos);
        float4 s = encode_hdr_to_filter(tap.rgb);

        float z_falloff = exp(-256.0 * abs(tap.w - curr.w) / max3(tap.w, curr.w, 1e-7));

        spatial_m1 += s     * z_falloff;
        spatial_m2 += s * s * z_falloff;
        wsum += z_falloff;  
    }

    spatial_m1 /= wsum;
    spatial_m2 /= wsum;

    float3 sigma = sqrt(abs(spatial_m2.rgb - spatial_m1.rgb * spatial_m1.rgb));
    float sigma_scale = is_specular ? 1 : 1;
    sigma *= sigma_scale;
    
    float3 delta = prev_sample.rgb - spatial_m1.rgb;

    delta /= max(1.0, length(delta / (sigma + 1e-7)));
    prev_sample.rgb = lerp(spatial_m1.rgb, spatial_m1.rgb + delta, saturate(sigma * 1024.0));  //fix problems with zero variance             
    
    int history_length = round(tex2Dlod(sRTGI_GuidePrev, i.uv, 1).z);
    history_length = valid_history ? min(is_specular ? (5 + sqrt(alpha) * 45) : 64, ++history_length) : 1;
 
    float lerpspeed = rcp(history_length); 
    o.t0.w = curr.w; //z to alpha 

    curr = encode_hdr_to_filter(curr.rgb);  
    curr.rgb = lerp(spatial_m1.rgb, curr.rgb, saturate(history_length * 0.25));

    o.t0.rgb = lerp(prev_sample.rgb, curr.rgb, lerpspeed);

    float2 curr_temporal_moments = curr.zw;
    float2 curr_spatial_moments = float2(spatial_m1.z, spatial_m2.z);

    float2 final_moments = lerp(prev_moments, curr_temporal_moments, lerpspeed);
    final_moments = lerp(curr_spatial_moments, final_moments, saturate(history_length / 3.0)); //use this if history is unreliable

    o.t1 = float4(final_moments, history_length, 0);      
}

void UpdateAccumPS(in VSOUT i, out float4 o : SV_Target0)
{
    o = tex2Dfetch(sRTGI_Aux1, uint2(i.vpos.xy));
}

void DemultiplexPS(in VSOUT i, out PSOUT2 o)
{
    float4 gbuffer = get_gbuffer(i.uv);
    uint2 p = uint2(i.vpos.xy);
    bool is_nonactive = (p.x % 2) == (p.y % 2);//!((p.x ^ p.y) & 1); 

    [branch]
    if(is_nonactive)
    {
        o.t0 = tex2Dfetch(sRTGI_Aux1, checkerboard_to_screen(p));
        o.t1 = tex2Dfetch(sRTGI_Aux1, checkerboard_to_screen(p) + int2(BUFFER_WIDTH / 2, 0));
    }
    else         
    {
        int2 offsets[4] = 
        {
            int2(-1, 0),
            int2(1, 0),
            int2(0, -1),
            int2(0, 1)
        };

        float best_score = -1;

        [unroll]
        for(int j = 0; j < 4; j++)
        {
            int2 offset = offsets[j];
            uint2 coord = checkerboard_to_screen(p + offset);

            float4 diff = tex2Dfetch(sRTGI_Aux1, coord);
            float4 spec = tex2Dfetch(sRTGI_Aux1, coord + int2(BUFFER_WIDTH / 2, 0));

            float4 tg = get_gbuffer(pixel_idx_to_uv(p + offset, BUFFER_SCREEN_SIZE));

            float score = saturate(dot(tg.xyz, gbuffer.xyz)) * saturate(1 - abs(tg.w - gbuffer.w) / max3(tg.w, gbuffer.w, 1e-7));       

            [flatten]
            if(score > best_score)
            {
                best_score = score;
                o.t0 = diff;
                o.t1 = spec;
            }                   
        }
    }

    float2 uv_diff = i.uv * float2(0.5, 1);
    float2 uv_spec = i.uv * float2(0.5, 1) + float2(0.5, 0.0);    
    
    //per signal variance into alpha channel
    {
        float4 offs = mad(BUFFER_PIXEL_SIZE.xyxy, float4(-2.0, -2.0, 2.0, 2.0), uv_diff.xyxy);
        float2 tmoments  = tex2Dlod(sRTGI_Guide, offs.xy, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.xw, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.zy, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.zw, 2).xy;
            tmoments /= 4.0;
        float variance = abs(tmoments.y - tmoments.x * tmoments.x);
        o.t0.w = variance;       
    }
    {
        float4 offs = mad(BUFFER_PIXEL_SIZE.xyxy, float4(-2.0, -2.0, 2.0, 2.0), uv_spec.xyxy);
        float2 tmoments  = tex2Dlod(sRTGI_Guide, offs.xy, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.xw, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.zy, 2).xy;
            tmoments += tex2Dlod(sRTGI_Guide, offs.zw, 2).xy;
            tmoments /= 4.0;
        float variance = abs(tmoments.y - tmoments.x * tmoments.x);
        o.t1.w = variance;       
    }
}

struct FilterSample
{
    float4 gbuffer;
    float4 diff;
    float4 spec;
};

struct FilterOutput
{
    float4 diff;
    float4 spec;
};

FilterSample get_filter_sample(in float2 uv, sampler gitex_diff, sampler gitex_spec)
{    
    FilterSample o;
    o.gbuffer = get_gbuffer(uv);   
    o.diff = tex2Dlod(gitex_diff, uv, 0);//.w = variance mask
    o.spec = tex2Dlod(gitex_spec, uv, 0);//.w = variance mask
    return o;
}

float2 geometry_weight(float3 pos_center, 
                      float3 pos_sample, 
                      float3 n_center, 
                      float3 n_sample,
                      float  alpha,
                      float2 sharpness_z,
                      float2 sharpness_n)
{    
    float3 deltavec = pos_sample - pos_center;

    float plane_dist     = abs(dot(deltavec, n_center));
    float euclidean_dist = length(deltavec);
    float camera_dist    = pos_center.z;

    float normal_angle   = Math::fast_acos(dot(normalize(n_center), normalize(n_sample)));
    float geometric_diff = lerp(plane_dist, euclidean_dist, 0.75) / camera_dist;  

    float halfangle = spec_half_angle_from_alpha(alpha);
    float spec_relaxant = rcp(1 + degrees(halfangle));

    float2 weight_n = linearstep(sharpness_n, sharpness_n * 0.666, degrees(normal_angle) * float2(1, spec_relaxant));
    float2 weight_z = exp2(-(geometric_diff / sharpness_z) * (geometric_diff / sharpness_z));

    weight_n = max(weight_n, 0.01);

    return weight_z * weight_n;
}

float signal_weight(float3 signal_center, float3 signal_sample, float sharpness_s)
{
    float diff = dot(abs(signal_center - signal_sample), float3(0.1, 0.1, 0.8));//cocgy
    diff *= sharpness_s;
    diff *= diff;
    diff = exp2(-diff);
    diff *= diff;
    diff *= diff;
    return diff; 
}

FilterOutput atrous(float2 center_uv, sampler gitex_diff, sampler gitex_spec, uint iteration)
{
    FilterSample center = get_filter_sample(center_uv, gitex_diff, gitex_spec);
    float3 pos_center = Camera::uv_to_proj(center_uv, center.gbuffer.w);    

    float smoothness = 3.9;
    float2 sv = rsqrt(1e-3 + float2(center.diff.w, center.spec.w) * 0.08 * smoothness);

    FilterOutput o;
    o.diff = center.diff;
    o.spec = center.spec;

    if(get_fade_factor(Camera::z_to_depth(center.gbuffer.w)) < 1e-5) return o;
        
    float2 wsum = 1;

    float2 minmax_diff, minmax_spec;
    minmax_diff = minmax_spec = 16384.0;

    static const float3 lw = float3(0.1, 0.1, 0.8);

    float alpha = get_alpha();

    const float2 sn = float2(25.0, 0.125);
    const float2 sz = float2(0.2, 0.1);

    [unroll]for(int y = -1; y <= 1; y++)
    [unroll]for(int x = -1; x <= 1; x++)
    {
        if(x == 0 && y == 0) continue;
        float2 tap_uv = center_uv + float2(x, y) * exp2(iteration) * BUFFER_PIXEL_SIZE; 
        FilterSample tap = get_filter_sample(tap_uv, gitex_diff, gitex_spec);
        float3 pos_tap = Camera::uv_to_proj(tap_uv, tap.gbuffer.w);
        
        float2 wg = geometry_weight(pos_center, pos_tap, center.gbuffer.xyz, tap.gbuffer.xyz, alpha, sz, sn);
        
        float ws_diff = signal_weight(center.diff.rgb, tap.diff.rgb, sv.x);
        float ws_spec = signal_weight(center.spec.rgb, tap.spec.rgb, sv.y);

        o.diff += tap.diff * wg.x * ws_diff;
        o.spec += tap.spec * wg.y * ws_spec; 

        wsum += wg * float2(ws_diff, ws_spec);

        float l = dot(tap.diff.rgb, lw);
        minmax_diff = min(minmax_diff, float2(l, -l));
        l = dot(tap.spec.rgb, lw);
        minmax_spec = min(minmax_spec, float2(l, -l));             
    }

    o.diff /= wsum.x;
    o.spec /= wsum.y;

    minmax_diff.y = -minmax_diff.y;
    minmax_spec.y = -minmax_spec.y;

    if(iteration < 1.5)
    {  
        float lum = dot(o.diff.rgb, lw);
        o.diff.rgb *= clamp(lum, minmax_diff.x, minmax_diff.y) / (1e-6 + lum); 
              lum = dot(o.spec.rgb, lw);
        o.spec.rgb *= clamp(lum, minmax_spec.x, minmax_spec.y) / (1e-6 + lum);
    }

    return o;
}

void FilterPS0(in VSOUT i, out PSOUT2 o)
{
    FilterOutput res = atrous(i.uv, sRTGI_Aux0, sRTGI_Aux2, 0);
    o.t0 = res.diff;
    o.t1 = res.spec;   
}

void FilterPS1(in VSOUT i, out PSOUT2 o)
{
    FilterOutput res = atrous(i.uv, sRTGI_Aux1, sRTGI_Aux3, 1);
    o.t0 = res.diff;
    o.t1 = res.spec;   
}

void FilterPS2(in VSOUT i, out PSOUT2 o)
{
    FilterOutput res = atrous(i.uv, sRTGI_Aux0, sRTGI_Aux2, 2);
    o.t0 = res.diff;
    o.t1 = res.spec;   
}

void FilterPS3(in VSOUT i, out PSOUT2 o)
{
    FilterOutput res = atrous(i.uv, sRTGI_Aux1, sRTGI_Aux3, 3);
    o.t0 = res.diff;
    o.t1 = res.spec;   
}

void UpdatePrevBuffersPS(in VSOUT i, out PSOUT2 o)
{   
    o.t0 = get_gbuffer(i.uv);
    o.t1 = tex2Dfetch(sRTGI_Guide, uint2(i.vpos.xy));
}

void BlendPS(in VSOUT i, out float3 o : SV_Target0)
{
    float3 diff = decode_hdr_from_filter(tex2D(sRTGI_Aux0, i.uv).rgb);
    float3 spec = decode_hdr_from_filter(tex2D(sRTGI_Aux2, i.uv).rgb);

    float fade = get_fade_factor(Depth::get_linear_depth(i.uv));
    diff = lerp(1, diff, fade);
    spec = lerp(0, spec, fade);

    o = tex2D(ColorInput, i.uv).rgb;
    if(RT_DEBUG_VIEW == 2 && i.uv.x < 0.35 + (i.uv.y - 0.5) * -0.15) return;
    if((RT_DEBUG_VIEW && i.uv.x < (1-0.35) + (i.uv.y - 0.5) * -0.15) || RT_DEBUG_VIEW == 1) o = 0.444;

    o = unpack_hdr(o);
    o = o * diff.rgb + spec.rgb;
    o = pack_hdr(o); 
}

void SkycolorDetectPS(in VSOUT i, out float4 o : SV_Target0)
{
    if(RT_AMBIENT_SKY_MIX == 0.0) discard;
    
    const uint2 samples = uint2(6 * BUFFER_ASPECT_RATIO.yx);
    float2 jitter = QMC::roberts2(FRAMECOUNT % 64u);

    o = 0;

    [loop]for(int x = 0; x < samples.x; x++)
    [loop]for(int y = 0; y < samples.y; y++)
    {
        float2 uv = (floor(i.vpos.xy) + float2(x, y) + jitter) / 32.0;
        float3 color = tex2Dlod(ColorInput, uv, 0).rgb;
        color = unpack_hdr(color);
        float is_depth = Camera::z_to_depth(tex2Dlod(sRTGI_ZSrc, uv, 0).x) > 0.999;
        o += float4(color, 1) * is_depth;
    }    

   /* float4 prev_sky = tex2D(sRTGI_IBLTexPrev, 0.5.xx);
    prev_sky = prev_sky.w == 0.0 ? prev_sky : prev_sky / prev_sky.w;*/
    float3 curr_sky = o.rgb / max(o.w, 1e-6);
    curr_sky = lerp(dot(curr_sky, 0.3333), curr_sky, 0.2);
 
    bool sky_found_now = o.w > 0.5;
    float k = sky_found_now ? saturate(0.2 * 0.01 * FRAMETIME) : 0;
   
    o.rgb = curr_sky;
    o.w = k;
}

/*=============================================================================
	Techniques
=============================================================================*/

technique MartysMods_RTGI
<
    ui_label = "iMMERSE Pro: RTGI";
    ui_tooltip =        
        "                                MartysMods - RTGI                                 \n"
        "                     MartysMods Epic ReShade Effects (iMMERSE)                    \n"
        "               Official versions only via https://patreon.com/mcflypg             \n"
        "__________________________________________________________________________________\n"
        "\n"
        "RTGI adds fully dynamic, realistic and immersive ray traced lighting to your games\n"
        "to enhance existing lighting or to completely relight your scene, depending on the\n"
        "use case.\n"
        "Make sure iMMERSE LAUNCHPAD is enabled and placed at the top of the effect list!    "
        "\n"
        "\n"
        "Visit https://martysmods.com for more information.                                \n"
        "\n"       
        "__________________________________________________________________________________\n"
        "Version: 0.51";
>
{
//Create Z texture  
#if _COMPUTE_SUPPORTED
pass { ComputeShader = DepthLinearizeCS<32, 32>;DispatchSizeX = CEIL_DIV(BUFFER_WIDTH, 64);DispatchSizeY = CEIL_DIV(BUFFER_HEIGHT, 64); }
#else 
pass { VertexShader = MainVS; PixelShader = DepthLinearizePS; RenderTarget0 = RTGI_ZSrc; }  
#endif
//Create Radiance texture
pass { VertexShader = MainVS; PixelShader = AlbedoInputPS; RenderTarget0 = RTGI_RadianceTex; }  
//Create Material Mask in .w here
pass{ VertexShader = MainVS; PixelShader = SkycolorDetectPS;RenderTarget = RTGI_IBLTex;   BlendEnable = true; BlendOp = ADD; SrcBlend = SrcAlpha; DestBlend = InvSrcAlpha; BlendOpAlpha=MAX; SrcBlendAlpha=SrcAlpha; DestBlendAlpha=InvSrcAlpha;}
//GI Trace -> RTGI_Aux0
#if _COMPUTE_SUPPORTED
pass { ComputeShader = TraceWrapDiffuseCS<16, 16>;DispatchSizeX = CEIL_DIV(BUFFER_WIDTH, 32);DispatchSizeY = CEIL_DIV(BUFFER_HEIGHT, 16); }
pass { ComputeShader = TraceWrapSpecularCS<16, 16>;DispatchSizeX = CEIL_DIV(BUFFER_WIDTH, 32);DispatchSizeY = CEIL_DIV(BUFFER_HEIGHT, 16); }
#else 
pass { VertexShader = MainVS; PixelShader = TraceWrapDiffusePS; RenderTarget0 = RTGI_Aux0;  } 
pass { VertexShader = MainVS; PixelShader = TraceWrapSpecularPS; RenderTarget0 = RTGI_Aux0;  }   
#endif
//Reproject -> RTGI_Aux1
pass { VertexShader = MainVS; PixelShader = AccumPS; RenderTarget0 = RTGI_Aux1; RenderTarget1 = RTGI_Guide; }  
//Copy to accum buffer -> RTGI_Accum
pass { VertexShader = MainVS; PixelShader = UpdateAccumPS; RenderTarget0 = RTGI_Accum; }  
//Demultiplex diff/spec RTGI_Aux1 -> RTGI_Aux0/RTGI_Aux2
pass { VertexShader = MainVS; PixelShader = DemultiplexPS; RenderTarget0 = RTGI_Aux0; RenderTarget1 = RTGI_Aux2; }  
//Filter RTGI_Aux0/RTGI_Aux2 <-> RTGI_Aux1/RTGI_Aux3
pass { VertexShader = MainVS; PixelShader = FilterPS0; RenderTarget0 = RTGI_Aux1; RenderTarget1 = RTGI_Aux3; }
pass { VertexShader = MainVS; PixelShader = FilterPS1; RenderTarget0 = RTGI_Aux0; RenderTarget1 = RTGI_Aux2; }
pass { VertexShader = MainVS; PixelShader = FilterPS2; RenderTarget0 = RTGI_Aux1; RenderTarget1 = RTGI_Aux3; }
pass { VertexShader = MainVS; PixelShader = FilterPS3; RenderTarget0 = RTGI_Aux0; RenderTarget1 = RTGI_Aux2; }

//Output to screen
pass { VertexShader = MainVS; PixelShader = BlendPS; }
//Update prev buffers -> RTGI_Aux3/RTGI_GuidePrev
pass { VertexShader = MainVS; PixelShader = UpdatePrevBuffersPS; RenderTarget0 = RTGI_Aux3; RenderTarget1 = RTGI_GuidePrev; }
}
