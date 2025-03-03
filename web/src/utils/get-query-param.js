export const getQueryParam = (param) => {
  const urlParams = new URLSearchParams(window.location.search)
  return Boolean(urlParams.get(param) !== null)
}
