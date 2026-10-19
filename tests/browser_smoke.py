"""Real Chromium smoke on local static origin. EIP-1193 wallet is stubbed ONLY for UI tests;
no mock validator or chain read is ever represented as a live attestation.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / 'frontend'
HTML = (ROOT / 'index.html').read_text()
HTML = HTML.replace('<script type="module" src="./app.js"></script>', '')
HTML = HTML.replace('<link rel="stylesheet" href="./styles.css" />', '')
HTML = HTML.replace('<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet" />', '')
JS = (ROOT/'wallet.js').read_text().replace('export const ', 'const ').replace('export class ', 'class ')
JS += '\n' + (ROOT/'app.js').read_text().split('\n',1)[1]
STYLES = (ROOT/'styles.css').read_text()

provider_script = """
(() => {
 const ADDRESS='0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
 const listeners = {};
 let accounts = [];
 let chain = '0x1';
 const calls = [];
 window.__walletTest = {
   calls, address: ADDRESS,
   setChain(v){chain=v;listeners.chainChanged?.forEach(f=>f(chain));},
   revoke(){accounts=[];listeners.accountsChanged?.forEach(f=>f(accounts));}
 };
 window.ethereum = {
   on(name,fn){(listeners[name]??=[]).push(fn);},
   removeListener(name,fn){listeners[name]=(listeners[name]||[]).filter(x=>x!==fn);},
   async request({method,params}){
     calls.push(method);
     if(method==='eth_accounts') return accounts;
     if(method==='eth_requestAccounts'){accounts=[ADDRESS]; return accounts;}
     if(method==='eth_chainId') return chain;
     if(method==='wallet_switchEthereumChain') {chain=params[0].chainId;listeners.chainChanged?.forEach(f=>f(chain));return null;}
     if(method==='wallet_revokePermissions'){accounts=[];return null;}
     if(method==='wallet_addEthereumChain') return null;
     throw new Error('Not implemented in this UI test: '+method);
   }
 };
})();
"""
with sync_playwright() as p:
    launch_opts = {'headless':True,'args':['--no-sandbox']}
    if os.path.isfile(os.environ.get('CHROMIUM_PATH','/usr/bin/chromium')):
        launch_opts['executable_path'] = os.environ.get('CHROMIUM_PATH','/usr/bin/chromium')
    browser = p.chromium.launch(**launch_opts)
    for width,height in [(1440,900),(390,844),(375,812)]:
        context = browser.new_context(viewport={'width':width,'height':height})
        context.add_init_script(provider_script)
        page = context.new_page()
        errors=[]
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(HTML)
        page.evaluate('''(() => {
          const values = new Map();
          const storage = {getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};
          Object.defineProperty(window,'localStorage',{configurable:true,value:storage});
        })()''')
        page.add_style_tag(content=STYLES)
        page.evaluate(provider_script)
        page.evaluate(JS)
        page.locator('h1').first.wait_for(state='visible')
        assert page.locator('h1').first.inner_text().startswith('Stop asking')
        assert page.get_by_text('No standards loaded').count() == 1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'overflow {width} homepage'
        # Wallet can connect without the contract deployed.
        page.locator('#wallet-button').click()
        page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('0xaaaa')")
        assert page.locator('#switch-network').is_visible(), 'Wrong network must expose switch CTA'
        page.locator('#switch-network').click()
        page.wait_for_function("document.querySelector('#switch-network').hidden")
        assert page.evaluate('window.__walletTest.calls.includes("wallet_switchEthereumChain")')
        page.locator('#wallet-button').click()
        assert page.get_by_text('Copy address').is_visible()
        assert page.get_by_text('Disconnect wallet').is_visible()
        page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable: true, value:{writeText:async v=>window.__copied=v}})")
        page.locator('[data-action="copy-wallet"]').click()
        page.wait_for_function('window.__copied===window.__walletTest.address')
        page.locator('#wallet-button').click()
        page.keyboard.press('Escape')
        assert not page.locator('#wallet-menu').is_visible()
        assert page.evaluate("localStorage.getItem('fitted:wallet:reconnect:v1')")=='yes'
        page.locator('#wallet-button').click()
        page.locator('[data-action="disconnect-wallet"]').click()
        page.wait_for_function("document.querySelector('#wallet-button')?.textContent.includes('Connect wallet')")
        assert page.evaluate("localStorage.getItem('fitted:wallet:reconnect:v1')") is None
        for route, expected in [('standards','Standards, not opinions.'),('candidates','Candidate evaluations.'),('certificates','Proof, with a paper trail.'),('compare','The fit comparison lab.')]:
            page.locator(f'.nav-item[data-route="{route}"]').click()
            page.wait_for_function('(x)=>document.querySelector("h1")?.textContent===x',arg=expected)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow {width} {route}'
        page.locator('[data-route="standards"]').first.click()
        page.locator('[data-route="new-standard"]').first.click()
        page.locator('#standard-form').wait_for(state='visible')
        page.locator('[data-action="add-rule"]').click()
        assert page.locator('[data-requirement]').count()==3
        # CSS hover glow and keyboard focus are real style features, never chain data.
        page.locator('[data-requirement]').first.hover()
        assert 'box-shadow' in page.locator('[data-requirement]').first.evaluate('(el)=>getComputedStyle(el).transitionProperty') or page.locator('[data-requirement]').first.evaluate('(el)=>getComputedStyle(el).boxShadow') != 'none'
        assert not errors,errors
        print(f'{width}px: navigation, wallet persistence/switch/disconnect, forms, zero overflow and JS exceptions passed')
        context.close()
    browser.close()
