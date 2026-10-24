"use client";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger once on the client
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export { gsap, ScrollTrigger };

/**
 * Standard page-load reveal animation that respects prefers-reduced-motion.
 * Animates only opacity and transform (translateY).
 */
export function revealOnLoad(targets: gsap.DOMTarget, options?: { delay?: number; stagger?: number; y?: number }) {
  if (typeof window === "undefined") return;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReduced) {
    gsap.set(targets, { opacity: 1, y: 0 });
    return;
  }

  return gsap.fromTo(
    targets,
    { opacity: 0, y: options?.y ?? 20 },
    {
      opacity: 1,
      y: 0,
      duration: 0.7,
      delay: options?.delay ?? 0.1,
      stagger: options?.stagger ?? 0.08,
      ease: "power2.out",
    }
  );
}

/**
 * Scroll-triggered reveal animation for sections.
 * Animates only opacity and transform.
 */
export function setupScrollTrigger(
  triggerElement: gsap.DOMTarget,
  animatedTargets: gsap.DOMTarget,
  options?: { y?: number; stagger?: number; delay?: number }
) {
  if (typeof window === "undefined") return;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced) {
    gsap.set(animatedTargets, { opacity: 1, y: 0 });
    return;
  }

  return gsap.fromTo(
    animatedTargets,
    { opacity: 0, y: options?.y ?? 24 },
    {
      opacity: 1,
      y: 0,
      duration: 0.8,
      stagger: options?.stagger ?? 0.1,
      delay: options?.delay ?? 0,
      ease: "power3.out",
      scrollTrigger: {
        trigger: triggerElement as Element,
        start: "top 85%",
        toggleActions: "play none none none",
      },
    }
  );
}
