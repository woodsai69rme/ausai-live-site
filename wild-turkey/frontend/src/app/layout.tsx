import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Wild Turkey 5.5 — Omnimodal Autonomous AI Platform',
  description: 'Compliant AI Resource Orchestrator, Swarms, Voice & Omnimodal RAG Hub',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
