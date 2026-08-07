"use client";

import { motion } from "motion/react";

export function BackgroundCircles() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
    >
      <motion.div
        className="absolute top-10 left-1/2 h-96 w-96 rounded-full bg-linear-to-br from-violet-700/30 via-blue-500/25 to-sky-400/20 blur-3xl"
        animate={{
          x: ["-45%", "-38%", "-50%", "-42%", "-45%"],
          y: [0, 18, -14, -20, 0],
          scale: [1, 1.08, 0.95, 1.04, 1],
        }}
        transition={{
          duration: 18,
          ease: "easeInOut",
          repeat: Number.POSITIVE_INFINITY,
        }}
      />

      <motion.div
        className="absolute bottom-0 left-1/2 h-80 w-80 rounded-full bg-linear-to-br from-green-500/50 via-emerald-500/40 to-cyan-400/30 blur-3xl"
        animate={{
          x: ["-6%", "6%", "-12%", "2%", "-6%"],
          y: [0, -14, 16, 8, 0],
          scale: [1, 1.05, 0.93, 1.02, 1],
        }}
        transition={{
          duration: 20,
          ease: "easeInOut",
          repeat: Number.POSITIVE_INFINITY,
        }}
      />
    </div>
  );
}
