# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import hashlib
import json
from datetime import datetime


@gl.evm.contract_interface
class _Recipient:
    class View: pass
    class Write: pass


MAX_CANDIDATES = 5
COMMIT_SECONDS = 300
REVEAL_SECONDS = 300


class DataProofMarket(gl.Contract):
    tournament_count: u256
    submission_count: u256
    tournament_data: TreeMap[u256, str]
    submission_data: TreeMap[u256, str]
    tournament_slot: TreeMap[str, u256]
    provider_entry: TreeMap[str, u256]
    credits: TreeMap[str, u256]
    total_received: u256
    active_prizes: u256
    active_bonds: u256
    total_credited: u256
    total_withdrawn: u256

    def __init__(self):
        self.tournament_count = u256(0)
        self.submission_count = u256(0)
        self.total_received = u256(0)
        self.active_prizes = u256(0)
        self.active_bonds = u256(0)
        self.total_credited = u256(0)
        self.total_withdrawn = u256(0)

    def _load(self, raw: str) -> dict:
        return json.loads(raw)

    def _save_t(self, tid: u256, value: dict) -> None:
        self.tournament_data[tid] = json.dumps(value, sort_keys=True, separators=(",", ":"))

    def _save_s(self, sid: u256, value: dict) -> None:
        self.submission_data[sid] = json.dumps(value, sort_keys=True, separators=(",", ":"))

    def _now(self) -> int:
        try:
            raw = str(gl.message_raw["datetime"])
            return int(datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp())
        except Exception:
            raise gl.vm.UserError("AUTHORITATIVE_TIME_UNAVAILABLE")

    def _url_ok(self, value: str) -> bool:
        low = value.lower()
        prefix = "https://ipfs.io/ipfs/" if low.startswith("https://ipfs.io/ipfs/") else "https://arweave.net/" if low.startswith("https://arweave.net/") else ""
        ident = low[len(prefix):] if prefix else ""
        return prefix != "" and len(value) <= 500 and len(ident) >= 32 and "example" not in ident and "replace" not in ident

    def _digest_ok(self, value: str) -> bool:
        if not value.startswith("sha256:") or len(value) != 71 or value[7:] == "0" * 64:
            return False
        try:
            int(value[7:], 16)
            return True
        except Exception:
            return False

    def _slot(self, tid: u256, slot: int) -> str:
        return str(int(tid)) + ":" + str(slot)

    def _provider(self, tid: u256, address: str) -> str:
        return str(int(tid)) + ":" + address.lower()

    def _sid_at(self, tid: u256, slot: int):
        encoded = self.tournament_slot.get(self._slot(tid, slot), u256(0))
        return None if encoded == u256(0) else encoded - u256(1)

    def _credit(self, address: str, amount: int) -> None:
        if amount <= 0: return
        value = u256(amount)
        self.credits[address] = self.credits.get(address, u256(0)) + value
        self.total_credited = self.total_credited + value

    def _parse_ranking(self, raw) -> dict:
        if isinstance(raw, dict): return raw
        text = str(raw).strip()
        start = text.find("{"); end = text.rfind("}")
        if start < 0 or end <= start: return {"outcome": "UNAVAILABLE"}
        try:
            value = json.loads(text[start:end + 1])
            return value if isinstance(value, dict) else {"outcome": "UNAVAILABLE"}
        except Exception:
            return {"outcome": "UNAVAILABLE"}

    @gl.public.write.payable
    def open_tournament(self, title: str, use_case: str, rubric_url: str, rubric_digest: str, provider_bond: u256, max_candidates: u256) -> u256:
        prize = gl.message.value
        if len(title) < 4 or len(title) > 140: raise gl.vm.UserError("INVALID_TITLE")
        if len(use_case) < 30 or len(use_case) > 1200: raise gl.vm.UserError("INVALID_USE_CASE")
        if not self._url_ok(rubric_url): raise gl.vm.UserError("IMMUTABLE_RUBRIC_REQUIRED")
        if not self._digest_ok(rubric_digest): raise gl.vm.UserError("INVALID_RUBRIC_DIGEST")
        if prize == u256(0): raise gl.vm.UserError("PRIZE_REQUIRED")
        if provider_bond == u256(0) or provider_bond >= prize: raise gl.vm.UserError("INVALID_PROVIDER_BOND")
        if max_candidates < u256(2) or max_candidates > u256(MAX_CANDIDATES): raise gl.vm.UserError("INVALID_CANDIDATE_CAP")
        now = self._now()
        tid = self.tournament_count
        self._save_t(tid, {"id": int(tid), "buyer": gl.message.sender_address.as_hex.lower(), "title": title, "use_case": use_case, "rubric_url": rubric_url, "rubric_digest": rubric_digest.lower(), "prize": str(int(prize)), "bond": str(int(provider_bond)), "cap": int(max_candidates), "candidates": 0, "revealed": 0, "commit_deadline": now + COMMIT_SECONDS, "reveal_deadline": now + COMMIT_SECONDS + REVEAL_SECONDS, "recovery_deadline": 0, "buyer_recovery": False, "provider_recovery": False, "status": "OPEN_COMMIT", "outcome": "PENDING", "winner": -1, "runner_up": -1, "reason": "Waiting for sealed commitments."})
        self.tournament_count = tid + u256(1)
        self.total_received = self.total_received + prize
        self.active_prizes = self.active_prizes + prize
        return tid

    @gl.public.write.payable
    def commit_submission(self, tid: u256, manifest_digest: str, sample_digest: str, license_digest: str) -> u256:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid]); sender = gl.message.sender_address.as_hex.lower()
        if t["status"] != "OPEN_COMMIT" or self._now() >= t["commit_deadline"]: raise gl.vm.UserError("COMMIT_WINDOW_CLOSED")
        if sender == t["buyer"]: raise gl.vm.UserError("BUYER_CANNOT_COMPETE")
        key = self._provider(tid, sender)
        if self.provider_entry.get(key, u256(0)) != u256(0): raise gl.vm.UserError("DUPLICATE_PROVIDER")
        if t["candidates"] >= t["cap"]: raise gl.vm.UserError("CANDIDATE_CAP_REACHED")
        if gl.message.value != u256(int(t["bond"])): raise gl.vm.UserError("EXACT_BOND_REQUIRED")
        if not all(self._digest_ok(x) for x in (manifest_digest, sample_digest, license_digest)): raise gl.vm.UserError("INVALID_EVIDENCE_DIGEST")
        sid = self.submission_count
        self._save_s(sid, {"id": int(sid), "tournament_id": int(tid), "provider": sender, "manifest_digest": manifest_digest.lower(), "sample_digest": sample_digest.lower(), "license_digest": license_digest.lower(), "manifest_url": "", "sample_url": "", "license_url": "", "note": "", "bond": t["bond"], "status": "COMMITTED", "rank": 0})
        self.tournament_slot[self._slot(tid, t["candidates"])] = sid + u256(1)
        self.provider_entry[key] = sid + u256(1)
        t["candidates"] += 1; self._save_t(tid, t)
        self.submission_count = sid + u256(1)
        self.total_received += gl.message.value; self.active_bonds += gl.message.value
        return sid

    @gl.public.write
    def start_reveal(self, tid: u256) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid])
        if t["status"] != "OPEN_COMMIT": raise gl.vm.UserError("REVEAL_ALREADY_STARTED")
        if self._now() < t["commit_deadline"]: raise gl.vm.UserError("COMMIT_WINDOW_ACTIVE")
        t["status"] = "OPEN_REVEAL"; t["reason"] = "Commitments sealed; reveal immutable packets."
        self._save_t(tid, t); return t["status"]

    @gl.public.write
    def reveal_dataset(self, tid: u256, manifest_url: str, sample_url: str, license_url: str, note: str) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid]); now = self._now()
        if t["status"] != "OPEN_REVEAL" or now < t["commit_deadline"] or now >= t["reveal_deadline"]: raise gl.vm.UserError("REVEAL_WINDOW_CLOSED")
        encoded = self.provider_entry.get(self._provider(tid, gl.message.sender_address.as_hex.lower()), u256(0))
        if encoded == u256(0): raise gl.vm.UserError("COMMITMENT_NOT_FOUND")
        sid = encoded - u256(1); s = self._load(self.submission_data[sid])
        if s["status"] != "COMMITTED": raise gl.vm.UserError("SUBMISSION_ALREADY_REVEALED")
        if not all(self._url_ok(x) for x in (manifest_url, sample_url, license_url)): raise gl.vm.UserError("IMMUTABLE_EVIDENCE_REQUIRED")
        if len(note) < 20 or len(note) > 800: raise gl.vm.UserError("INVALID_SUBMISSION_NOTE")
        s.update({"manifest_url": manifest_url, "sample_url": sample_url, "license_url": license_url, "note": note, "status": "REVEALED"})
        t["revealed"] += 1; self._save_s(sid, s); self._save_t(tid, t); return "REVEALED"

    @gl.public.write
    def close_reveal(self, tid: u256) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid])
        if t["status"] != "OPEN_REVEAL" or self._now() < t["reveal_deadline"]: raise gl.vm.UserError("REVEAL_WINDOW_ACTIVE")
        for slot in range(MAX_CANDIDATES):
            if slot >= t["candidates"]: break
            sid = self._sid_at(tid, slot); s = self._load(self.submission_data[sid])
            if s["status"] == "COMMITTED": s["status"] = "NO_REVEAL"; self._save_s(sid, s)
        t["status"] = "READY_FOR_JURY"; t["reason"] = "Reveal closed; packets await verification and ranking."
        self._save_t(tid, t); return t["status"]

    @gl.public.write
    def judge_tournament(self, tid: u256) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid])
        if t["status"] != "READY_FOR_JURY": raise gl.vm.UserError("JURY_NOT_READY")
        eligible = []; packets = []
        for slot in range(MAX_CANDIDATES):
            if slot >= t["candidates"]: break
            sid = self._sid_at(tid, slot); s = self._load(self.submission_data[sid])
            if s["status"] != "REVEALED": continue
            urls = [s["manifest_url"], s["sample_url"], s["license_url"]]; digests = [s["manifest_digest"], s["sample_digest"], s["license_digest"]]
            def verify() -> str:
                try:
                    for i in range(3):
                        body = gl.nondet.web.get(urls[i]).body
                        if len(body) < 80: return "UNAVAILABLE"
                        if "sha256:" + hashlib.sha256(body).hexdigest() != digests[i]: return "INVALID"
                    return "VALID"
                except Exception: return "UNAVAILABLE"
            try: verification = str(gl.eq_principle.strict_eq(verify)).strip().upper()
            except Exception: verification = "UNAVAILABLE"
            if verification == "UNAVAILABLE":
                s["status"] = "UNAVAILABLE"; self._save_s(sid, s)
                continue
            s["status"] = "ELIGIBLE" if verification == "VALID" else "INVALID"; self._save_s(sid, s)
            if verification == "VALID": eligible.append(int(sid)); packets.append(s)
        if len(eligible) < 2:
            t.update({"outcome": "NO_QUALIFIED_DATASET", "status": "RULING_READY", "reason": "Fewer than two packets passed exact digest verification; no competitive winner can be selected. Revealed participation bonds remain refundable."}); self._save_t(tid, t); return t["status"]
        rubric_url, rubric_digest = t["rubric_url"], t["rubric_digest"]
        def evaluate() -> str:
            try:
                rubric_bytes = gl.nondet.web.get(rubric_url).body
                if "sha256:" + hashlib.sha256(rubric_bytes).hexdigest() != rubric_digest: return '{"outcome":"UNAVAILABLE","winner_id":-1,"runner_up_id":-1,"reason":"Rubric mismatch"}'
                rubric = gl.nondet.web.render(rubric_url, mode="text").strip()
                blocks = []
                for s in packets:
                    parts = [gl.nondet.web.render(s[k], mode="text").strip()[:2600] for k in ("manifest_url", "sample_url", "license_url")]
                    blocks.append("CANDIDATE #" + str(s["id"]) + "\n" + "\n".join(parts))
                return gl.nondet.exec_prompt("Rank datasets for: " + t["use_case"] + "\nRUBRIC:\n" + rubric[:2600] + "\n" + "\n".join(blocks) + '\nReturn ONLY {"outcome":"RANKED|NO_QUALIFIED_DATASET|UNAVAILABLE","winner_id":0,"runner_up_id":-1,"reason":"under 700 chars"}. Never invent ids.')
            except Exception: return '{"outcome":"UNAVAILABLE","winner_id":-1,"runner_up_id":-1,"reason":"Evidence unavailable"}'
        principle = "Equivalent only if outcome, winner id, and runner-up id match. Reason wording may differ. Never accept ids outside the eligible candidates."
        try: data = self._parse_ranking(gl.eq_principle.prompt_comparative(evaluate, principle))
        except Exception: data = {"outcome": "UNAVAILABLE"}
        outcome = str(data.get("outcome", "UNAVAILABLE")).upper()
        try:
            winner = int(data.get("winner_id", -1)); runner = int(data.get("runner_up_id", -1))
        except Exception:
            outcome = "UNAVAILABLE"; winner = -1; runner = -1
        reason = str(data.get("reason", "Unsafe ranking."))[:900]
        valid_rank = outcome == "RANKED" and winner in eligible and runner in eligible and runner != winner
        valid_empty = outcome in ("NO_QUALIFIED_DATASET", "UNAVAILABLE") and winner == -1 and runner == -1
        if not (valid_rank or valid_empty): outcome = "UNAVAILABLE"; winner = -1; runner = -1
        t.update({"outcome": outcome, "winner": winner, "runner_up": runner, "reason": reason, "status": "EVIDENCE_UNAVAILABLE" if outcome == "UNAVAILABLE" else "RULING_READY"})
        if outcome == "UNAVAILABLE": t["recovery_deadline"] = self._now() + REVEAL_SECONDS
        if winner >= 0:
            s = self._load(self.submission_data[u256(winner)]); s["rank"] = 1; self._save_s(u256(winner), s)
        self._save_t(tid, t); return t["status"]

    def _settle(self, tid: u256, t: dict) -> None:
        prize = int(t["prize"])
        self._credit(self._load(self.submission_data[u256(t["winner"])])["provider"] if t["outcome"] == "RANKED" else t["buyer"], prize)
        self.active_prizes -= u256(prize); t["prize"] = "0"
        for slot in range(MAX_CANDIDATES):
            if slot >= t["candidates"]: break
            sid = self._sid_at(tid, slot); s = self._load(self.submission_data[sid]); bond = int(s["bond"])
            refundable = s["status"] in ("ELIGIBLE", "REVEALED", "INVALID", "UNAVAILABLE")
            self._credit(s["provider"] if refundable else t["buyer"], bond)
            if s["status"] == "NO_REVEAL": s["status"] = "FORFEITED"
            s["bond"] = "0"; self.active_bonds -= u256(bond); self._save_s(sid, s)
        t["status"] = "SETTLED"; self._save_t(tid, t)

    @gl.public.write
    def settle_tournament(self, tid: u256) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid])
        if t["status"] != "RULING_READY": raise gl.vm.UserError("RULING_NOT_READY")
        self._settle(tid, t); return "SETTLED"

    @gl.public.write
    def recover_unavailable(self, tid: u256) -> str:
        if tid >= self.tournament_count: raise gl.vm.UserError("TOURNAMENT_NOT_FOUND")
        t = self._load(self.tournament_data[tid])
        if t["status"] != "EVIDENCE_UNAVAILABLE": raise gl.vm.UserError("RECOVERY_NOT_AVAILABLE")
        sender = gl.message.sender_address.as_hex.lower()
        if sender == t["buyer"]: t["buyer_recovery"] = True
        else:
            is_provider = False
            for slot in range(MAX_CANDIDATES):
                if slot >= t["candidates"]: break
                sid = self._sid_at(tid, slot)
                if self._load(self.submission_data[sid])["provider"] == sender: is_provider = True; break
            if not is_provider: raise gl.vm.UserError("PARTY_ONLY")
            t["provider_recovery"] = True
        timed_out = t["recovery_deadline"] > 0 and self._now() >= t["recovery_deadline"]
        if not ((t["buyer_recovery"] and t["provider_recovery"]) or timed_out):
            self._save_t(tid, t); return "RECOVERY_APPROVAL_RECORDED"
        t["outcome"] = "UNAVAILABLE"; self._settle(tid, t); return "SETTLED"

    @gl.public.write
    def withdraw(self) -> u256:
        sender = gl.message.sender_address.as_hex.lower(); amount = self.credits.get(sender, u256(0))
        if amount == u256(0): raise gl.vm.UserError("NOTHING_TO_WITHDRAW")
        if amount > self.balance: raise gl.vm.UserError("CUSTODY_INVARIANT_BROKEN")
        self.credits[sender] = u256(0); self.total_credited -= amount; self.total_withdrawn += amount
        _Recipient(Address(sender)).emit_transfer(value=amount); return amount

    @gl.public.view
    def get_tournament(self, tid: u256) -> str:
        return "{}" if tid >= self.tournament_count else self.tournament_data[tid]

    @gl.public.view
    def get_submission(self, sid: u256) -> str:
        return "{}" if sid >= self.submission_count else self.submission_data[sid]

    @gl.public.view
    def get_tournament_submission(self, tid: u256, slot: u256) -> str:
        if tid >= self.tournament_count: return "{}"
        t = self._load(self.tournament_data[tid])
        if int(slot) >= t["candidates"]: return "{}"
        sid = self._sid_at(tid, int(slot))
        return "{}" if sid is None or sid >= self.submission_count else self.submission_data[sid]

    @gl.public.view
    def get_provider_submission(self, tid: u256, address: str) -> str:
        if tid >= self.tournament_count: return "{}"
        encoded = self.provider_entry.get(self._provider(tid, address), u256(0))
        return "{}" if encoded == u256(0) else self.submission_data[encoded - u256(1)]

    @gl.public.view
    def get_withdrawable(self, address: str) -> str:
        return str(self.credits.get(address.lower(), u256(0)))

    @gl.public.view
    def get_state(self) -> str:
        return json.dumps({"tournament_count": str(self.tournament_count), "submission_count": str(self.submission_count), "active_prizes": str(self.active_prizes), "active_bonds": str(self.active_bonds), "total_received": str(self.total_received), "total_credited": str(self.total_credited), "total_withdrawn": str(self.total_withdrawn)}, sort_keys=True, separators=(",", ":"))
