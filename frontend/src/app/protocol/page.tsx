import { ArrowRight, Binary, CircleDollarSign, FileLock2, Scale } from "lucide-react";
import Link from "next/link";

export default function ProtocolPage() {
  return (
    <section className="protocol-page">
      <div className="protocol-hero">
        <p className="eyebrow">HOW IT WORKS</p>
        <h1>Sealed supply.<br />One comparative verdict.</h1>
        <p>A bounded tournament makes competing datasets comparable without exposing packets before commitment.</p>
      </div>
      <div className="protocol-steps">
        <article><span>01</span><FileLock2 /><h2>Buyer funds demand</h2><p>A public rubric, prize, reveal bond, deadline, and two-to-five candidate cap are fixed together.</p></article>
        <article><span>02</span><Binary /><h2>Providers commit, then reveal</h2><p>Digests are sealed before immutable manifest, sample, and license URLs become visible.</p></article>
        <article><span>03</span><Scale /><h2>Validators rank meaning</h2><p>Exact digest consensus establishes eligibility; comparative consensus selects only among eligible IDs.</p></article>
        <article><span>04</span><CircleDollarSign /><h2>Contract assigns credits</h2><p>The winner receives the prize, revealed providers recover liveness bonds, and no-reveal bonds return to the buyer.</p></article>
      </div>
      <div className="guardrail">
        <div><p className="eyebrow">FAILURE PATH</p><h2>Unavailable evidence is explicit.</h2></div>
        <p>An unavailable or mismatched packet is excluded without vetoing eligible rivals. If ranking itself is unavailable, no winner is invented: the prize returns to the buyer and revealed liveness bonds remain refundable.</p>
        <Link className="button button-primary" href="/bounties/new">Fund a tournament <ArrowRight size={17} /></Link>
      </div>
    </section>
  );
}
