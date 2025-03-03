export function deferred() {
  let temp_resolve
  let temp_reject
  const promise = new Promise((resolve, reject) => {
    temp_resolve = resolve;
    temp_reject = reject;
  })
  promise.resolve = temp_resolve;
  promise.reject = temp_reject;
  return promise;
}