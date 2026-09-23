# ☀️ SUNSHINE_MOONLIGHT_SETUP.md — set up cable-free dual-display via GPU-accelerated remote-desktop

> **Generated:** 2026-07-09
> **Stack:** Sunshine (open-source host on the Windows box with RTX 4060) ⇄ Moonlight (free client on phone / tablet / other laptop). RTX hardware encoding = ~30 ms latency on LAN = feels like native.
> **Author-style:** Document-only, **NOT auto-installing.** Sunshine install creates a Windows service, opens firewall ports, and exposes UDP 47984-47989 by default. Effectful system change → **install yourself** via the steps below; I will not run the installer.

---

## WHY this instead of a $130 hub

- **No cables** — phone on Wi-Fi on the kitchen counter becomes a 2nd display.
- **NVENC-friendly** — RTX 4060 hardware-encodes the stream; CPU stays idle.
- **Persistent / always-on** — once Sunshine is set up as a service, you forget it exists. Phone discovers it on the LAN automatically.
- **Latency 30-50 ms on local Wi-Fi** — fine for desktop, browser, terminals; feels laggy for fast-paced FPS gaming but you're at a workstation.

---

## STEP 0 — baseline diagnostic (run BEFORE installing)

If you skipped the auto-diag (or it errored out), copy-paste this PowerShell block into an elevated PowerShell:

```powershell
# USB + Thunderbolt enumeration (single screen of output)
Get-PnpDevice | Where-Object {
  $_.Class -match 'USB' -or $_.Class -match 'Thunderbolt'
} | Format-Table Status,FriendlyName,Class -AutoSize | Out-String -Width 4096

# NVENC hardware-presence check (should always say True on a 4060)
Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' } | Select Name,AdapterCompatibility,VideoProcessor | Format-List

# Confirm RTX 4060 has NVENC encode sessions (PowerShell one-liner)
ffmpeg -version 2>$null | Select-Object -First 1
if ($?) { "ffmpeg available — required by Sunshine under the hood" } else { "Install ffmpeg first: choco install ffmpeg" }
```

What to look for:
- **Thunderbolt** in Class column → your ports support TB (great for `STARWIND-toolkit`).
- **USB** controllers with multiple downstream hubs → laptop has USB-C 3.2 with Alt Mode (work with any tier from `HARDWARE_SHOPPING_LIST_2026.md`).
- **NVIDIA RTX 4060** in the video controller list → NVENC hardware present (Sunshine will fly).
- **ffmpeg available** → required by Sunshine's auto-stream pipeline. If missing: `choco install ffmpeg` first.

---

## STEP 1 — install Sunshine on the Windows box (host machine)

⚠️ Effectful: creates Windows service + firewall rules → run interactively.

1. Download installer: <https://github.com/LizardByte/Sunshine/releases/latest> → `Sunshine-Windows-AMD64.exe`.
2. Run the installer as Administrator (right-click → "Run as administrator").
3. When prompted, allow Windows Firewall exception (default port range 47984-47989, UDP).
4. After install, the **Sunshine web UI** opens at <https://localhost:47984>. Note: HTTPS with self-signed cert — browser will warn; click through "Advanced → proceed". Username `sunshine`, password empty by default (you'll be prompted to set one on first login).
5. Sign in. First-time prompts: set a username + password. This becomes your login when clients connect.
6. (Optional) Pair with monthly-style login: <https://localhost:47984> → set up PIN.
7. Add apps — these are shortcuts accessible from the moonlight client:
   - **Settings → Apps → Add New** → name = "Desktop", command = `cmd /C start "" "C:\Windows\System32\desk.cpl"` (opens Display Settings; useful for picking resolution).
   - **Add New** → name = "Steam Big Picture", command = `steam://open/bigpicture` (full-screen gaming).
   - **Add New** → name = "OBS", command = `obs64.exe`.

