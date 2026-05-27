import React, { useRef, useCallback } from "react";
import styles from "./tilt-card.module.css";

export type TiltCardProps = {
  className?: string;
  /** Maximum tilt angle in degrees (default 6) */
  maxTilt?: number;
  /** Translate-Z lift on hover in px (default 14) */
  lift?: number;
  /** Kept for API compat — glare is now disabled by default for cleaner look */
  glare?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
};

/**
 * TiltCard — wraps any card content and applies a subtle 3D parallax tilt
 * that tracks the cursor on hover.  Falls back to a static, lifted state
 * on touch / reduced-motion devices via CSS only.
 */
const TiltCard: React.FC<TiltCardProps> = ({
  className = "",
  maxTilt = 6,
  lift = 14,
  glare: _glare = false,
  children,
  style,
}) => {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const rafRef = useRef<number | null>(null);

  const apply = useCallback(
    (rx: number, ry: number) => {
      const el = wrapRef.current;
      if (!el) return;
      el.style.setProperty("--tilt-rx", `${rx.toFixed(2)}deg`);
      el.style.setProperty("--tilt-ry", `${ry.toFixed(2)}deg`);
      el.style.setProperty("--tilt-lift", `${lift}px`);
    },
    [lift]
  );

  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = wrapRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width;
    const py = (e.clientY - r.top) / r.height;
    const dx = px * 2 - 1;
    const dy = py * 2 - 1;
    const ry = dx * maxTilt;
    const rx = -dy * maxTilt;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => apply(rx, ry));
  };

  const onLeave = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    apply(0, 0);
    // also reset lift on leave
    const el = wrapRef.current;
    if (el) el.style.setProperty("--tilt-lift", "0px");
  };

  return (
    <div
      ref={wrapRef}
      className={[styles.tilt, className].filter(Boolean).join(" ")}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={style}
    >
      <div className={styles.inner}>{children}</div>
    </div>
  );
};

export default TiltCard;
