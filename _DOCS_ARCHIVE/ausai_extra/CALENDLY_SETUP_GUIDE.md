# Calendly Setup Guide — AusAI Tech

> Step-by-step guide to create a booking page for discovery calls.

---

## Step 1: Create Calendly Account

1. Go to **calendly.com**
2. Click "Get Started for Free"
3. Sign up with your email (hello@ausaitech.com if set up, or personal email)
4. Connect your Google Calendar (for availability sync)
5. Set timezone to **AEST (Australian Eastern Standard Time)**

---

## Step 2: Create Event Type — "Free Discovery Call"

1. Click **"+ Create New"** → **"One-on-One"**
2. Fill in:
   - **Event name:** "Free AI Discovery Call"
   - **Duration:** 15 minutes
   - **Location:** Zoom (auto-generates link) or Google Meet
   - **Description:**
   ```
   Free 15-minute discovery call to discuss your AI needs.

   What we'll cover:
   • Your current pain points
   • What AI can realistically solve
   • A rough estimate of scope and cost
   • Next steps (if we're a good fit)

   No sales pitch — just honest advice.
   ```

---

## Step 3: Set Availability

1. Go to **Availability** tab
2. Set weekly hours:
   - Monday–Friday: 9:00 AM – 5:00 PM AEST
   - Saturday: By appointment
   - Sunday: Closed
3. Set buffer time: 15 minutes before/after each meeting
4. Set minimum notice: 24 hours (don't accept same-day bookings)
5. Set date range: Available starting from tomorrow (no same-day)

---

## Step 4: Customize Booking Page

1. Go to **Branding** tab
2. Upload logo: Use your AusAI Tech logo (or a simple "AusAI" text logo)
3. Set brand color: **#3b82f6** (matches your landing page)
4. Set thank-you page redirect: `https://ausai.tech/thank-you`

---

## Step 5: Get Your Calendly Link

1. Go to **"My Link"** in top-right
2. Your link will be: `calendly.com/ausaitech` (or similar)
3. Copy this link

---

## Step 6: Update Landing Page

1. Open `AUSAI_TECH_LANDING_PAGE/index.html`
2. Find: `https://calendly.com/ausaitech`
3. Replace with your actual Calendly link
4. Redeploy to Hostinger

---

## Step 7: Test Booking Flow

1. Open your Calendly link in incognito window
2. Select a date/time
3. Fill in test details
4. Confirm booking
5. Verify you receive email confirmation
6. Verify event appears in your Google Calendar

---

## Step 8: Add Calendly to LinkedIn

1. Go to LinkedIn profile → "Contact info"
2. Add your Calendly link under "Website"
3. In your LinkedIn DM follow-ups, include: "Pick a time: [your Calendly link]"

---

## Calendly Free Tier Limits

| Feature | Free Tier |
|---|---|
| Event types | 1 |
| Calendars connected | 1 |
| Group events | ❌ |
| SMS notifications | ❌ |
| Custom branding | ❌ |
| Payment collection | ❌ |

**Upgrade to Standard ($12/mo) when you're getting 5+ bookings/week.**

---

## Alternative: If Calendly Doesn't Work

If you can't use Calendly, alternatives:
- **TidyCal** ($29 one-time) — lifetime deal, no monthly fees
- **Cal.com** (free tier) — open source, self-hostable
- **SimplyBook.me** (free tier) — good for service businesses
- **Manual scheduling** — just put "Available Tuesday/Thursday 3-5pm AEST" in your DMs

---

## Time to Set Up

| Step | Time |
|---|---|
| Create account | 5 min |
| Create event type | 5 min |
| Set availability | 5 min |
| Customize branding | 5 min |
| Get link + test | 5 min |
| Update landing page | 5 min |
| **Total** | **~30 minutes** |
