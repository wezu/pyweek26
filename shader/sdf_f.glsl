#version 130

uniform sampler2D p3d_Texture0;
uniform vec4 outline_color;
uniform vec2 outline_offset;
uniform float outline_power;
uniform vec4 p3d_ClipPlane[1];

in vec2 uv;
in vec4 txt_color;
in vec4 vpos;

void main()
    {
    if (dot(p3d_ClipPlane[0], vpos) < 0.0)
        {
        discard;
        }
    float dist = texture(p3d_Texture0, uv).a;
    vec2 width = vec2(0.5-fwidth(dist), 0.5+fwidth(dist));
    float alpha = smoothstep(width.x, width.y, dist);
    //supersampling
    float scale = 0.354; // half of 1/sqrt2 - value from internet(???)
    vec2 duv = scale * (dFdx(uv) + dFdy(uv));
    vec4 box = vec4(uv-duv, uv+duv);
    alpha +=0.5*(smoothstep(width.x, width.y, texture(p3d_Texture0, box.xy).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.zw).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.xw).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.zy).a));
    alpha/=3.0; //weighted average, 1*1 + 4*0.5 = 3, so divide by 3
    //outline
    float outline=pow(texture(p3d_Texture0, uv-outline_offset).a, outline_power);
    gl_FragData[0] =mix(vec4(outline_color.rgb, outline_color.a*outline), txt_color, alpha);
    //gl_FragData[0]=vec4(txt_color.rgb, alpha);
    }
