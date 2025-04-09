import { gsap } from "gsap";
import { Flip } from "gsap/Flip";
import { deferred } from "./deferred";

gsap.registerPlugin(Flip);

export const waitUntil = async (condition, checkTime = 1 / 60) => {
  let result = deferred();

  function check() {
    if (condition()) {
      result.resolve();
    } else {
      gsap.delayedCall(checkTime, check);
    }
  }

  check();

  return result;
}

export * from "gsap";
export { Flip };
