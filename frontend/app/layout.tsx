import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Yuma - AI Timelapse Generator",
  description: "Generate stunning AI-powered timelapse transformation videos",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans bg-gray-950 text-white min-h-screen">
        {children}
      </body>
    </html>
  );
}
