import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Email Brief — AI Email Summarizer",
  description:
    "Email Brief reads your inbox, summarizes emails with AI, and tells you what to reply to first. Free, private, and open source.",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
