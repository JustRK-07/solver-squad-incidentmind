// ── FRONTEND ── root layout (Next.js App Router)
import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'IncidentMind — memory is the product',
  description: 'On-call SRE agent that learns from every outage.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
