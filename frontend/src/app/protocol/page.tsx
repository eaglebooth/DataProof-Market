import { ArrowRight, Binary, CircleDollarSign, FileLock2, Scale } from "lucide-react";
import Link from "next/link";

export default function ProtocolPage() {
  return (
    <section className="protocol-page">
      <div className="protocol-hero">
        <p className="eyebrow">HOW IT WORKS</p>
        <h1>Four locks.<br />One economic verdict.</h1>
        <p>The workflow stays narrow enough to review and strong enough to move real escrow.</p>
      </div>
      <div className="protocol-steps">
        <article><span>01</span><FileLock2 /><h2>Buyer locks demand</h2><p>A designated provider, use case, rubric snapshot, full escrow, and partial band are fixed together.</p></article>
        <article><span>02</span><Binary /><h2>Provider locks supply</h2><p>The provider submits immutable manifest and sample evidence, then adds a separately hashed license snapshot.</p></article>
        <article><span>03</span><Scale /><h2>Validators judge meaning</h2><p>GenLayer reads the public packet and compares verdict semantics: accept, partial, reject, or unavailable.</p></article>
        <article><span>04</span><CircleDollarSign /><h2>Contract settles exactly</h2><p>Full payout, locked partial split, or buyer refund. No caller can rewrite the jury&apos;s economic band.</p></article>
      </div>
      <div className="guardrail">
        <div><p className="eyebrow">FAILURE PATH</p><h2>Unavailable evidence is explicit.</h2></div>
        <p>If a locked source cannot be read, neither party can force a payout. Buyer and provider must both approve recovery.</p>
        <Link className="button button-primary" href="/bounties/new">Fund a request <ArrowRight size={17} /></Link>
      </div>
    </section>
  );
}