🛑 **Sunshine starts as Windows service by default. It auto-starts when Windows boots.** Confirm via `services.msc` → look for "Sunshine".

---

## STEP 2 — install Moonlight on the CLIENT device

Free, ~5 MB. Available on:

| Platform | Download |
|---|---|
| iOS / iPadOS | App Store → "Moonlight Game Streaming" |
| Android / Fire TV | Play Store → "Moonlight" |
| Windows | <https://github.com/moonlight-stream/moonlight-qt/releases/latest> |
| macOS | App Store → "Moonlight" |
| Linux | `flatpak install moonlight-qt` or `apt install moonlight` |
| Raspberry Pi | `Moonlight-Pi` GitHub releases |
| Nintendo Switch (homebrew) | `nx-moonlight` (only if your Switch is modded) |

Run Moonlight → "Add Host" → scan LAN → Sunshine host appears → pin = whatever you set in step 1 → done.

---

## STEP 3 — first connection

1. From the client, click Sunshine → enter PIN → "Pair".
2. Stream "Desktop" (the cmd-configured app from Step 1) → your screen contents appear on the client.
3. Type / mouse over / drag windows from client → they happen on the host. Latency ~30-50 ms on local Wi-Fi.
4. Resolution: the client picks a default resolution. To override on the host: Sunshine web UI → Settings → Display → manual resolution.
5. Bitrate: defaults to 20 Mbps; bumping to 50+ Mbps improves visual fidelity on Retina/4K screens.

---

## STEP 4 — common adjustments & gotchas

| Symptom | Fix |
|---|---|
| Black screen on client → click → screen appears | Sunshine restart: `services.msc` → restart "Sunshine". |
| High latency / stutter | Move client to 5 GHz Wi-Fi; or use Ethernet. |
| "Pairing failed" | PIN can be reset via Sunshine web UI → Security → Reset PIN. |
| Audio cuts out | Disable audio in Moonlight client settings temporarily; check Windows audio device. |
| Moonlight can't find Sunshine on LAN | Both must be on same subnet. Or: Sunshine web UI → find external IP → manually enter in Moonlight instead of LAN scan. |
| Sunshine uses lots of CPU even though RTX has NVENC | Driver issue — install latest NVIDIA Studio Driver (not Game Ready), Sunshine HUD shows NVENC indicator. |
| Firewall keeps prompting | Add a permanent firewall rule: `netsh advfirewall firewall add rule name="Sunshine" dir=in action=allow protocol=UDP localport=47984-47989` |

---

## STEP 5 — when to prefer a hardware hub instead

Sunshine is great for occasional / mobile use, but a $130 USB-C dock is right when:

- You want **zero Wi-Fi dependency** — wired docks don't fail on a busy Sunday afternoon.
- You're rendering & editing 4K video — the latency overhead is noticeable.
- You want to **charge the laptop + drive displays through one cable** (Sunshine / Moonlight does not charge).
- You want the client display to be **touch / pen-enabled** with proper HID — Moonlight does pass-through but with quirks.

So the matrix:
- **Sundance / Moonlight** → quick 2nd display from phone/tablet, no cables, zero dongle.
- **USB-C hub (tier 1)** → single external display + peripherals, ~$35.
- **Dual-display dock (tier 2)** → desk setup, 2 monitors + Ethernet + keyboard/mouse, no Wi-Fi dependency, ~$130.
- **TB4 dock (tier 3)** → desk studio + future-proofing, 2-3 displays + 100W PD + 2.5GbE, $300+.

These are complementary, not exclusive. Many setups run **a hardware dock at the desk + Sunshine/Moonlight on a tablet for roaming around the room**.

---

## STEP 6 — uninstall

`appwiz.cpl` → find Sunshine → Uninstall. Firewall rules clean up automatically with the installer.

Moonlight: delete the app. No service to remove.

---

*End of setup guide. Run Step 0 first, then walk through Steps 1-5 in order.*
