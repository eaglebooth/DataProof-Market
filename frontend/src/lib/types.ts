export type MarketState = {
  active_escrow: string;
  bounty_count: string;
  total_buyer_refunded: string;
  total_provider_paid: string;
  total_received: string;
  total_transferred: string;
};

export type Bounty = {
  id: string;
  buyer: string;
  provider: string;
  title: string;
  use_case: string;
  rubric_url: string;
  rubric_digest: string;
  manifest_url: string;
  manifest_digest: string;
  sample_url: string;
  sample_digest: string;
  license_url: string;
  license_digest: string;
  submission_note: string;
  submitter: string;
  escrow: string;
  partial_reward: string;
  status: string;
  decision: string;
  score: string;
  reason: string;
  buyer_recovery: string;
  provider_recovery: string;
};

export const EMPTY_STATE: MarketState = {
  active_escrow: "0",
  bounty_count: "0",
  total_buyer_refunded: "0",
  total_provider_paid: "0",
  total_received: "0",
  total_transferred: "0",
};
