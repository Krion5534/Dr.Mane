import { Inter } from "next/font/google";
import "./globals.css";

import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";

import { AppSidebar } from "@/components/sidebar";
import { Plus } from "lucide-react";
import Link from "next/link";

import { ModeToggle } from "@/components/mode-toggle";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata = {
  title: "Hospital",
  description: "Hospital management system",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full">
        <SidebarProvider>
          <AppSidebar />

          <SidebarInset>
            <header className="flex h-14 items-center gap-2 border-b px-4">
              <SidebarTrigger />

              <Link
                href="/"
                className="flex items-center gap-2 font-semibold"
              >
                <Plus />
                <span>Hospital</span>
              </Link>

              <div className="ml-auto">
                <ModeToggle />
              </div>
            </header>

            {children}
          </SidebarInset>
        </SidebarProvider>
      </body>
    </html>
  );
}