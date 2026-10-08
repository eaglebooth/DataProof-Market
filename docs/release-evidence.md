# v2 Studionet Release Evidence

Canonical contract: [`0x6e2F...b168`](https://explorer-studio.genlayer.com/address/0x6e2F654E69562129aC62ea0a0289CAf960e6b168)

The release gate used three funded wallets and immutable Arweave evidence. Every
listed transaction reached `ACCEPTED`; state was read back after each phase.

## Tournament 0 — semantic rejection

Both packets passed raw-byte SHA-256 verification and became `ELIGIBLE`. The
comparative jury correctly returned `NO_QUALIFIED_DATASET` because carshare and
recall documents do not satisfy an urban-accessibility dataset request.

| Step | Explorer |
| --- | --- |
| Open tournament | [`0x79ab...cac1`](https://explorer-studio.genlayer.com/tx/0x79abc94d3a43180adcecb3b326b9a525b9fe2a47d7b148769772b999b440cac1) |
| Provider A commit | [`0x160f...96df`](https://explorer-studio.genlayer.com/tx/0x160fdd083a484344c9be74752fafad07329d3d15d8673880a2f71ca5ffb796df) |
| Provider B commit | [`0xd971...074a`](https://explorer-studio.genlayer.com/tx/0xd97180e237ed1c1d900f50f058cf29b8c35a0d1e4e5bbde5ba0b55652a94074a) |
| Start reveal | [`0xfa48...419c`](https://explorer-studio.genlayer.com/tx/0xfa48fc20eaad3f456c7c7ff9cd4888858b1d54a35c6260b55ad946750d00419c) |
| Provider A reveal | [`0xf281...ec17`](https://explorer-studio.genlayer.com/tx/0xf2811387dbd0a016ae04e6a2a6584994cf33d539c1050137a17b228b20e1ec17) |
| Provider B reveal | [`0x8b49...7936`](https://explorer-studio.genlayer.com/tx/0x8b492860fe1b8133ac41f7902c37e6b625992ce4fe061d2d4cd07f2c4e327936) |
| Close reveal | [`0x2749...2114`](https://explorer-studio.genlayer.com/tx/0x2749f9d80b2062ef5f2322278e832440016f26f2e5c3273739093abc882d2114) |
| Comparative jury | [`0x9a3f...ed51`](https://explorer-studio.genlayer.com/tx/0x9a3fbf1877bfcd7a2e64846bae6402ffcc092ba3716f7d12c2bd9b4a9d38ed51) |
| Settlement | [`0x8c00...b044`](https://explorer-studio.genlayer.com/tx/0x8c00fc2cf0ceef94b1a86615dc0b7c44b8d2c774b33af4a94cdeb8b4fe8eb044) |
| Buyer withdraws | [`0x4e6f...235b`](https://explorer-studio.genlayer.com/tx/0x4e6ff92feb4bc6b6826eee313da50c67dc874a18553259a7c126a5279c88235b) |
| Provider A withdraws | [`0x3202...abe4`](https://explorer-studio.genlayer.com/tx/0x32022f38487af26c6b30d8c17cf439d92d557a1fc6241c3acaa03be1f81fabe4) |
| Provider B withdraws | [`0xcaa6...c837`](https://explorer-studio.genlayer.com/tx/0xcaa6bd514797b065c686103f1903b7e3516cc165ca024f1c96dc87a7e7c0c837) |

## Tournament 1 — ranked winner payout

The use case matched the locked carshare policy. The jury ranked submission `2`
above submission `3`, citing its dual pickup baseline and complete return record.

| Step | Explorer |
| --- | --- |
| Open tournament | [`0xfd4b...bb86`](https://explorer-studio.genlayer.com/tx/0xfd4b593a43937b02da2661c5ed7347cb4cc87ea001aed7818fd7c8770ec7bb86) |
| Provider A commit | [`0x32d6...25ba`](https://explorer-studio.genlayer.com/tx/0x32d6581f2742b53b6418ff920974fa3e49244ac075622c0c838627da135c25ba) |
| Provider B commit | [`0x413d...6b06`](https://explorer-studio.genlayer.com/tx/0x413dc5cf4fefade54cff1be1c91d52a9847ad9d9f04725183c64c9708f006b06) |
| Start reveal | [`0x1081...1e4e`](https://explorer-studio.genlayer.com/tx/0x10818c3ff4390c69bc403beef2f5a92794d5faddbefe9d6e37bc9f8e547e1e4e) |
| Provider A reveal | [`0xd82a...c532`](https://explorer-studio.genlayer.com/tx/0xd82afb8154f9e6a9ff223d005441f9badf79aae023a0ec8e3a2a9e6a0577c532) |
| Provider B reveal | [`0x5e89...e19a`](https://explorer-studio.genlayer.com/tx/0x5e89b04490e659a1c35c8a221c1d598ac867091b30953f328b7fa23c9b5be19a) |
| Close reveal | [`0x7a73...e05`](https://explorer-studio.genlayer.com/tx/0x7a73480ea3bfd11db19f7efb22591ee9445842ced65134e0291b9bd666c12e05) |
| Comparative jury | [`0xd422...56ab`](https://explorer-studio.genlayer.com/tx/0xd422455fc58d77574d53ae17dfdd6c3ab9edf88ce517c674df8ecbd6bb7756ab) |
| Settlement | [`0xd6d0...f2b5`](https://explorer-studio.genlayer.com/tx/0xd6d0d72ef1df84ca14349194f87412444af4a14684124142ff504dd2774df2b5) |
| Winner withdraws 1100 wei | [`0x4883...6de3`](https://explorer-studio.genlayer.com/tx/0x488359100315829ef89c0d509be22e431f4de8a0e91a779aca478b1a3f736de3) |
| Runner-up withdraws 100 wei | [`0xdb2e...d8e3`](https://explorer-studio.genlayer.com/tx/0xdb2eeeaccd819ffdf6e80caa5eff44fca8d68d005d655aa9495ccd80e919d8e3) |

## Final state

```text
tournament_count = 2
submission_count = 4
total_received = 2400
total_withdrawn = 2400
active_prizes = 0
active_bonds = 0
total_credited = 0
```

Local release checks: 36 tests, ESLint, TypeScript, and Next.js production build.
