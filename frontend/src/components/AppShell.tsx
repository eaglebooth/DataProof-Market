"use client";

import { FlaskConical, Menu, WalletCards, X } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { configuredAddress, connectWallet, networkLabel } from "@/lib/genlayer";
import { shortAddress } from "@/lib/format";

const links = [
  { href: "/", label: "Market" },
  { href: "/bounties/new", label: "Fund tournament" },
  { href: "/protocol", label: "Protocol" },
  { href: "/contract", label: "Contract" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [wallet, setWallet] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [address, setAddress] = useState("");
  const [walletError, setWalletError] = useState("");

  useEffect(() => {
    const timer = window.setTimeout(() => setAddress(configuredAddress()), 0);
    return () => window.clearTimeout(timer);
  }, [pathname]);

  async function handleConnect() {
    setWalletError("");
    const result = await connectWallet();
    if (result.success) setWallet(String(result.data));
    else setWalletError(result.error || "Wallet connection failed.");
  }

  return (
    <div className="app">
      <header className="topbar">
        <Link className="brand" href="/">
          <span className="brand-mark">
            <Image className="brand-logo" src="/dataproof-logo.png" alt="" width={38} height={38} priority />
          </span>
          <span>DataProof</span>
          <small>MARKET</small>
        </Link>
        <nav className={menuOpen ? "nav nav-open" : "nav"}>
          {links.map((link) => (
            <Link className={pathname === link.href ? "active" : ""} href={link.href} key={link.href} onClick={() => setMenuOpen(false)}>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="header-actions">
          <span className="network-chip"><span />{networkLabel}</span>
          <button className="wallet-button" onClick={handleConnect} type="button">
            <WalletCards size={17} />
            {wallet ? shortAddress(wallet) : "Connect wallet"}
          </button>
          <button aria-label="Toggle navigation" className="icon-button menu-button" onClick={() => setMenuOpen((open) => !open)} type="button">
            {menuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </header>
      <div className="runtime-strip">
        <div><FlaskConical size={15} /> Contract</div>
        <span>{address ? shortAddress(address) : "Awaiting deployment address"}</span>
        {walletError && <strong>{walletError}</strong>}
      </div>
      <main>{children}</main>
      <footer>
        <div className="brand footer-brand">
          <span className="brand-mark"><Image className="brand-logo" src="/dataproof-logo.png" alt="" width={38} height={38} /></span>
          <span>DataProof</span>
        </div>
        <p>Immutable evidence. Semantic jury. Conserved escrow.</p>
        <Link href="/protocol">Read the protocol</Link>
      </footer>
    </div>
  );
}
