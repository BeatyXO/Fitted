/** EIP-1193 wallet session: authorization stays with the wallet, not local storage.
 * Reconnect is non-interactive and only uses eth_accounts after explicit consent.
 */
export const STUDIO_CHAIN_ID = 61999;
export const STUDIO_CHAIN_HEX = '0xf22f';
export const STUDIO_RPC = 'https://studio.genlayer.com/api';
export const STUDIO_EXPLORER = 'https://explorer-studio.genlayer.com';
export const RECONNECT_KEY = 'fitted:wallet:reconnect:v1';

export const isAddress = (value) => /^0x[0-9a-fA-F]{40}$/.test(value || '');
export const chainIsStudio = (chainId) => {
  if (typeof chainId !== 'string' || !/^0x[0-9a-f]+$/i.test(chainId)) return false;
  return Number.parseInt(chainId, 16) === STUDIO_CHAIN_ID;
};
export const friendlyWalletError = (error, fallback = 'Wallet request failed') => {
  if (error?.code === 4001) return 'Request rejected in your wallet.';
  if (error?.code === -32002) return 'A wallet request is already open. Check your wallet extension.';
  if (error?.code === 4900 || error?.code === 4901) return 'Wallet is not connected to the selected network.';
  return (typeof error?.message === 'string' && error.message.trim()) || fallback;
};
export const studioNetworkParameter = () => ({
  chainId: STUDIO_CHAIN_HEX,
  chainName: 'GenLayer StudioNet',
  rpcUrls: [STUDIO_RPC],
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  blockExplorerUrls: [STUDIO_EXPLORER],
});

export class WalletSession {
  constructor({ provider, storage, onChange = () => {} }) {
    this.provider = provider;
    this.storage = storage;
    this.onChange = onChange;
    this.address = '';
    this.chainId = '';
    this.connected = false;
    this.requesting = false;
    this.menuOpen = false;
    this.generation = 0;
    this.started = false;
    this.onAccounts = accounts => this.handleAccounts(accounts);
    this.onChain = id => { this.chainId = id || ''; this.changed(); };
    this.onDisconnect = () => { this.clear(); };
  }
  get installed() { return !!this.provider?.request; }
  get correctChain() { return chainIsStudio(this.chainId); }
  get snapshot() {
    return { installed: this.installed, address: this.address, chainId: this.chainId,
      connected: this.connected, correctChain: this.correctChain, requesting: this.requesting, menuOpen: this.menuOpen };
  }
  changed() { this.onChange(this.snapshot); }
  clear() { this.address = ''; this.connected = false; this.chainId = ''; this.menuOpen = false; this.changed(); }
  handleAccounts(accounts) {
    const address = Array.isArray(accounts) && isAddress(accounts[0]) ? accounts[0] : '';
    this.address = address;
    this.connected = !!address;
    if (!address) this.menuOpen = false;
    this.changed();
  }
  async start() {
    if (this.started) return;
    this.started = true;
    if (!this.installed) { this.changed(); return; }
    this.provider.on?.('accountsChanged', this.onAccounts);
    this.provider.on?.('chainChanged', this.onChain);
    this.provider.on?.('disconnect', this.onDisconnect);
    if (this.storage?.getItem(RECONNECT_KEY) === 'yes') await this.restore();
    else await this.syncChain();
  }
  async syncChain() {
    if (!this.installed) return;
    try { this.chainId = await this.provider.request({ method: 'eth_chainId' }); this.changed(); }
    catch { /* Read-only network query can fail during wallet startup. */ }
  }
  async restore() {
    if (!this.installed) return;
    const current = ++this.generation;
    try {
      const accounts = await this.provider.request({ method: 'eth_accounts' });
      if (current !== this.generation || this.storage?.getItem(RECONNECT_KEY) !== 'yes') return;
      this.handleAccounts(accounts);
      await this.syncChain();
    } catch { this.clear(); }
  }
  async connect() {
    if (!this.installed) throw new Error('Install an EIP-1193 wallet such as MetaMask to connect.');
    if (this.requesting) return;
    this.requesting = true; this.changed();
    const current = ++this.generation;
    try {
      const accounts = await this.provider.request({ method: 'eth_requestAccounts' });
      if (current !== this.generation) return;
      this.handleAccounts(accounts);
      if (!this.connected) throw new Error('Your wallet did not authorize an account.');
      this.storage?.setItem(RECONNECT_KEY, 'yes');
      await this.syncChain();
    } catch (error) { throw new Error(friendlyWalletError(error, 'Could not connect wallet')); }
    finally { this.requesting = false; this.changed(); }
  }
  async switchToStudio() {
    if (!this.installed) throw new Error('No injected wallet detected.');
    if (!this.connected) throw new Error('Connect your wallet first.');
    try {
      await this.provider.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: STUDIO_CHAIN_HEX }] });
    } catch (error) {
      if (error?.code !== 4902) throw new Error(friendlyWalletError(error, 'Unable to switch to StudioNet'));
      try {
        await this.provider.request({ method: 'wallet_addEthereumChain', params: [studioNetworkParameter()] });
        await this.provider.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: STUDIO_CHAIN_HEX }] });
      } catch (addError) { throw new Error(friendlyWalletError(addError, 'Unable to add GenLayer StudioNet')); }
    }
    await this.syncChain();
    if (!this.correctChain) throw new Error('The wallet did not confirm StudioNet (61999). Switch networks in the wallet and retry.');
    return this.chainId;
  }
  /** Disconnect removes app consent; wallet permission revocation is optional and provider-specific. */
  async disconnect() {
    this.generation++;
    this.storage?.removeItem(RECONNECT_KEY);
    this.clear();
    if (this.installed) {
      try { await this.provider.request({ method: 'wallet_revokePermissions', params: [{ eth_accounts: {} }] }); }
      catch { /* Browser-side disconnect still works; some wallets don't implement permission revocation. */ }
    }
  }
  setMenu(open) { this.menuOpen = this.connected && !!open; this.changed(); }
  dispose() {
    this.provider?.removeListener?.('accountsChanged', this.onAccounts);
    this.provider?.removeListener?.('chainChanged', this.onChain);
    this.provider?.removeListener?.('disconnect', this.onDisconnect);
  }
}
