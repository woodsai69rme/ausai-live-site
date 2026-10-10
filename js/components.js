class SiteHeader extends HTMLElement {
  connectedCallback() {
    // Support nested pages for local dev (e.g. root="..")
    const root = this.getAttribute('root') || '.';
    
    this.innerHTML = `
<nav>
  <div class="container">
    <div class="logo"><a href="${root}/index.html" style="color:inherit;text-decoration:none;">Aus<span>AI</span>.tech</a></div>
    <ul class="nav-links">
      <li><a href="${root}/index.html#services">Services</a></li>
      <li><a href="${root}/studio.html">Studio</a></li>
      <li><a href="${root}/catalog.html">Catalog</a></li>
      <li><a href="${root}/portfolio/index.html">Portfolio</a></li>
      <li><a href="${root}/tiers.html">Pricing</a></li>
      <li><a href="${root}/portal.html">Client Portal</a></li>
      <li><a href="${root}/faq.html">FAQ</a></li>
      <li><a href="${root}/book.html" class="nav-cta">Book a Call →</a></li>
    </ul>
    <button class="mobile-menu" aria-label="Menu">☰</button>
  </div>
</nav>
    `;

    // Handle mobile menu toggle
    const btn = this.querySelector('.mobile-menu');
    const links = this.querySelector('.nav-links');
    if (btn && links) {
      btn.addEventListener('click', () => links.classList.toggle('show'));
    }
  }
}
customElements.define('site-header', SiteHeader);

class SiteFooter extends HTMLElement {
  connectedCallback() {
    const root = this.getAttribute('root') || '.';
    
    this.innerHTML = `
<footer>
  <div class="container">
    <div class="logo" style="font-size: 1.1rem;"><a href="${root}/index.html" style="color:inherit;text-decoration:none;">Aus<span>AI</span>.tech</a></div>
    <ul class="footer-links">
      <li><a href="${root}/index.html#services">Services</a></li>
      <li><a href="${root}/studio.html">Studio</a></li>
      <li><a href="${root}/catalog.html">Catalog</a></li>
      <li><a href="${root}/portfolio/index.html">Portfolio</a></li>
      <li><a href="${root}/tiers.html">Pricing</a></li>
      <li><a href="${root}/portal.html">Client Portal</a></li>
      <li><a href="${root}/faq.html">FAQ</a></li>
      <li><a href="${root}/book.html">Contact</a></li>
    </ul>
    <div style="margin-top: 24px; display: flex; gap: 24px; font-size: 0.85rem; color: var(--text-dim);">
      <a href="${root}/legal/terms.html" style="color: inherit;">Terms & Conditions</a>
      <a href="${root}/legal/privacy.html" style="color: inherit;">Privacy Policy</a>
      <a href="${root}/legal/refunds.html" style="color: inherit;">Refunds</a>
    </div>
    <p class="footer-copy" style="margin-top: 16px;">© 2026 AusAI Tech Pty Ltd. All rights reserved. Based in Australia.</p>
  </div>
</footer>
    `;
  }
}
customElements.define('site-footer', SiteFooter);
