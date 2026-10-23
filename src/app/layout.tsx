import type { Metadata } from "next";
import "./globals.css";
import "./wordpress.css";
export const metadata: Metadata = { title: {default:"Youth Council Pakistan — A generation of possibility", template:"%s | Youth Council Pakistan"}, description:"Discover Youth Council Pakistan: leadership, opportunities, programs, events, and a connected community of young changemakers." };
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>) {return <html lang="en" data-scroll-behavior="smooth"><body>{children}</body></html>}
