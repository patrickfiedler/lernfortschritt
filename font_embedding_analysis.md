# Font Embedding Analysis

## Can We Embed These Fonts?

### SF Pro (Apple)
**License:** Proprietary - Apple End User License Agreement
**Can we embed?** ❌ **NO**
- SF Pro is Apple's proprietary font
- License prohibits redistribution
- Only usable on Apple devices where it's pre-installed
- Available for app development on Apple platforms only
- Cannot legally bundle with web apps

### Segoe UI (Microsoft)
**License:** Proprietary - Microsoft End User License Agreement
**Can we embed?** ❌ **NO**
- Segoe UI is Microsoft's proprietary font
- License prohibits redistribution
- Only usable on Windows devices where it's pre-installed
- Cannot legally bundle with web apps

### Roboto (Google)
**License:** Apache License 2.0
**Can we embed?** ✅ **YES**
- Roboto is open source
- Apache License 2.0 allows free use, modification, and distribution
- Can download from Google Fonts and self-host
- No attribution required (though appreciated)
- Commercially usable

### Comic Sans MS (Microsoft)
**License:** Proprietary - Microsoft Core Fonts for the Web (discontinued)
**Can we embed?** ⚠️ **COMPLICATED**
- Microsoft released it as part of "Core Fonts for the Web" project
- That project was discontinued in 2002
- License was ambiguous about web embedding
- Generally considered NOT embeddable for legal safety
- Only usable where pre-installed (Windows, some Mac OS versions)

## Why System Font Stack Works

The CSS font stack we're using:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Comic Sans MS', 'Comic Sans', 'Helvetica Neue', Arial, sans-serif;
```

**How it works:**
1. Browser checks if `-apple-system` exists (Apple devices) → uses SF Pro
2. If not, checks `BlinkMacSystemFont` (Chrome on Mac) → uses SF Pro
3. If not, checks `Segoe UI` (Windows) → uses Segoe UI
4. If not, checks `Roboto` (Android, Linux with Google apps)
5. If not, checks `Comic Sans MS` (Windows fallback)
6. If not, checks `Comic Sans` (older systems)
7. If not, checks `Helvetica Neue` (older macOS)
8. If not, uses `Arial` (nearly universal)
9. If not, uses browser default `sans-serif`

**Result:** Every device uses a font that's already installed. No download, no licensing issues.

## Should We Embed Roboto?

### Pros
- Legal to do so (Apache License 2.0)
- Ensures consistent rendering across all platforms
- Full control over font files

### Cons
- Adds ~500KB download on first page load (multiple font weights/styles)
- Users on Android/Chrome already have Roboto
- System fonts are faster (0 download time)
- Extra complexity

### Recommendation
**Don't embed Roboto**. Use the system font stack:
- 99% of users will have one of these fonts installed
- Faster (no download)
- Simpler (no font file management)
- Better UX (uses familiar system font)

If we DID want Roboto as guaranteed fallback, we could add it at position 4, but it's probably unnecessary.

## Why Did Comic Sans "Work Before"?

**It didn't.** The Google Fonts link for Comic Sans MS was added in commit 21da15a (UX Tier 1) and has been broken since creation:
- Comic Sans MS is NOT available on Google Fonts
- Google Fonts API returns 403 error for this request
- The browser then falls back to `font-family: 'Comic Sans MS', ...` in the CSS
- If user has Comic Sans installed (Windows users), it works via CSS fallback, not via Google Fonts
- If user doesn't have it installed, it uses the next fallback font

The Google Fonts link was always non-functional and can be safely removed.
