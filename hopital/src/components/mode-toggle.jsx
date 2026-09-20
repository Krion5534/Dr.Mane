"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ModeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const applyTheme = (isDark) => {
      document.documentElement.classList.toggle("dark", isDark);
      setDark(isDark);
    };

    // Initial system preference
    applyTheme(mediaQuery.matches);

    // React to system changes while the app is open
    const handleChange = (event) => {
      applyTheme(event.matches);
    };

    mediaQuery.addEventListener("change", handleChange);

    return () => {
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, []);

  function toggleTheme() {
    const newDark = !dark;

    document.documentElement.classList.toggle("dark", newDark);
    setDark(newDark);
  }

  return (
    <Button variant="ghost" size="icon" onClick={toggleTheme}>
      {dark ? (
        <Moon className="size-5" />
      ) : (
        <Sun className="size-5" />
      )}

      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}