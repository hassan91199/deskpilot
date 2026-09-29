import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

import "@testing-library/jest-dom/vitest";

// @testing-library/react's auto-cleanup only registers itself when it finds
// a global `afterEach` (e.g. Jest, or Vitest with `test.globals: true`).
// This project imports `afterEach` explicitly per test file instead, so
// cleanup is wired up here rather than turning on Vitest's globals.
afterEach(() => {
  cleanup();
});
