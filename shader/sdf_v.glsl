#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Color;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

out vec2 uv;
out vec4 txt_color;
out vec4 vpos;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv=p3d_MultiTexCoord0;
    txt_color=p3d_Color;
    vpos=p3d_ModelViewMatrix * p3d_Vertex;
    }
