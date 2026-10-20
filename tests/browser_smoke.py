"""Chromium smoke against the built Vite frontend, served by ``vite preview``.

The injected EIP-1193 provider is a UI-only test double. This script never
submits transactions or represents local UI state as production evidence.
"""
from pathlib import Path
import os
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / "frontend"
CONTRACT = "0xCFd6184ad5589a329E8F89984d2FfEc98607cD72"

provider_script = r"""
(() => {
 const ADDRESS='0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
 const OTHER='0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
 const listeners={};
 const ACCOUNT_KEY='__fitted_ui_test_accounts';
 const CHAIN_KEY='__fitted_ui_test_chain';
 let accounts=JSON.parse(localStorage.getItem(ACCOUNT_KEY)||'[]');
 let chain=localStorage.getItem(CHAIN_KEY)||'0x1';
 let rejectConnect=false;
 const calls=[];
 const emit=(name,value)=>listeners[name]?.forEach(fn=>fn(value));
 window.__walletTest={
   calls,address:ADDRESS,other:OTHER,
   setAccounts(value){accounts=value;localStorage.setItem(ACCOUNT_KEY,JSON.stringify(value));emit('accountsChanged',value);},
   setChain(value){chain=value;localStorage.setItem(CHAIN_KEY,value);emit('chainChanged',value);},
   rejectNextConnect(){rejectConnect=true;},
 };
 window.ethereum={
   on(name,fn){(listeners[name]??=[]).push(fn);},
   removeListener(name,fn){listeners[name]=(listeners[name]||[]).filter(x=>x!==fn);},
   async request({method,params}){
     calls.push(method);
     if(method==='eth_accounts')return accounts;
     if(method==='eth_requestAccounts'){
       if(rejectConnect){rejectConnect=false;throw Object.assign(new Error('User rejected request'),{code:4001});}
       this.__walletTest?.setAccounts?.([ADDRESS]);
       accounts=[ADDRESS];localStorage.setItem(ACCOUNT_KEY,JSON.stringify(accounts));emit('accountsChanged',accounts);return accounts;
     }
     if(method==='eth_chainId')return chain;
     if(method==='wallet_switchEthereumChain'){chain=params[0].chainId;localStorage.setItem(CHAIN_KEY,chain);emit('chainChanged',chain);return null;}
     if(method==='wallet_addEthereumChain')return null;
     if(method==='wallet_revokePermissions'){accounts=[];localStorage.setItem(ACCOUNT_KEY,'[]');emit('accountsChanged',accounts);return null;}
     throw new Error('Not implemented in this UI-only test: '+method);
   }
 };
 // Keep the provider method independent of a browser wallet and the chain.
 window.ethereum.request=window.ethereum.request.bind(window.ethereum);
 window.ethereum.request.__walletTest=window.__walletTest;
})();
"""


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_preview(url, process):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Vite preview exited early with code {process.returncode}")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError):
            time.sleep(0.25)
    raise RuntimeError("Vite preview did not become ready within 30 seconds")


