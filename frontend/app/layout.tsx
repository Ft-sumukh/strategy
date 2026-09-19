import "./styles.css";

export const metadata = { title: "Aegis Invest", description: "Investment decision intelligence workspace" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
