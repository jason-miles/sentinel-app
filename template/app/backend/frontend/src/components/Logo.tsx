// Capitec mark recreated as a crisp inline SVG (razor-sharp at any size): the
// deep-blue rounded tile carrying a stylised red "C" arc, paired with the
// Sentinel lockup. Used for a spectacular hero on the landing page and a
// compact mark in the top bar.

export function CapitecMark({ size = 40, tile = "#003b5c", arc = "#e2001a" }:
  { size?: number; tile?: string; arc?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" fill="none" aria-hidden>
      {/* Deep-blue rounded tile */}
      <rect x="4" y="4" width="92" height="92" rx="18" fill={tile} />
      {/* Signature red "C" arc — open on the right */}
      <path
        d="M72 32 A28 28 0 1 0 72 68"
        stroke={arc}
        strokeWidth="11"
        strokeLinecap="round"
        fill="none"
      />
      {/* Inner blue dot at the arc mouth for a crosshair/aperture feel */}
      <circle cx="50" cy="50" r="7" fill={arc} />
    </svg>
  );
}

// Large hero lockup for the landing page.
export function HeroLogo() {
  return (
    <div className="hero-logo">
      <div className="hero-glow" />
      <div className="hero-inner">
        <CapitecMark size={48} tile="#ffffff" arc="#e2001a" />
        <div className="hero-wordmark">
          <span className="hero-capitec">Capitec</span>
          <span className="hero-divider" />
          <span className="hero-sentinel">Sentinel</span>
        </div>
      </div>
      <div className="hero-tag">CDP &amp; Financial Crime Intelligence Platform</div>
    </div>
  );
}

// Compact mark for the top bar.
export function BrandMark() {
  return (
    <div className="brandmark">
      <CapitecMark size={26} tile="#003b5c" arc="#e2001a" />
      <span className="brandmark-text"><b>Capitec</b> Sentinel</span>
    </div>
  );
}
