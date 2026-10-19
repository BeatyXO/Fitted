# Wallet UX and transaction boundaries (v1.1)

Fitted intentionally supports injected EIP-1193 wallets. This includes MetaMask-style extensions. Multi-provider discovery (EIP-6963), WalletConnect and mobile deeplinking are not implemented; add these only with their real provider SDKs and integration tests.

## Connection

- Connecting calls `eth_requestAccounts` on user activation, **without requiring a deployed contract address**.
- After a successful connection, browser local storage keeps only a reconnection **consent flag** (`fitted:wallet:reconnect:v1`). No mnemonic, secret, private key, transaction signature or auth token is stored.
- On reload, Fitted calls only `eth_accounts` (does **not** display a fresh connect permission prompt). The provider must still have authorized this origin. If authorization was revoked, the page shows disconnected.
- Wallet changes and chain changes are consumed through `accountsChanged`, `chainChanged`, and `disconnect`; the banner and network CTA update accordingly.
- Clicking an already connected account opens a dropdown to copy the full address, switch networks, or disconnect.
- Fitted disconnect clears local reconnection consent and attempts `wallet_revokePermissions` when implemented. Some wallets do not support revocation; the page is still disconnected **locally** and will not silently reconnect on refresh. The extension may retain permission until manually revoked there.
- Copy address uses the standard Clipboard API, which needs HTTPS or localhost. Failure is reported, not silently ignored.

## Wrong network

- StudioNet ID is `61999` (`0xf22f`), RPC `https://studio.genlayer.com/api`, symbol `GEN`, explorer `https://explorer-studio.genlayer.com`.
- If connected on another network (or unknown chain), show **Switch to StudioNet**.
- Clicking it asks for `wallet_switchEthereumChain`. If wallet responds with EIP-1193/MetaMask `4902` (unknown chain), ask for `wallet_addEthereumChain`, then retry switch.
- User rejection (`4001`) never triggers automatic add or silent retries.
- The transaction client re-queries the current chain **immediately before a write**, and refuses to sign unless StudioNet is confirmed. A wallet’s explicit approval remains required for every write.

## Browser presentation

Cards, hero tiles, stat tiles and form rules have subtle lift and lime glow on hover, with reduced-motion support. Header wallet controls and the dropdown have focus-visible styling, keyboard Escape dismissal, and click-away dismissal. The mobile breakpoints (1440, 390 and 375 px) are covered by local Chromium smoke checks. The browser suite stubs the EIP-1193 wallet **only** to test local UI; it does not fabricate a contract, validators, blockchain network or certificate.

## SDK and transaction integration boundary

The Vite production build bundles the exact-pinned `genlayer-js@1.1.8` package from `package-lock.json`; there is no runtime SDK CDN import. The UI uses the SDK's `writeContract({ value: 0n })`, `waitForTransactionReceipt({ status: TransactionStatus.FINALIZED })`, and checks `ExecutionResult.FINISHED_WITH_RETURN` before refreshing chain state. Live wallet compatibility, StudioNet RPC behavior, fees and finality still require a funded wallet and a reachable StudioNet RPC; these are not established by the browser unit tests or local build.
