export const getQueryParam = (param, asBoolean = true) => {
  const urlParams = new URLSearchParams(window.location.search)
  const value = urlParams.get(param)
  if (asBoolean) {
    return Boolean(value !== null)
  }
  return value
}
