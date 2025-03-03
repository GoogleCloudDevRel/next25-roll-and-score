varying vec2 vUv;
uniform sampler2D tMap;

float msdf(vec3 tex, vec2 uv, bool discards) {
    // TODO: fallback for fwidth for webgl1 (need to enable ext)
    float signedDist = max(min(tex.r, tex.g), min(max(tex.r, tex.g), tex.b)) - 0.5;
    float d = fwidth(signedDist);
    float alpha = smoothstep(-d, d, signedDist);
    return alpha;
}

float msdf(sampler2D tMap, vec2 uv, bool discards) {
    vec3 tex = texture2D(tMap, uv).rgb;
    return msdf( tex, uv, discards );
}

float msdf(vec3 tex, vec2 uv) {
    return msdf( tex, uv, true );
}

float msdf(sampler2D tMap, vec2 uv) {
    vec3 tex = texture2D(tMap, uv).rgb;
    return msdf( tex, uv );
}

float strokemsdf(sampler2D tMap, vec2 uv, float stroke, float padding) {
    vec3 tex = texture2D(tMap, uv).rgb;
    float signedDist = max(min(tex.r, tex.g), min(max(tex.r, tex.g), tex.b)) - 0.5;
    float t = stroke;
    float alpha = smoothstep(-t, -t + padding, signedDist) * smoothstep(t, t - padding, signedDist);
    return alpha;
}

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
    vec2 uv = vUv;

    uv -= 0.5;
    uv *=0.9;
    uv += 0.5;

    float alpha = msdf(tMap, uv);
    float stroke = alpha - msdf(tMap, vUv);
    float alphaShadow = msdf(tMap, vUv - vec2(0.05, -0.05));
    alpha = max(alpha + alphaShadow, stroke);
    gl_FragColor = vec4(vec3(((alpha - alphaShadow) * (1.0 - stroke))), alpha);
}