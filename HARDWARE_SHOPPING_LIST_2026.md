# 🛒 HARDWARE_SHOPPING_LIST_2026.md — laptop → display + peripheral tiers

> **Generated:** 2026-07-09
> **For:** Windows laptop + RTX 4060 8GB operator who wants to connect external display(s) + keyboard + mouse (and possibly Ethernet / SD / charging passthrough).
> **Style:** 3 tiers, anchored on tier 2 (dual-display hub + DisplayLink fallback) as the universal sweet spot. Cheap tier 1 for laptops; expensive tier 3 for desk-grade setups. All listings are brand-agnostic; replace retailer before ordering.

---

## 🔍 STEP 0 — run this BEFORE you buy anything

On the Windows laptop, confirm what the USB-C ports actually support.

```powershell
# 1. List USB-C / Thunderbolt controllers
Get-WmiObject Win32_PnPEntity | Where-Object { $_.Caption -match "USB|Thunderbolt" } | Select Caption,PNPDeviceID

# 2. Check Thunderbolt specifically (empty if no TB)
wmic path win32_pnpsignedentry where "caption like '%Thunderbolt%'" get caption,deviceid

# 3. Look for the DP / Thunderbolt logos physically:
#    DP-logo near port  -> Alt Mode supported (HDMI via USB-C works)
#    lightning-bolt    -> Thunderbolt 3/4 supported (full dock bandwidth)
#    neither           -> USB-C 3.2 data only (need DisplayLink adapter for video)
```

If neither logo: jump straight to **Tier 1 (DisplayLink adapter)** — Alt Mode won't work.

---

## 🟢 TIER 1 — ~$30-60 single-display USB-C hub

For: 1 external monitor + keyboard + mouse + maybe SD/USB-A. No Dual-monitor ambitions.

| Brand | Ports | Notable | ~Price | Watch-outs |
|---|---|---|---|---|
| **Anker 332 USB-C Hub (5-in-1)** | HDMI 4K@30Hz + 2× USB-A 3.0 + SD + microSD + USB-C PD 100W passthrough | Solid Anker brand, compact | $35 | HDMI 30Hz only — fine for productivity, not gaming |
| **UGREEN Revodok 105** | HDMI 4K@60Hz + 3× USB-A 3.0 + USB-C PD 100W | 60Hz refresh matters for scrolling feel | $40 | Slightly larger footprint |
| **Baseus 8-in-1** | HDMI 4K@30Hz + 3× USB-A + Gigabit Ethernet + SD + USB-C PD 100W | Includes Ethernet, great for travel | $50 | Brand cool-factor only |

**Choose if:** You have one external display + standard keyboard/mouse, and don't need 100W charging.

---

## 🟡 TIER 2 — ~$90-200 dual-display (recommended sweet spot)

For: 2 displays + full desk peripheral set. Works even without Thunderbolt.

### 2A. Pure Alt Mode (laptop has DP Alt Mode + dual USB-C / DP-MST support)

| Brand | Ports | Notable | ~Price |
|---|---|---|---|
| **Anker 563 USB-C Docking Station** | 2× HDMI (1 via Alt Mode, 1 via DisplayLink fallback) + 4× USB-A + Gigabit Ethernet + 85W PD | Mixed Alt Mode + DisplayLink; covers both laptop types | $130-160 |
| **WAVLINK WL-UG39DK1** | 2× HDMI 4K + DisplayPort + 6× USB-A + Gigabit Ethernet + 100W PD | Lots of ports, aggressive price | $90-130 |
| **Plugable UD-6950** | 2× HDMI 4K@60Hz (DisplayLink) + 4× USB-A 3.0 + Ethernet + audio | DisplayLink-native, works on ANY USB-C | $120 |

### 2B. DisplayLink-only (for laptops WITHOUT Alt Mode)

| Brand | Chip | Resolution | ~Price |
|---|---|---|---|
| **Plugable USB3-HDMI-DP** | DisplayLink DL-6950 | 4K@60Hz | $60-80 |
| **StarTech DL-4KHDMI** | DisplayLink DL-6950 | 4K@60Hz | $70-90 |

⚠️ DisplayLink needs the driver installed (~150 MB Windows driver). 5-15% CPU overhead per attached display.

**Choose if:** You have 2 monitors and want a productive workspace setup that works on any laptop.

