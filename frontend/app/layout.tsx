import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AfterMath — memory is the product",
  description: "On-call SRE agent that learns from every outage.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-bg text-text font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