def main():
    npm = shutil.which("npm.cmd") if os.name == "nt" else shutil.which("npm")
    if not npm:
        raise RuntimeError("npm is required to serve the built Vite app")
    port = free_port()
    env = os.environ.copy()
    # Keep the browser smoke deterministic and avoid any inherited live address.
    env.pop("VITE_CONTRACT_ADDRESS", None)
    command = [npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(port), "--strictPort"]
    server = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}/"
    try:
        wait_for_preview(url, server)
        chromium_path = os.environ.get("CHROMIUM_PATH")
        launch_opts = {"headless": True, "args": ["--no-sandbox"]}
        if chromium_path and os.path.isfile(chromium_path):
            launch_opts["executable_path"] = chromium_path

        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_opts)
            for width, height in [(1440, 900), (390, 844), (375, 812)]:
                context = browser.new_context(viewport={"width": width, "height": height})
                context.add_init_script(provider_script)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                response = page.goto(url, wait_until="networkidle")
                assert response and response.status == 200
                assert page.locator('script[type="module"][src*="/assets/"]').count() == 1, "must load Vite-built module bundle"
                page.get_by_role("heading", name="Stop asking if it sounds right. Prove it fits.").wait_for(state="visible")
                assert page.get_by_role("textbox", name="Live contract address").count() == 1
                standards_nav = page.locator('.nav-item[data-route="standards"]')
                assert standards_nav.count() == 1
                assert "Standards" in standards_nav.evaluate("el => el.textContent")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"overflow {width}px homepage"

                # Keyboard focus and the live error region are part of the public UI.
                page.keyboard.press("Tab")
                assert page.evaluate("document.activeElement !== document.body"), "Tab should reach a focusable control"
                assert page.locator("#notice[role=status][aria-live=polite]").count() == 1

                # Wallet test double covers rejection, connect, wrong-network switch,
                # account changes, reconnect consent and explicit disconnect only.
                page.evaluate("window.__walletTest.rejectNextConnect()")
                page.locator("#wallet-button").click()
                page.get_by_text("Request rejected in your wallet.").wait_for(state="visible")
                page.locator("#wallet-button").click()
                page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('0xaaaa')")
                assert page.locator("#switch-network").is_visible(), "wrong network must expose switch CTA"
                page.locator("#switch-network").click()
                page.wait_for_function("document.querySelector('#switch-network').hidden")
                assert page.evaluate("window.__walletTest.calls.includes('wallet_switchEthereumChain')")
                page.evaluate("window.__walletTest.setAccounts([window.__walletTest.other])")
                page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('0xbbbb')")
                page.reload(wait_until="networkidle")
                page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('0xbbbb')")
                assert page.evaluate("window.__walletTest.calls.includes('eth_accounts')"), "consented refresh must use non-interactive eth_accounts"
                page.locator("#wallet-button").click()
                assert page.get_by_text("Copy address").is_visible()
                assert page.get_by_text("Disconnect wallet").is_visible()
                page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async v=>window.__copied=v}})")
                page.locator('[data-action="copy-wallet"]').click()
                page.wait_for_function("window.__copied===window.__walletTest.other")
                page.locator("#wallet-button").click()
                page.keyboard.press("Escape")
                assert not page.locator("#wallet-menu").is_visible(), "Escape should close wallet menu"
                assert page.evaluate("localStorage.getItem('fitted:wallet:reconnect:v1')==='yes'")
                page.locator("#wallet-button").click()
                page.locator('[data-action="disconnect-wallet"]').click()
                page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('Connect wallet')")
                assert page.evaluate("localStorage.getItem('fitted:wallet:reconnect:v1')===null")

                for route, heading in [
                    ("standards", "Standards, not opinions."),
                    ("candidates", "Candidate evaluations."),
                    ("certificates", "Proof, with a paper trail."),
                    ("compare", "The fit comparison lab."),
                ]:
                    page.locator(f'.nav-item[data-route="{route}"]').click()
                    page.get_by_role("heading", name=heading).wait_for(state="visible")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"overflow {width}px {route}"

                page.locator('[data-route="standards"]').first.click()
                page.locator('[data-route="new-standard"]').first.click()
                page.locator("#standard-form").wait_for(state="visible")
                assert page.get_by_label("Standard name").count() == 1
                page.locator('[data-action="add-rule"]').click()
                assert page.locator("[data-requirement]").count() == 3
                if width == 1440:
                    page.locator('[data-requirement]').first.hover()
                    hover = page.locator('[data-requirement]').first.evaluate("el=>getComputedStyle(el).boxShadow")
                    assert hover != "none", "requirement card should retain hover affordance"
                assert not errors, errors
                print(f"{width}px: Vite production bundle, keyboard, navigation, wallet session UI and form checks passed")
                context.close()

            # A real RPC failure must be visible, not replaced with synthetic data.
            error_context = browser.new_context(viewport={"width": 1440, "height": 900})
            error_context.add_init_script(provider_script)
            error_page = error_context.new_page()
            rpc_errors = []
            error_page.on("pageerror", lambda err: rpc_errors.append(str(err)))
            error_page.route("https://studio.genlayer.com/**", lambda route: route.abort("failed"))
            error_page.goto(f"{url}?contract={CONTRACT}", wait_until="networkidle")
            error_page.get_by_text("Could not read the deployed contract:", exact=False).wait_for(state="visible")
            assert "Could not read the deployed contract:" in error_page.locator("#notice").inner_text()
            assert error_page.get_by_text("No published standards found").count() == 0, "RPC failure must not masquerade as an empty registry"
            assert not rpc_errors, rpc_errors
            print("RPC failure: error state shown; no empty or successful state fabricated")
            error_context.close()
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
