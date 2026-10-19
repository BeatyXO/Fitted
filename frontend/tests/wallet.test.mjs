import test from 'node:test';
import assert from 'node:assert/strict';
import { WalletSession, RECONNECT_KEY, STUDIO_CHAIN_HEX, chainIsStudio, studioNetworkParameter } from '../wallet.js';
const ADDRESS = '0x' + 'a'.repeat(40);
function kit({ chain = '0x1', accounts = [ADDRESS], failSwitch = null } = {}) {
  const values = new Map();
  const storage = { getItem: k => values.get(k) ?? null, setItem: (k, v) => values.set(k, v), removeItem: k => values.delete(k) };
  const events = new Map();
  const calls = [];
  let authorized = accounts;
  let currentChain = chain;
  const provider = {
    on: (key, fn) => events.set(key, fn), removeListener: key => events.delete(key),
    async request({ method, params }) {
      calls.push({ method, params });
      if (method === 'eth_accounts' || method === 'eth_requestAccounts') return authorized;
      if (method === 'eth_chainId') return currentChain;
      if (method === 'wallet_revokePermissions') return null;
      if (method === 'wallet_switchEthereumChain') {
        if (failSwitch) { const code = failSwitch; failSwitch = null; throw { code }; }
        currentChain = params[0].chainId; events.get('chainChanged')?.(currentChain); return null;
      }
      if (method === 'wallet_addEthereumChain') return null;
      throw new Error(`Unexpected method ${method}`);
    },
  };
  return { provider, storage, calls, events, values, setAccounts(v) { authorized = v; events.get('accountsChanged')?.(v); } };
}
test('chain matching rejects malformed and foreign networks', () => {
  assert.equal(chainIsStudio('0xf22f'), true); assert.equal(chainIsStudio('0xF22F'), true);
  assert.equal(chainIsStudio('61999'), false); assert.equal(chainIsStudio('0x1'), false);
  assert.equal(studioNetworkParameter().chainId, STUDIO_CHAIN_HEX);
});
test('startup never requests permission without reconnect consent', async () => {
  const k = kit(); const w = new WalletSession(k); await w.start();
  assert.equal(k.calls.some(x => x.method === 'eth_requestAccounts'), false);
  assert.equal(k.calls.some(x => x.method === 'eth_accounts'), false);
  assert.equal(w.connected, false);
});
test('connect persists opt-in and restore only uses eth_accounts', async () => {
  const k = kit({ chain: STUDIO_CHAIN_HEX }); const w = new WalletSession(k); await w.start(); await w.connect();
  assert.equal(w.address, ADDRESS); assert.equal(w.correctChain, true);
  assert.equal(k.storage.getItem(RECONNECT_KEY), 'yes');
  const restored = new WalletSession(k); await restored.start();
  assert.equal(restored.address, ADDRESS);
  assert.equal(k.calls.filter(x => x.method === 'eth_requestAccounts').length, 1);
});
test('disconnect clears consent and session, refresh does not reconnect', async () => {
  const k = kit(); const w = new WalletSession(k); await w.start(); await w.connect(); await w.disconnect();
  assert.equal(w.connected, false); assert.equal(k.storage.getItem(RECONNECT_KEY), null);
  const refreshed = new WalletSession(k); await refreshed.start(); assert.equal(refreshed.connected, false);
});
test('handles accountsChanged and network changes', async () => {
  const k = kit(); const w = new WalletSession(k); await w.start(); await w.connect();
  k.events.get('chainChanged')(STUDIO_CHAIN_HEX); assert.equal(w.correctChain, true);
  k.setAccounts([]); assert.equal(w.connected, false);
});
test('switches installed network and confirms chain before use', async () => {
  const k = kit(); const w = new WalletSession(k); await w.start(); await w.connect(); await w.switchToStudio();
  assert.equal(w.correctChain, true);
  assert.equal(k.calls.find(x => x.method === 'wallet_switchEthereumChain').params[0].chainId, '0xf22f');
});
test('unknown network adds StudioNet then retries switching', async () => {
  const k = kit({ failSwitch: 4902 }); const w = new WalletSession(k); await w.start(); await w.connect(); await w.switchToStudio();
  assert.equal(w.correctChain, true);
  assert.equal(k.calls.filter(x => x.method === 'wallet_switchEthereumChain').length, 2);
  assert.equal(k.calls.filter(x => x.method === 'wallet_addEthereumChain').length, 1);
});
test('user rejection does not automatically add or switch chain', async () => {
  const k = kit({ failSwitch: 4001 }); const w = new WalletSession(k); await w.start(); await w.connect();
  await assert.rejects(() => w.switchToStudio(), /rejected/);
  assert.equal(k.calls.some(x => x.method === 'wallet_addEthereumChain'), false);
});
test('reconnect preference with no authorized accounts leaves session disconnected', async () => {
  const k = kit({accounts:[]}); k.storage.setItem(RECONNECT_KEY, 'yes'); const w = new WalletSession(k); await w.start();
  assert.equal(w.connected, false);
});
test('disconnect while stale reconnect request is pending prevents late resurrection', async () => {
  let release; const pending = new Promise(resolve => release = resolve);
  const k = kit(); k.storage.setItem(RECONNECT_KEY,'yes');
  const raw = k.provider.request; k.provider.request = async q => q.method === 'eth_accounts' ? pending : raw(q);
  const w = new WalletSession(k); const startup = w.start(); await w.disconnect(); release([ADDRESS]); await startup;
  assert.equal(w.connected, false);
});
