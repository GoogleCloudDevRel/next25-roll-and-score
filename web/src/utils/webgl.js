
export const convertFragmentTo300 = (value) => {
  return (
    /* glsl */ `#version 300 es
          precision highp float;
          #define varying in
          #define texture2D texture
          #define gl_FragColor FragColor
          out vec4 FragColor;
      ` + value
  )
}

export const convertVertexTo300 = (value) => {
  return (
    /* glsl */ `#version 300 es
          #define attribute in
          #define varying out
      ` + value
  )
}

export const getHeightFromCamera = function (camera, dist) {
  if (!dist) dist = camera.position.z
  let fov = camera.fov;
  return 2 * dist * Math.tan(fov * Math.PI / 180 / 2);
}

export const getWidthFromCamera = function (camera, dist) {
  const height = getHeightFromCamera(camera, dist);
  return height * camera.aspect;
}