---

## 🔴 TIER 3 — $200-450 Thunderbolt 4 dock (desk-grade)

For: Studio / multi-display desk with PD 100W + 2.5GbE + future-proofing. Requires **TB3 or TB4** USB-C port.

| Brand | Ports | Notable | ~Price |
|---|---|---|---|
| **Anker 778 NEBULA** | TB4 upstream + 2× HDMI/DP 8K + 4× USB-A + 2× USB-C + 2.5GbE + SD + 100W PD | Most popular TB4 dock in 2026 | $300 |
| **CalDigit TS4** | 18 ports, TB4, dual 6K/4K display, 98W PD, 2.5GbE | Most-extensive on market, used by studios | $380 |
| **Lenovo ThinkPad USB-C Dock Gen 2** | 11-in-1, dual 4K via TB4, 100W PD | Best bulk pricing if you shop Lenovo | $250 |
| **OWC Thunderbolt Hub** | 5-port TB4 hub downstream daisy-chain | Pure passthrough; pair with other docks | $200 |

**Choose if:** Multi-display studio/lab setup + max bandwidth + 10-year lifespan.

---

## 🔌 VIRTUAL CONNECTIONS — no cable needed

| App stack | Cost | Latency (LAN) | Best for |
|---|---|---|---|
| **Sunshine (host) + Moonlight (client)** | Free, open-source | 30-50 ms (NVENC across LAN) | Wireless-display, gaming-grade, multi-platform |
| **Parsec** | Free personal / $20+/mo team | 30-80 ms (NVENC) | VFX / editing / leisurely desktop |
| **Microsoft RDP** | Free (built-in) | 60-100 ms | Traditional remote-desktop |
| **Windows Project to this PC** (`Win+K`) | Free (built-in) | 80-150 ms | Quick-cast without install |
| **VirtualHere** | Free / paid tiers | Variable (USB-over-IP) | Tunnel USB devices (HW key, camera) over LAN |
| **Spacedesk** | Free | 30-50 ms | Wireless 2nd-display from phone/tablet |

Your RTX 4060 = NVENC hardware encode for Sunshine/Moonlight/Parsec (offloads encoding from CPU). Net result: ~30 ms perceived latency for remote desktop feels native.

**Choose if:** You want zero cable, multi-room desktop reach, or remote-in for a quieter workstation by your desk.

---

## 🔧 CABLES you'll actually need

| Type | Spec | Where to buy | ~Price |
|---|---|---|---|
| **USB-C → HDMI 6ft** | DP Alt Mode required on both ends | Belkin, Anker, JSAUX, Cable Matters | $10-15 |
| **USB-C 100W 1m / 2m** (for PD passthrough) | 5A E-marked | Anker, Baseus, UGREEN | $10-25 |
| **HDMI 2.1 6ft** (for 4K@120Hz content) | Certified Ultra High Speed | Atevon, Zeskit, Monoprice | $10-20 |
| **USB-C hub → DisplayPort cable** (for DP-out docks) | VESA-certified | StarTech, Plugable | $15-25 |

⚠️ Cheapest USB-C → HDMI cables often LACK Alt Mode support — you'll get "no signal." Spend $12+ on a known brand.

---

## ✅ DECISION TREE

```
START: how many external displays do you want, and does your laptop have TB?
│
├── 1 display ───────────────────────────────► Tier 1 (USB-C hub)
│
├── 2 displays ─┬─ laptop has TB3/TB4 ──────► Tier 3 (TB dock, e.g. Anker 778)
│              └─ laptop has USB-C only ────► Tier 2A (Anker 563 / Plugable UD-6950)
│
└── No Alt Mode on laptop ──────────────────► Tier 2B (DisplayLink adapter) OR virtual (Sunshine/Moonlight)
```

---

## 🌐 ALL METHODS — complete catalogue (everything I could find)

The 3 tiers above cover physical wired. Below is the **exhaustive** list grouped by mechanism. If you've heard of a connection method and it's not here, I missed it.

### A. Pure-direct cable (laptop has native port)

