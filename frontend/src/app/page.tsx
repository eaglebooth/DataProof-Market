"use client";

import { ArrowRight, Coins, FileCheck2, ScanSearch, Scale, ShieldCheck, Sparkles } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { DataMatrix } from "@/components/DataMatrix";
import { Notice } from "@/components/Notice";
import { Reveal } from "@/components/Reveal";
import { StatusPill } from "@/components/StatusPill";
import { configuredAddress, readContract } from "@/lib/genlayer";
import { parseJsonResult } from "@/lib/format";
import { Bounty, EMPTY_STATE, MarketState } from "@/lib/types";

export default function MarketPage() {
  const [state, setState] = useState<MarketState>(EMPTY_STATE);
  const [bounties, setBounties] = useState<Bounty[]>([]);
  const [message, setMessage] = useState("Connect a deployed contract to load the live market.");
  const [loading, setLoading] = useState(false);

  const sync = useCallback(async () => {
    if (!configuredAddress()) {
      setMessage("Awaiting a deployed DataProof Market contract.");
      return;
    }
    setLoading(true);
    const result = await readContract("get_state");
    if (!result.success) {
      setMessage(result.error || "Unable to read contract state.");
      setLoading(false);
      return;
    }
    try {
      const nextState = parseJsonResult<MarketState>(result.data);
      setState(nextState);
      const count = Math.min(Number(nextState.bounty_count || 0), 12);
      const rows = await Promise.all(
        Array.from({ length: count }, (_, id) => readContract("get_bounty", [BigInt(id)])),
      );
      setBounties(rows.filter((row) => row.success).map((row) => parseJsonResult<Bounty>(row.data)).reverse());
      setMessage(`Live state received. ${count} bounded record${count === 1 ? "" : "s"} inspected.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Contract response could not be parsed.");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void sync(), 0);
    return () => window.clearTimeout(timer);
  }, [sync]);

  return (
    <>
      <section className="hero">
        <Reveal className="hero-copy">
          <p className="eyebrow">GENLAYER DATASET PROCUREMENT</p>
          <h1>Buy useful data.<br /><em>Not confident claims.</em></h1>
          <p className="hero-lede">
            Buyers lock real GEN and a public rubric. Providers lock immutable dataset evidence.
            A GenLayer jury decides the payout band.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/bounties/new">Fund a dataset request <ArrowRight size={17} /></Link>
            <Link className="text-link" href="/protocol">Inspect the safeguards <ArrowRight size={16} /></Link>
          </div>
        </Reveal>
        <Reveal className="hero-matrix" delay={120}><DataMatrix /></Reveal>
      </section>

      <Reveal className="metric-band">
        <div><strong>{state.bounty_count}</strong><span>requests</span></div>
        <div><strong>{state.active_escrow} wei</strong><span>active escrow</span></div>
        <div><strong>{state.total_provider_paid} wei</strong><span>provider payouts</span></div>
        <div><strong>{state.total_buyer_refunded} wei</strong><span>buyer refunds</span></div>
      </Reveal>

      <section className="workflow-section" id="how-it-works">
        <Reveal className="workflow-intro">
          <p className="eyebrow">HOW IT WORKS</p>
          <h2>One request. Four accountable states.</h2>
          <p>
            Each action narrows what can happen next. Evidence stays immutable,
            identities stay sender-bound, and settlement cannot exceed escrow.
          </p>
        </Reveal>
        <div className="workflow-track">
          <Reveal className="workflow-step" delay={40}>
            <span>01</span><Coins />
            <div><h3>Fund the request</h3><p>The buyer selects a provider, publishes a rubric digest, and locks exact GEN escrow.</p></div>
          </Reveal>
          <Reveal className="workflow-step" delay={90}>
            <span>02</span><FileCheck2 />
            <div><h3>Bind the packet</h3><p>The provider attaches manifest, sample, and license snapshots before the record is sealed.</p></div>
          </Reveal>
          <Reveal className="workflow-step" delay={140}>
            <span>03</span><ScanSearch />
            <div><h3>Run the jury</h3><p>Validators inspect live sources and agree on usefulness, provenance, leakage, and licensing.</p></div>
          </Reveal>
          <Reveal className="workflow-step" delay={190}>
            <span>04</span><Sparkles />
            <div><h3>Settle the band</h3><p>ACCEPT, PARTIAL, REJECT, or mutual recovery deterministically controls the conserved payout.</p></div>
          </Reveal>
        </div>
        <Reveal className="workflow-cta">
          <Link className="button button-primary" href="/bounties/new">Start with a funded request <ArrowRight size={17} /></Link>
          <Link className="text-link" href="/protocol">Read every guardrail <ArrowRight size={16} /></Link>
        </Reveal>
      </section>

      <Reveal className="market-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">LIVE PROCUREMENT BOARD</p>
            <h2>Evidence-backed requests</h2>
          </div>
          <button className="button button-quiet" disabled={loading} onClick={() => void sync()} type="button">
            {loading ? "Reading..." : "Sync contract"}
          </button>
        </div>
        <Notice>{message}</Notice>
        {bounties.length ? (
          <div className="bounty-list">
            {bounties.map((bounty) => (
              <Link className="bounty-row" href={`/bounties/${bounty.id}`} key={bounty.id}>
                <span className="row-id">#{bounty.id.padStart(2, "0")}</span>
                <span className="row-main"><strong>{bounty.title}</strong><small>{bounty.use_case}</small></span>
                <span className="row-value">{bounty.escrow} wei</span>
                <StatusPill status={bounty.status} />
                <ArrowRight size={18} />
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <FileCheck2 />
            <strong>No funded requests yet.</strong>
            <p>The first buyer can define a rubric, provider, and real escrow.</p>
            <Link className="text-link" href="/bounties/new">Open the first request <ArrowRight size={16} /></Link>
          </div>
        )}
      </Reveal>

      <Reveal className="principles">
        <article><ShieldCheck /><span>01</span><h3>Evidence cannot drift</h3><p>Every rubric, manifest, sample, and license is bound to an immutable URL and SHA-256 digest.</p></article>
        <article><Scale /><span>02</span><h3>Money follows a band</h3><p>The jury chooses full, partial, or refund. It cannot invent a payout amount.</p></article>
        <article><FileCheck2 /><span>03</span><h3>Recovery needs both parties</h3><p>Unavailable web evidence cannot trap funds forever; mutual approval returns escrow to the buyer.</p></article>
      </Reveal>
    </>
  );
}
