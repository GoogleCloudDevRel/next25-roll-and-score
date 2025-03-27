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

export function waitFor(cb) {
  const promise = deferred()
  let maxTime = 2000
  let count = 0
  let interval = setInterval(() => {
    if (cb()) {
      promise.resolve()
      clearInterval(interval)
    }
    count++
    if (count > maxTime) {
      promise.reject()
      clearInterval(interval)
    }
  }, 120)
  return promise
}
