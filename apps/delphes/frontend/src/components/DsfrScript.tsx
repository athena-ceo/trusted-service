"use client";

import { useEffect } from "react";

const DSFR_SCRIPT_SRC =
  "https://cdn.jsdelivr.net/npm/@gouvfr/dsfr/dist/dsfr.module.min.js";

export default function DsfrScript() {
  useEffect(() => {
    const existing = document.querySelector(`script[src="${DSFR_SCRIPT_SRC}"]`);
    if (existing) {
      return;
    }

    const script = document.createElement("script");
    script.src = DSFR_SCRIPT_SRC;
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  return null;
}
