# Font Research Notes: Accessibility Fonts

## Source
https://pimpmytype.com/dyslexia-fonts/

## Key Findings

### Dyslexia Fonts Don't Work
- OpenDyslexic and Dyslexie fonts **perform worse** than standard fonts
- Multiple scientific studies show **no benefit** for reading speed or accuracy
- Marketing claims are not backed by research

### What Actually Helps
1. **Good spacing** between letters and lines
2. **Open letter shapes** (c, e, a should be clearly open)
3. **Clear differentiation** between similar characters (l/I, O/0)

### Recommended Fonts (from survey)
- **SF Pro** (Apple's system font)
- **BBC Reith Sans**
- **Verdana**
- **Segoe UI** (Microsoft's system font)
- **Roboto** (Google's system font)

All of these performed better than "dyslexia-friendly" fonts.

## Licensing for Self-Hosting

### Free to Self-Host (Open Source)
- **Roboto** - Apache License 2.0, freely available from Google Fonts
  - Can download and self-host
  - No restrictions

### System Fonts (Can't Self-Host, Use as Fallback)
- **SF Pro** - Apple proprietary, cannot redistribute
- **Segoe UI** - Microsoft proprietary, cannot redistribute
- **Comic Sans MS** - Microsoft proprietary, cannot redistribute

### Strategy
Use **font-family fallback stack**:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

This uses native system fonts (fast, no download) with Roboto as freely available fallback.

## Decision

**Don't use OpenDyslexic** - research shows it doesn't help and may hurt readability.

**Better approach:**
1. Improve spacing and typography in CSS
2. Use system font stack for native look and fast loading
3. Optionally: Self-host Roboto as fallback (Apache License allows this)
4. Consider: Add Comic Sans to fallback stack (many people associate it with easier reading, even if not scientifically proven)
