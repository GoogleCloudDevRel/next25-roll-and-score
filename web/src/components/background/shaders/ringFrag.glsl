varying vec2 vUv;
uniform vec3 uColor;
uniform float uBorder;
uniform vec3 uGrayscaleColor;
uniform float uGrayscale;

float aastep(float threshold, float value) {
    float afwidth = length(vec2(dFdx(value), dFdy(value))) * 0.70710678118654757;
    return smoothstep(threshold-afwidth, threshold+afwidth, value);
}

float aastep(float threshold, float value, float padding) {
    return smoothstep(threshold - padding, threshold + padding, value);
}

vec2 aastep(vec2 threshold, vec2 value) {
    return vec2(
        aastep(threshold.x, value.x),
        aastep(threshold.y, value.y)
    );
}

void main() {
    float dist = distance(vUv, vec2(0.5));
    float border = mix(0.5, 0.025, uBorder);
    float alpha = aastep(0.5 - border, dist) * aastep(0.5, 1.0 - dist);
    vec3 color = mix(vec3(0.0), mix(uColor, uGrayscaleColor, uGrayscale), alpha);
    gl_FragColor = vec4(color, alpha);
}