import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CV Master",
  description: "AI-powered resume generation from your career knowledge base",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