| Method | Use case | Notes |
|---|---|---|
| **HDMI cable** (laptop has full-size HDMI) | Single external display. Most laptops 2015+ have it. | Cable ~$8; cleanest for projector/TV use. Doesn't carry USB data or charge. |
| **Mini-HDMI / Micro-HDMI** | Same as HDMI but smaller devices (some laptops). | Adapters ~$5. |
| **DisplayPort (DP) cable** | Single display, often on business laptops. | Cable ~$10. Supports daisy-chain via MST. |
| **Mini-DP** (common on older MacBook Pros, Dell XPS) | Single display; convertible via passive adapter to HDMI. | Cable ~$10. MST daisy-chain supported. |
| **VGA** (legacy analog) | Old projector / old monitor. | Only on laptops from ~2014 era. Cable ~$6. |
| **DVI** (legacy, never on laptops but adapter common) | Rare. | DVI-to-HDMI adapter ~$8. |
| **MHL** (mobile high-def link) | Phone → display via USB. | Mostly obsoleted by USB-C DP Alt Mode. Adapters ~$10. |

### B. USB-C cable + cable-style adapter + cable-hub

| Method | Use case | Notes |
|---|---|---|
| **USB-C → HDMI cable (DP Alt Mode)** | 1 display, no peripherals. | Need Alt Mode on laptop **and** cable. ~$12-18 quality cable only. Cheap cables often lack Alt Mode → "no signal." |
| **USB-C → DP cable (DP Alt Mode)** | 1 display via DP. Same Alt Mode requirement. | ~$12. |
| **USB-C → Dual-HDMI splitter** | 2 HDMI outputs from 1 USB-C. | Requires DisplayLink chip in the cable; ~$45-90. Driver install. |
| **USB-C hub tier** | (See Tier 1 above.) Adds 3 USB-A + Ethernet + PD passthrough. | Same cable shape, more ports. |

### C. Thunderbolt 3/4 dock

(Requires TB3 or TB4 USB-C with ⚡ logo.) See Tier 3 above.

### D. MST (multi-stream transport) daisy-chain

- Some DisplayPort 1.2+ ports support daisy-chaining 2-3 displays from one DP out.
- 1st display → 2nd display via DP out → 3rd display. Each display reduced bandwidth.
- Common on Dell business laptops, HP EliteBook. Consumer laptops often lack.
- No MST-to-HDMI adapter at retail; must be DP-native monitors.

### E. Adapter-class (USB-A based fallback)

| Method | Use case | Notes |
|---|---|---|
| **USB-A → HDMI adapter (DisplayLink)** | Add 1 display to a laptop with **no DP Alt Mode**. | Driver install. ~$45-90. 5-15% CPU overhead. |
| **USB-A → DP adapter (DisplayLink)** | Same idea, DP output. | Same chips. |
| **USB-A → VGA adapter (no DisplayLink needed)** | Old projectors. | ~$8-15. Analog signal, lower quality. |

### F. Wireless display (low latency tolerance)

| Method | Latency | Use case |
|---|---|---|
| **Miracast / Windows Project (Win+K)** | 50-150 ms | Quick-cast without install. Built into Windows 11. |
| **AirPlay (sender)** | 80-120 ms | Apple sender (iPhone/Mac) → Windows receiver. |
| **AirPlay receiver on Windows** | 80-120 ms | Free: LonelyScreen / 5KPlayer. Commercial: AirServer. Receives AirPlay from iPhone/Mac without needing an Apple device at the receiving end. |
| **Chromecast (Google)** | 100-300 ms | Tab casting, full-screen casting. Not a primary display replacement. |
| **Intel Wireless Display (WiDi)** | 80-150 ms | Older Intel branding; mostly absorbed into Miracast. |
| **WHDI / WirelessHD transmitter** (IOGEAR GW3DHDKIT) | 30-60 ms | Wireless HDMI; 30 ft range; **$130-180** typical Amazon range. |
| **Chromium-based Cast display (Steam Link, NVIDIA Gamestream)** | 30-80 ms | Game streaming mostly; older NVIDIA SHIELD use case. |

### G. App-based remote-desktop (full OS dispatch)

