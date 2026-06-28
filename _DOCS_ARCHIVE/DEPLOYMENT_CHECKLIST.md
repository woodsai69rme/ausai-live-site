# Deployment Checklist — Deploy Landing Page (Hostinger Backup Path)

> ⚠️ **Faster primary path exists:** See `MANUAL_DEPLOY.md` for the **90-second GitHub Pages deploy** (push `.github/workflows/pages.yml` + toggle repo **Settings → Pages → Source = GitHub Actions**). Use THIS checklist only as a **backup path** if you already own a Hostinger plan and want to skip GitHub Pages for legacy reasons.

> Step-by-step instructions to get your landing page live on ausai.tech via Hostinger (File Manager upload).

---

## Prerequisites

- Hostinger account (you already have this — ausai.tech is hosted there)
- `AUSAI_TECH_LANDING_PAGE/index.html` file ready

---

## Step 1: Log Into Hostinger

1. Go to **hpanel.hostinger.com**
2. Log in with your Hostinger credentials
3. Click on **ausai.tech** in your domains list

---

## Step 2: Access File Manager

1. In the Hostinger dashboard for ausai.tech
2. Click **File Manager** (or **Website → File Manager**)
3. Navigate to the **public_html** folder
4. This is where your website files live

---

## Step 3: Upload the Landing Page

1. In File Manager, navigate to `public_html/`
2. You should see existing files (default Hostinger placeholder)
3. **Delete** all existing files in `public_html/` (they're just the default scaffold)
4. Click **Upload** (top-right corner)
5. Select **File** → choose `index.html` from `AUSAI_TECH_LANDING_PAGE/`
6. Wait for upload to complete
7. Verify `index.html` is now in `public_html/`

---

## Step 4: Update Links in index.html

> **Scope note:** This step covers the `index.html` **landing page only**. Stripe placeholder URLs live in **`STRIPE_CHECKOUT_PREVIEW.html`** (4× `REPLACE_WITH_YOUR_LINK_*`), and the Calendly iframe handle lives in **`BOOKING_PAGE.html`** (3× `YOUR_USERNAME`). Replace those placeholders too when going live — see `EXECUTION_SCRATCHPAD.md` Step 2 + Step 3 for the checklist.

Before going live, update these placeholder links:

### Calendly Link
Find: `https://calendly.com/ausaitech`
Replace with: Your actual Calendly link (create at calendly.com if needed)

### Stripe Payment Links
Find: `#contact` (multiple instances)
Replace with: Your Stripe payment link URLs (from STRIPE_SETUP_GUIDE.md)

### Email Address
Find: `hello@ausaitech.com`
Verify: This email exists or set up forwarding

---

## Step 5: Verify SSL

1. In Hostinger dashboard, go to **Security → SSL**
2. Ensure SSL is **Active** for ausai.tech
3. If not active, click **Install SSL** (usually free with Hostinger)
4. Wait 5-10 minutes for propagation

---

## Step 6: Test the Site

1. Open browser → go to `https://ausai.tech`
2. Verify:
   - [ ] Page loads correctly
   - [ ] Navigation works (click each link)
   - [ ] Mobile menu works (resize to mobile width, click hamburger)
   - [ ] Calendly link opens correctly
   - [ ] Email link opens mail client
   - [ ] No console errors (F12 → Console)
   - [ ] SSL padlock shows (secure connection)

---

## Step 7: Test on Mobile

1. Open Chrome DevTools (F12)
2. Click device toggle (mobile icon)
3. Test on iPhone 14, iPhone SE, Samsung Galaxy S21
4. Verify:
   - [ ] Hero text is readable
   - [ ] Navigation hamburger works
   - [ ] Cards stack properly
   - [ ] Buttons are tap-friendly
   - [ ] No horizontal scroll

---

## Step 8: Submit to Google Search Console

1. Go to **search.google.com/search-console**
2. Add property: `https://ausai.tech`
3. Verify ownership (DNS or HTML file)
4. Submit sitemap (create `sitemap.xml` if needed)
5. Request indexing for homepage

---

## Step 9: Set Up Analytics (Optional)

1. Go to **analytics.google.com**
2. Create property: `ausai.tech`
3. Get tracking ID (e.g., `G-XXXXXXXXXX`)
4. Add to `index.html` in `<head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```
5. Redeploy updated `index.html`

---

## Step 10: Create Thank-You Page (Optional)

After someone pays via Stripe, redirect them to a thank-you page:

1. Create `thank-you.html` in `public_html/`
2. Content:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Thank You — AusAI Tech</title>
  <style>
    body { font-family: sans-serif; background: #0a0a0f; color: #e4e4e7; display: flex; align-items: center; justify-content: center; min-height: 100vh; text-align: center; }
    .container { max-width: 500px; padding: 40px; }
    h1 { font-size: 2rem; margin-bottom: 16px; }
    p { color: #71717a; margin-bottom: 24px; }
    a { color: #3b82f6; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>✅ Payment Received!</h1>
    <p>Thanks for choosing AusAI Tech. We'll be in touch within 24 hours to kick off your project.</p>
    <p>Questions? Email <a href="mailto:hello@ausaitech.com">hello@ausaitech.com</a></p>
    <p><a href="https://ausai.tech">← Back to home</a></p>
  </div>
</body>
</html>
```
3. Upload to `public_html/thank-you.html`
4. Update Stripe payment links to redirect to `https://ausai.tech/thank-you`

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Site shows "Index of /" | `index.html` is missing from `public_html/` — upload it |
| SSL error | Wait 10 min, or reinstall SSL in Hostinger dashboard |
| Old placeholder still showing | Clear browser cache (Ctrl+Shift+R) or test in incognito |
| Mobile menu doesn't work | Check `.nav-links.show` CSS is present (it is in our version) |
| Links don't work | Verify you updated `#contact` to actual Stripe/Calendly URLs |

---

## Time Estimate

| Step | Time |
|---|---|
| Log in + navigate | 2 min |
| Delete old files + upload | 5 min |
| Update links | 10 min |
| Test desktop | 5 min |
| Test mobile | 5 min |
| SSL verification | 2 min |
| Google Search Console | 10 min |
| **Total** | **~40 minutes** |
