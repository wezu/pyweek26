//GLSL
#version 130
in vec2 uv;
uniform sampler2D p3d_Texture0;
uniform sampler2D map_tex;


void main()
    {
    float lines=texture(p3d_Texture0,uv).r;
    lines=clamp(lines, pow(distance(uv.xy, vec2(0.5))*2.0, 4.0), 1.0);
    vec4 map=texture(map_tex,uv);
    vec4 final_color=map*lines;
    gl_FragData[0]=vec4(final_color.rgb, map.a);
    }