| Method | Latency (LAN) | Cost | Best for |
|---|---|---|---|
| **Microsoft RDP** (built-in) | 60-100 ms | Free | Traditional remote. |
| **Apple Remote Desktop** | 80-150 ms | Free (Mac only) | macOS host. |
| **VNC (TightVNC, TigerVNC, RealVNC)** | 100-200 ms | Free | Cross-platform. |
| **NoMachine NX** | 30-60 ms (hardware-accelerated) | Free for personal | Low-latency replacement for RDP/VNC. |
| **Chrome Remote Desktop** | 100-300 ms | Free | Browser-based; no install on client. |
| **AnyDesk** | 30-80 ms (codec-optimized) | Free for personal use | Commercial-grade; current mid-tier pick. |
| **TeamViewer** | 60-150 ms | Commercial | Old stand-by. |
| **Parsec** | 30-80 ms (NVENC hardware encoding) | Free for personal | Gaming-grade; GPU-accelerated; Windows-host + Mac-client popular. |
| **Apache Guacamole** (HTML5 gateway) | varies | Free (self-host) | Browser-only client. |
| **MeshCentral** (open-source remote mgmt) | varies | Free (self-host) | Multi-host management. |
| **Apple Screen Sharing** (Messages / FaceTime) | 80-200 ms | Free | Apple-native. |

### H. Game-streaming (latency-grade for full-screen)

| Method | Latency | Notes |
|---|---|---|
| **Steam Remote Play** (software) | 30-80 ms | Built into Steam client; full-desktop mode supported since 2024. Free. |
| **NVIDIA GameStream protocol + Moonlight client** | 30-80 ms | Moonlight is an **open-source client** for NVIDIA's still-existing GameStream protocol (shipped via GeForce Experience / NVIDIA App on RTX hosts). Client = open-source; server-side remains NVIDIA embedded. |
| **NVIDIA GeForce NOW** (cloud) | 30-100 ms (cloud-side RTX) | Cloud gaming; free tier + paid tiers. |
| **NVIDIA Shield TV** (legacy hardware receiver) | 30-80 ms | Discontinued product line but existing units continue to work as GameStream receivers. |
| **Steam Link hardware** (legacy HDMI stick) | 30-80 ms | Official discontinued; community RPi clones still ship. |
| **Razer Edge / Logitech G Cloud** | varies | Handheld game-streaming devices (cloud + local sources). |
| **Boosteroid / Shadow PC cloud gaming** | 50-100 ms | Cloud VM; latency depends on datacenter. |
| **Xbox Cloud Gaming** | 50-150 ms | Console games; mostly VPN-routed. |

### I. USB / device tunneling over network

| Method | Use case | Platform |
|---|---|---|
| **USB/IP** (kernel module) | Tunnel USB devices between Linux hosts | Linux ↔ Linux. |
| **usbip-win** (community port) | USB/IP server on Windows | Windows host. |
| **VirtualHere** | USB-over-IP, commercial-grade, multi-platform | Win / Mac / Linux / Android client. |
| **FlexiHub** | Cross-platform USB sharing, commercial | Win / Mac / Linux / Android. |
| **USB Network Gate** | Commercial | Win / Mac / Linux. |
| **Microsoft "USB to Go"** (legacy) | Older Windows Server feature, mostly EOL | Windows only, deprecated. |

### J. Software-defined KVM (share 1 keyboard+mouse across machines)

| Method | Use case |
|---|---|
| **Barrier** (open-source, stable) | Software KVM; sits on top of `libsynergy`. Mature. |
| **Input Leap** (active fork of Barrier) | Drop-in successor maintained by original Barrier authors after upstream stalled mid-2020s. Currently the best open-source pick. |
| **Synergy** (commercial, original) | Original paid multi-machine KVM. |
| **Mouse Without Borders** (Microsoft Garage) | Windows-only; up to 4 PCs. Free. |
| **ShareMouse** | Windows-only; commercial. |

### K. Phone-as-display / phone-as-computer

| Method | Use case |
|---|---|
| **Samsung DeX** (Galaxy phones) | Phone → desktop UI, wired or wireless. **DeX has existed since Galaxy S8 (wired only); wireless DeX landed with Note 20 / OneUI 2.5+. Strong above Note 20.** |
| **Microsoft Phone Link** (Windows 11) | Mirror notifications + screen; phone-as-companion. |
| **Spacedesk** (free, Windows + iOS/Android) | Wireless 2nd display from phone. |
| **Samsung Flow** | Phone tethering + notification mirroring. |
| **Apple Continuity + Universal Control** | Mac ↔ iPad; not Windows. |
| **Honor / Huawei PC Mode** | Some Huawei laptops have it. |

### L. Cloud desktop (run a Windows VM elsewhere)

