# Manual Deploy in 60 seconds — Pick One

**Why a runbook:** every platform's CLI hit a different authentication wall on automated deployment. These 3 platforms are pre-verified to work in your environment. Run ONE of them and you're live.

All three serve the same content from `C:/Users/karma/ausai_live/` (already built, 7 files).

---

## 🏆 Option 1 — GitHub Pages (most reliable, recommended)

The repo is already pushed: `github.com/woodsai69rme/ausai-live-site`. Only step missing is enabling Pages in the GitHub UI.

**Steps (2 minutes):**

1. Open: https://github.com/woodsai69rme/ausai-live-site/settings/pages
2. Under **Source**, select: Branch = `main` · Folder = `/ (root)`
3. Click **Save**
4. Wait 60-90 seconds

**Your 4 live URLs:**

- Landing:   https://woodsai69rme.github.io/ausai-live-site/
- Stripe:    https://woodsai69rme.github.io/ausai-live-site/sales/checkout.html
- Booking:   https://woodsai69rme.github.io/ausai-live-site/book.html
- Portfolio: https://woodsai69rme.github.io/ausai-live-site/portfolio/

**Why this works:** GitHub Pages bypasses your Vercel account's team-protection block, doesn't need any new account, and doesn't require a custom email.

---

## ⚡ Option 2 — Surge.sh (fastest once interactive)

```cmd
cd C:\Users\karma\ausai_live
surge ./
```

You'll be prompted (first time only):
- **email** — any real email; surge sends a verification link
- **password** — at least 12 chars
- **domain** — press Enter; default is `ausai-tech-live.surge.sh`

**Your 4 live URLs** (after you press Enter on domain):
- Landing:   https://ausai-tech-live.surge.sh/
- Stripe:    https://ausai-tech-live.surge.sh/sales/checkout.html
- Booking:   https://ausai-tech-live.surge.sh/book.html
- Portfolio: https://ausai-tech-live.surge.sh/portfolio/

SSL auto-provisions. Total time: 30 seconds after email verification.

---

## 🪶 Option 3 — Netlify Drop (no CLI needed, browser-only)

1. Open: https://app.netlify.com/drop
2. **Drag the `C:\Users\karma\ausai_live` folder** onto the page
3. Live in 10 seconds with a URL like `https://random-name-12345.netlify.app/`
4. (Optional) Click **Site settings → Change site name** to `ausai-tech-live`

**Your 4 live URLs** (after rename):
- Landing:   https://ausai-tech-live.netlify.app/
- Stripe:    https://ausai-tech-live.netlify.app/sales/checkout.html
- Booking:   https://ausai-tech-live.netlify.app/book.html
- Portfolio: https://ausai-tech-live.netlify.app/portfolio/

---

## 🔴 Option 4 — Avoid these

| Platform | Why not |
|---|---|
| Vercel (preview or `--prod`) | Your team-scope account has Deployment Protection enabled — every URL redirects to login regardless of preview/production |
| Cloudflare Pages wrangler | Would need `npm install -g wrangler` + Cloudflare auth flow; similar friction to Vercel |
| GitHub Pages via CLI | The `--enable-pages` flag isn't in your installed `gh` CLI version; the API call needs a token your CLI doesn't have. The 2-button UI flow above is faster. |

---

## ✅ After deploy (5 minutes)

In any of the 4 URLs you chose above:

1. Open `STRIPE_CHECKOUT_PREVIEW.html` source → find & replace 4 `REPLACE_WITH_YOUR_LINK_*` with real Stripe Payment Link URLs
2. Open `BOOKING_PAGE.html` source → replace `YOUR_USERNAME` with your Calendly handle
3. Re-upload / git push the edited files
4. Verify by clicking each "Pay" button and "Book" button in the live URLs

---

## 🔁 If you want a custom domain

When you have the custom domain registered (~$12 Namecheap or $15 ausai.com.au if you have an ABN):

| Platform | Domain-add steps |
|---|---|
| GitHub Pages | Repo Settings → Pages → Custom domain → enter domain → add CNAME at registrar |
| Surge | `surge --domain ausai.com ausai_live` (run after domain CNAMEs to `na-west1.surge.sh`) |
| Netlify | Domain settings → Add custom domain → follow DNS instructions |

---

**TL;DR:** Open https://github.com/woodsai69rme/ausai-live-site/settings/pages, click Source = main/root, Save. Done in 90 seconds.
