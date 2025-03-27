precision mediump float;

struct Disk {
    vec3 color;
    vec2 center;
    float radius;
};

varying vec2 vUv;
uniform vec2 uResolution;
uniform float uFade;
uniform Disk uDisk1;
uniform Disk uDisk2;
uniform Disk uDisk3;
uniform Disk uDisk4;

uniform vec3 uBGColor;

float opU( float d1, float d2 )
{
    return min(d1,d2);
}

float smin(float a, float b, float k) {
    float h = clamp(0.5+0.5*(b-a)/k, 0.0, 1.0);
    return mix(b, a, h) - k*h*(1.0-h);
}

float circle(vec2 uv, vec2 center, float radius) {
    return length(uv - center) - radius;
}

float dither(vec2 uv) {
    return fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {

    vec2 st = vUv;
    st -= 0.5;
    st.x *= uResolution.x / uResolution.y;
    st += 0.5;

    vec3 bgColor = uBGColor;

    vec3 col = bgColor;

    float disk1 = smoothstep(0.0, 1.0, circle(st, uDisk1.center, uDisk1.radius));
    float disk2 = smoothstep(0.0, 1.0, circle(st, uDisk2.center, uDisk2.radius));
    float disk3 = smoothstep(0.0, 1.0, circle(st, uDisk3.center, uDisk3.radius));
    float disk4 = smoothstep(0.0, 1.0, circle(st, uDisk4.center, uDisk4.radius));
    
    col = mix(uDisk1.color, col, disk1);
    col = mix(uDisk2.color, col, disk2);
    col = mix(uDisk3.color, col, disk3);
    col = mix(uDisk4.color, col, disk4);

    gl_FragColor = vec4(col * uFade, 1.0);

    gl_FragColor.rgb += dither(vUv + fract(100.0)) * 0.015;

}