import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataProof Market",
  description: "A GenLayer dataset procurement market with immutable evidence and escrow-backed AI verdicts.",
  icons: {
    icon: "/dataproof-logo.png",
    apple: "/dataproof-logo.png",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