| Service | Cost | Use case |
|---|---|---|
| **Windows 365 Cloud PC** | ~$20-160/mo across the Frontline / Enterprise / Business Microsoft licensing tiers | "My Windows desktop lives in Azure." |
| **Amazon WorkSpaces** | ~$25-75/mo | Full Windows VM in AWS. |
| **Azure Virtual Desktop** | Pay-as-you-go | Enterprise scale. |
| **Shadow PC** | ~$30/mo | Gaming-class VM with RTX. |
| **Paperspace** | Pay-as-you-go | Various GPU tiers. |
| **Google Cloud Compute (manual setup)** | Variable | DIY cloud VM. |
| **Vultr / Linode / DigitalOcean** | $5-50/mo | VPS-grade (bring your own GUI). |

### M. Hardware-KVM-at-the-physical-layer

| Method | Use case | Cost |
|---|---|---|
| **2/4-port KVM switch box** (TrendNet TK-408K, IOGEAR GCS632U, Belkin SOHO KVM) | Box between 2-4 computers and 1 set of monitor + keyboard + mouse. Physical-button (or hotkey) toggle. Very common in offices with multi-PC desks. | $25-80 |
| **Networked KVM** (Raritan, Adder) | Server-room grade; $$$ dedicated hardware. | $500-5000 |
| **PiKVM / NanoKVM** | Raspberry-Pi-based KVM-over-IP; DIY-friendly; ATX control + video capture. | $100-300 |

---

## 🎯 MEGA-DECISION-TREE

```
START: What kind of "display + peripherals" do you want?
│
├── A. Single external display, wired, minimal setup ──► HDMI-cable or USB-C → HDMI (Tier 1 hub)
├── B. Two+ displays at desk, wired ─┬─ have TB3/TB4? ─► TB4 dock (Tier 3)
│                                  └─ USB-C only ─────► Alt Mode + DisplayLink combo (Tier 2A)
├── C. Cables impossible (mobile / changing rooms) ──► Sunshine/Moonlight, Parsec, NoMachine
├── D. Laptop drives a phone/tablet as 2nd display ───► Spacedesk, Miracast, Samsung DeX, Phone Link
├── E. Desktop lives in cloud ────────────────────────► Windows 365 Cloud PC, Shadow, WorkSpaces
├── F. Need to share 1 keyboard+mouse across N PCs ───► Input Leap (free) or Synergy (paid)
├── G. Need to remote into a server / NAS ───────────► RDP, AnyDesk, MeshCentral, Guacamole
├── H. Old projector with VGA only ──────────────────► USB-A → VGA adapter or dock with VGA-out
├── I. Wireless HDMI like a cable ───────────────────► WHDI transmitter (~$130-180)
├── J. 2-4 computers sharing 1 kbm at desk ──────────► Hardware KVM switch box (TrendNet TK-408K)
└── K. GPU-heavy game streaming with proper display ──► Steam Remote Play, NVIDIA GameStream + Moonlight client, Parsec host
```

---

## 🛠️ DECISION HEURISTICS (when picking)

| Constraint | Pick |
|---|---|
| Latency-sensitive (gaming, video editing) | Wired dock (any tier). Avoid Sunshine for high-frame-rate work. |
| Already on Wi-Fi, traveling, no dock space | Sunshine + Moonlight + your RTX 4060. |
| Need 2 displays + 100W charging through ONE port | TB4 dock (Tier 3). |
| Need to charge laptop + drive 1 display through ONE port | USB-C hub with PD ≥ 60W (Tier 1). |
| Phone as 2nd display, casual use | Spacedesk (free). |
| Run Windows in cloud, all your apps in the cloud | Windows 365 or Shadow PC. |
| Forget cables: wireless HDMI | WHDI (~30ms, 30ft, $130-180). |
| Old projector with no modern port | USB-A → VGA adapter, ~$10. |
| Sharing 1 keyboard+mouse between 2 computers | Input Leap (free / cross-platform). |
| 2-4 PCs at one desk, hotkey-toggle between them | Hardware KVM switch box (TrendNet TK-408K, $25-80). |
| Headless server in another room | MeshCentral + RDP / PiKVM. |

---

*Now exhaustive. Run Step 0 first; pick the category that fits your scenario; cross-reference the tier tables in §-§-§ above for SKU suggestions.*
