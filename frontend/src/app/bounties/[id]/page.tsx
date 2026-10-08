"use client";

import { ArrowLeft, ArrowRight, ExternalLink, Scale, WalletCards } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Notice } from "@/components/Notice";
import { StatusPill } from "@/components/StatusPill";
import { connectWallet, readContract, writeContract } from "@/lib/genlayer";
import { parseJsonResult, shortAddress } from "@/lib/format";
import type { Submission, Tournament } from "@/lib/types";

export default function TournamentPage() {
  const { id } = useParams<{ id: string }>();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [entries, setEntries] = useState<Submission[]>([]);
  const [wallet, setWallet] = useState("");
  const [myEntry, setMyEntry] = useState<Submission | null>(null);
  const [busy, setBusy] = useState(false);
  const [now, setNow] = useState(0);
  const [message, setMessage] = useState("Reading tournament.");
  const [commit, setCommit] = useState({ manifest: "", sample: "", license: "" });
  const [reveal, setReveal] = useState({ manifest: "", sample: "", license: "", note: "" });

  const sync = useCallback(async (account = wallet) => {
    const result = await readContract("get_tournament", [BigInt(id)]);
    if (!result.success) { setMessage(result.error || "Read failed."); return null; }
    const next = parseJsonResult<Tournament>(result.data);
    setTournament(next);
    const rows = await Promise.all(Array.from({ length: next.candidates }, (_, slot) => readContract("get_tournament_submission", [BigInt(id), BigInt(slot)])));
    setEntries(rows.filter((row) => row.success).map((row) => parseJsonResult<Submission>(row.data)));
    if (account) {
      const own = await readContract("get_provider_submission", [BigInt(id), account]);
      const parsed = own.success ? parseJsonResult<Partial<Submission>>(own.data) : {};
      setMyEntry(typeof parsed.id === "number" ? parsed as Submission : null);
    }
    setMessage(`Verified ${next.status} with ${next.candidates} sealed candidate(s).`);
    return next;
  }, [id, wallet]);

  useEffect(() => { const timer = window.setTimeout(() => void sync(), 0); return () => window.clearTimeout(timer); }, [sync]);
  useEffect(() => { const tick = () => setNow(Math.floor(Date.now() / 1000)); tick(); const timer = window.setInterval(tick, 1000); return () => window.clearInterval(timer); }, []);

  async function connect() {
    const result = await connectWallet();
    if (!result.success || typeof result.data !== "string") { setMessage(result.error || "Wallet connection failed."); return; }
    const account = result.data.toLowerCase();
    setWallet(account);
    await sync(account);
  }

  async function transact(name: string, args: unknown[], expected: string | string[], value = BigInt(0), verifyEntry?: string) {
    setBusy(true);
    try {
      const result = await writeContract(name, args, value);
      if (!result.success) { setMessage(result.error || "Transaction failed."); return; }
      const next = await sync(wallet);
      const allowed = Array.isArray(expected) ? expected : [expected];
      let entryVerified = true;
      if (verifyEntry && wallet) {
        const own = await readContract("get_provider_submission", [BigInt(id), wallet]);
        const parsed = own.success ? parseJsonResult<Partial<Submission>>(own.data) : {};
        entryVerified = parsed.status === verifyEntry;
      }
      setMessage(next && allowed.includes(next.status) && entryVerified ? `State and caller record verified. Transaction: ${result.hash}` : "Receipt completed, but the expected contract state was not proven.");
    } finally { setBusy(false); }
  }

  async function commitEntry(event: FormEvent) { event.preventDefault(); if (tournament) await transact("commit_submission", [BigInt(id), commit.manifest, commit.sample, commit.license], "OPEN_COMMIT", BigInt(tournament.bond), "COMMITTED"); }
  async function revealEntry(event: FormEvent) { event.preventDefault(); await transact("reveal_dataset", [BigInt(id), reveal.manifest, reveal.sample, reveal.license, reveal.note], "OPEN_REVEAL", BigInt(0), "REVEALED"); }
  async function withdrawCredit() {
    if (!wallet) { await connect(); return; }
    setBusy(true);
    try {
      const before = await readContract("get_withdrawable", [wallet]);
      if (!before.success || BigInt(String(before.data ?? "0")) === BigInt(0)) { setMessage("This wallet has no withdrawable credit."); return; }
      const result = await writeContract("withdraw");
      const after = result.success ? await readContract("get_withdrawable", [wallet]) : null;
      setMessage(result.success && after?.success && BigInt(String(after.data ?? "0")) === BigInt(0) ? `Withdrawal verified. Transaction: ${result.hash}` : result.error || "Withdrawal state was not verified.");
    } finally { setBusy(false); }
  }

  if (!tournament) return <section className="detail-page"><Notice>{message}</Notice></section>;
  const isBuyer = wallet === tournament.buyer.toLowerCase();
  const isProvider = Boolean(myEntry);
  const canCommit = Boolean(wallet) && !isBuyer && !isProvider && now < tournament.commit_deadline && tournament.candidates < tournament.cap;
  const canReveal = Boolean(wallet) && myEntry?.status === "COMMITTED" && now >= tournament.commit_deadline && now < tournament.reveal_deadline;

  return <section className="detail-page">
    <div className="detail-header"><Link className="back-link" href="/"><ArrowLeft size={16}/> Market</Link><div className="detail-title"><span className="row-id">TOURNAMENT #{id}</span><h1>{tournament.title}</h1><StatusPill status={tournament.status}/></div><p>{tournament.use_case}</p></div>
    <div className="evidence-ledger"><div><span>BUYER</span><strong>{shortAddress(tournament.buyer)}</strong><span>CANDIDATES</span><strong>{tournament.candidates}/{tournament.cap}</strong></div><div><span>PRIZE</span><strong>{tournament.prize} wei</strong><span>BOND</span><strong>{tournament.bond} wei</strong></div><div><span>RUBRIC</span><a href={tournament.rubric_url} target="_blank">Open source <ExternalLink size={13}/></a><code>{tournament.rubric_digest.slice(0, 18)}…</code></div></div>
    <Notice>{message}</Notice>
    {!wallet && <button className="button button-primary" onClick={() => void connect()}><WalletCards size={17}/> Connect wallet to reveal valid actions</button>}
    {tournament.status === "OPEN_COMMIT" && canCommit && <form className="action-form" onSubmit={commitEntry}><p className="eyebrow">PROVIDER · SEALED COMMIT</p><h2>Commit digests before reveal.</h2>{(["manifest", "sample", "license"] as const).map((key) => <label key={key}>{key} SHA-256<input required value={commit[key]} onChange={(event) => setCommit({ ...commit, [key]: event.target.value })} placeholder="sha256:..."/></label>)}<button className="button button-primary" disabled={busy}>Post exact bond & commit <ArrowRight size={17}/></button></form>}
    {tournament.status === "OPEN_COMMIT" && now >= tournament.commit_deadline && <button className="button button-quiet" disabled={busy} onClick={() => void transact("start_reveal", [BigInt(id)], "OPEN_REVEAL")}>Start reveal</button>}
    {tournament.status === "OPEN_REVEAL" && canReveal && <form className="action-form" onSubmit={revealEntry}><p className="eyebrow">PROVIDER · REVEAL</p><h2>Reveal your immutable packet.</h2>{(["manifest", "sample", "license"] as const).map((key) => <label key={key}>{key} URL<input required value={reveal[key]} onChange={(event) => setReveal({ ...reveal, [key]: event.target.value })}/></label>)}<label>Disclosure note<textarea required value={reveal.note} onChange={(event) => setReveal({ ...reveal, note: event.target.value })}/></label><button className="button button-primary" disabled={busy}>Reveal packet</button></form>}
    {tournament.status === "OPEN_REVEAL" && now >= tournament.reveal_deadline && <button className="button button-quiet" disabled={busy} onClick={() => void transact("close_reveal", [BigInt(id)], "READY_FOR_JURY")}>Close reveal</button>}
    {tournament.status === "READY_FOR_JURY" && <div className="decision-panel"><Scale/><h2>Rank eligible datasets.</h2><button className="button button-primary" disabled={busy} onClick={() => void transact("judge_tournament", [BigInt(id)], ["RULING_READY", "EVIDENCE_UNAVAILABLE"])}>Run comparative jury</button></div>}
    {tournament.status === "RULING_READY" && <div className="verdict-panel"><strong>{tournament.outcome}</strong><p>{tournament.reason}</p><button className="button button-primary" disabled={busy} onClick={() => void transact("settle_tournament", [BigInt(id)], "SETTLED")}>Assign deterministic credits</button></div>}
    {tournament.status === "EVIDENCE_UNAVAILABLE" && (isBuyer || isProvider) && <div className="recovery-panel"><h2>Fail-closed recovery</h2><p>Buyer and one provider may approve immediately; after the recovery deadline either party may finish recovery.</p><button className="button button-primary" disabled={busy} onClick={() => void transact("recover_unavailable", [BigInt(id)], ["EVIDENCE_UNAVAILABLE", "SETTLED"])}>Approve recovery</button></div>}
    {tournament.status === "SETTLED" && wallet && <button className="button button-primary" disabled={busy} onClick={() => void withdrawCredit()}>Withdraw my verified credit</button>}
    <section className="packet"><div className="section-heading"><h2>Candidate matrix</h2></div><div className="packet-grid">{entries.map((entry) => <article key={entry.id}><span>#{entry.id} · {entry.status}</span><strong>{shortAddress(entry.provider)}</strong><code>rank {entry.rank || "—"}</code>{entry.manifest_url && <a href={entry.manifest_url} target="_blank">Manifest <ExternalLink size={13}/></a>}</article>)}</div></section>
  </section>;
}
