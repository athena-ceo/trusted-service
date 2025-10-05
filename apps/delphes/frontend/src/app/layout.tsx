import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Services de l'État dans les Yvelines",
  description: "Portail des services préfectoraux des Yvelines",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" data-fr-scheme="system" data-fr-js="true" data-fr-theme="light">
      <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@gouvfr/dsfr/dist/dsfr.min.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@gouvfr/dsfr/dist/utility/icons/icons.min.css" />
        <link rel="apple-touch-icon" href="/favicon/apple-touch-icon.png" />
        <link rel="icon" href="/favicon/favicon.svg" type="image/svg+xml" />
        <link rel="shortcut icon" href="/favicon/favicon.ico" type="image/x-icon" />
      </head>
      <body className={inter.className}>
        {children}
        <script src="https://cdn.jsdelivr.net/npm/@gouvfr/dsfr/dist/dsfr.module.min.js" defer />
      </body>
    </html>
  );
}
