//GLSL
#version 140
uniform sampler2D depth_tex;
uniform sampler2D normal_tex;
uniform sampler2D albedo_tex;
uniform sampler2D lit_tex;

uniform sampler2D shpere_tex;
uniform mat4 p3d_ProjectionMatrixInverse;



//in vec2 uv;


// For each component of v, returns -1 if the component is < 0, else 1
vec2 sign_not_zero(vec2 v)
    {
    // Version with branches (for GLSL < 4.00)
    return vec2(v.x >= 0 ? 1.0 : -1.0, v.y >= 0 ? 1.0 : -1.0);
    }

// Unpacking from octahedron normals, input is the output from pack_normal_octahedron
vec3 unpack_normal_octahedron(vec2 packed_nrm)
    {
    if (packed_nrm==vec2(0.0))
        {
            return vec3(0.0);
        }
    // Version using newer GLSL capatibilities
    vec3 v = vec3(packed_nrm.xy, 1.0 - abs(packed_nrm.x) - abs(packed_nrm.y));
    // Branch-Less version
    v.xy = mix(v.xy, (1.0 - abs(v.yx)) * sign_not_zero(v.xy), step(v.z, 0));
    return normalize(v);
    }

vec3 getPosition(vec2 uv, float depth)
    {
    vec4 view_pos = p3d_ProjectionMatrixInverse * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    view_pos.xyz /= view_pos.w;
    return view_pos.xyz;
    }

vec3 do_specular(float roughness, vec3 tint,
                 float metallic, float NdotH,
                 float gloss, float base_roughness)
    {
    return mix(vec3(1.0-roughness), tint, metallic) * pow(NdotH, gloss)*(1.0-base_roughness+metallic);
    }

void main()
    {
    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec2 uv=gl_FragCoord.xy/win_size;
    vec4 pre_light_tex=texture(lit_tex, uv);

    vec4 color_tex=texture(albedo_tex, uv);
    vec3 albedo=color_tex.rgb;
    vec4 normal_roughness_metallic=texture(normal_tex,uv);
    vec3 N=unpack_normal_octahedron(normal_roughness_metallic.xy);
    float roughness =pow(normal_roughness_metallic.b, 0.5);
    float base_roughness =normal_roughness_metallic.b;
    float metallic=normal_roughness_metallic.a;
    //vec3 specular = mix(vec3(0.04), albedo, metallic);
    float gloss=350.0*(1.0-roughness);
    float glow=color_tex.a;
    albedo =mix(albedo, vec3(0.0), metallic);
    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;


    vec3 color=texture(shpere_tex, vec2(N.xyz * vec3(0.49) + vec3(0.5))).rgb;

    vec4 final=pre_light_tex+vec4(albedo*pow(color*vec3(0.8+metallic*0.5), vec3(2.0)), glow);

    final.rgb+=albedo*glow;

    gl_FragData[0]=final;
    }

