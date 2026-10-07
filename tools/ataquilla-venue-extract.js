// Extracts every upcoming event on an Ataquilla venue page
// (https://entradas.ataquilla.com/es/ventaentradas/recintos/<id>-<venue>)
// with its exact event page, direct purchase link and sold-out flag.
// Run in the page (browser console or Claude in Chrome javascript_tool).
// Ataquilla is behind Cloudflare, so it must run in a real browser.
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 30; i++) {
    const more = [...document.querySelectorAll("button, a, div, span")]
      .find(e => e.children.length === 0 && /^\s*ver m[aá]s\s*$/i.test(e.textContent));
    if (!more) break;
    more.click();
    await sleep(1200);
  }
  const products = new Map();
  for (const card of document.querySelectorAll('[class*="style_content__"]')) {
    const fk = Object.keys(card).find(k => k.startsWith("__reactFiber"));
    let f = fk && card[fk];
    for (let i = 0; f && i < 4; i++, f = f.return) {
      const p = f.memoizedProps && f.memoizedProps.product;
      if (p && p.product_uri) { products.set(p.id, p); break; }
    }
  }
  return [...products.values()].map(p => ({
    name: p.name,
    first: p.first_session_date,
    last: p.last_session_date,
    price_from: p.price_from,
    sold_out: p.sold_out,
    page: "https://entradas.ataquilla.com/es/ventaentradas" + p.product_uri,
    sale_link: p.sale_link
  }));
})();
