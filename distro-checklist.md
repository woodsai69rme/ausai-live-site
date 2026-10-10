# Distribution Checklist — tellemthatsme → Spotify / Apple / YouTube Music
> All ISRC / copyright / release_date fields in your catalog are currently **empty**. Fill these before uploading to any distributor (DistroKid, CD Baby, Amuse, or Tunecore). Spotify will not pay streams without a valid ISRC.

## 1. Decide your distributor
| Distributor | Cost | Keeps 100%? | Notes |
|---|---|---|---|
| **DistroKid** | ~US$23/yr, unlimited | Keeps ~100% | Fastest, industry default for volume |
| **Amuse** | Free tier available | Keeps 100% (free) | Good starting point |
| **CD Baby** | Per-release | Keeps ~91% | Slower |
| **TuneCore** | Per-release/yr | Keeps 100% | Good reporting |

## 2. Per-song metadata you MUST fill (currently all empty)
For each of the 220 tracks before distro:
- [ ] **ISRC** — distributor usually generates these; you don't need to make them yourself
- [ ] **Title** — final release name (decide: keep or rename weak titles first — see note below)
- [ ] **Artist** — `tellemthatsme` (exact, consistent everywhere)
- [ ] **Featuring** — if any
- [ ] **Album** — one of: Street Royalty, Night Drives, Rotary Tapes, Two Faces One Truth (or a new "Best Of")
- [ ] **Track number + disc number**
- [ ] **Genre** — map: drill→Hip-Hop/Rap, phonk→Hip-Hop/Rap, trap→Hip-Hop/Rap, rnb→R&B/Soul, hip-hop→Hip-Hop/Rap
- [ ] **Composer / Lyricist / Producer** — your legal name + PRO (APRA AMCOS for AU)
- [ ] **Copyright year + holder** — e.g. `© 2026 tellemthatsme`
- [ ] **Explicit flag** — Yes if any profanity (most phonk/drill → mark explicit)
- [ ] **Language** — English (or as per track)
- [ ] **Release date** — schedule one album at a time (see plan below)
- [ ] **Master owner** — you (keep masters non-destructive per blueprint)
- [ ] **Publisher** — self

## 3. Artwork (required by every DSP)
- [ ] **3000×3000px JPG/PNG**, square, RGB
- [ ] Under 10 MB, no logos of DSPs, no URLs, no blurry/illegible text
- [ ] One cover per single; one per album (album cover reused on tracks)
- [ ] You have 220 tracks — you need at least **4 album covers** + any standalone singles

## 4. ⚠️ AI-disclosure (critical for 2026)
- AI-generated music is **allowed** on Spotify/Apple **only if disclosed**.
- Spotify flags undisclosed AI content and can remove it.
- In your distributor's metadata, tick the **"contains AI-generated content"** disclosure.
- Keep the same AI-music label you use on YouTube — consistency protects the channels.

## 5. Release order (match your YouTube plan, don't dump all 220 at once)
- **Phase 1:** 4 album EPs/singles first (Street Royalty, Night Drives, Rotary Tapes, Two Faces One Truth)
- **Phase 2:** rollout deep cuts weekly
- **Phase 3:** compile a "Best Of" once tracks have stream data

## 6. Royalty setup
- [ ] Link a bank account + tax info (AU: ABN/tax file number) in your distributor
- [ ] Register with **APRA AMCOS** (Australian PRO) so you collect performance royalties
- [ ] Claim your **YouTube Content ID** via distributor (they route your YouTube sound recordings)

## 7. Pre-flight before you submit
- [ ] Masters are final (loudness ~ -14 LUFS for streaming)
- [ ] No third-party samples you don't own (AI-only = clean, your advantage)
- [ ] Metadata matches YouTube titles exactly (title, artist) so platforms cross-link

---
**Before distro, decide the title question you raised:** if you're renaming weak titles, do it in `catalog-data.json` + the release schedule first, THEN export to the distributor — so every platform matches.