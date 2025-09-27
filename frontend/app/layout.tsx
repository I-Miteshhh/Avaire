import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { AppProvider } from "@/lib/context";

export const metadata: Metadata = {
  title: "Avaire | Fashion AI for Gen Z",
  description: "Personalized recommendations and virtual try-on for Gen Z women in India."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950">
        <AppProvider>
          <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-24">
            <Navbar />
            <main className="flex-1 pt-20">{children}</main>
          </div>
        </AppProvider>
      </body>
    </html>
  );
}
