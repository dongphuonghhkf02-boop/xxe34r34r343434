import React, { useEffect, useState, useCallback } from "react";
import ReactDOM from "react-dom";
import { Link, useNavigate } from "react-router-dom";
import Search1 from "./search1";
import { useCallbackModal } from "../../context/CallbackContext";
import styles from "./mobile-menu.module.css";

/* =================================================================
   MobileMenu — full-screen drawer for mobile header burger.
   ----------------------------------------------------------------
   Per the design (see Меню.png):
     • Top row: TAMIS logo (left), User+Cart icons + close X (right)
       — handled by the parent <Navbar1>, this component renders the
       drawer BODY beneath the navbar.
     • Search field (rounded, full width, "Пошук...")
     • Vertical nav: Каталог · Культури · Про нас · Контакти
       with 1px dividers between each.
     • Bottom: phones + email
     • Bottom CTA: "Замовити дзвінок →" (full-width brand-green).
   ================================================================= */

type Props = {
  open: boolean;
  onClose: () => void;
};

const NAV_ITEMS: Array<{ label: string; to: string; testId: string }> = [
  { label: "Каталог", to: "/catalog", testId: "mobile-menu-catalog" },
  { label: "Культури", to: "/cultures", testId: "mobile-menu-cultures" },
  { label: "Про нас", to: "/about", testId: "mobile-menu-about" },
  { label: "Контакти", to: "/contacts", testId: "mobile-menu-contacts" },
];

const MobileMenu: React.FC<Props> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const { openModal: openCallback } = useCallbackModal();
  const [query, setQuery] = useState("");

  // Lock body scroll when open.
  useEffect(() => {
    if (!open) return;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = original;
    };
  }, [open]);

  // ESC closes.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const handleSearchSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const q = query.trim();
      navigate(`/catalog${q ? `?q=${encodeURIComponent(q)}` : ""}`);
      onClose();
      setQuery("");
    },
    [query, navigate, onClose],
  );

  const handleCallback = useCallback(() => {
    onClose();
    // tiny delay so close animation/state lands before modal opens
    setTimeout(() => openCallback(), 80);
  }, [onClose, openCallback]);

  return (
    <Portal>
      <div
        className={styles.drawer}
        data-open={open ? "true" : "false"}
        aria-hidden={!open}
        data-testid="mobile-menu-drawer"
      >
        <div className={styles.inner}>
          {/* Search */}
          <form className={styles.searchWrap} onSubmit={handleSearchSubmit} role="search">
            <span className={styles.searchIcon} aria-hidden="true">
              <Search1 size={20} />
            </span>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Пошук…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              data-testid="mobile-menu-search-input"
              aria-label="Пошук по сайту"
            />
          </form>

          {/* Vertical nav */}
          <nav className={styles.nav} aria-label="Основне меню">
            {NAV_ITEMS.map((it) => (
              <Link
                key={it.to}
                to={it.to}
                className={styles.navItem}
                onClick={onClose}
                data-testid={it.testId}
              >
                {it.label}
              </Link>
            ))}
          </nav>

          {/* Contacts block */}
          <div className={styles.contacts}>
            <a href="tel:+380509375657" className={styles.contactLine}>
              050 937 56 57
            </a>
            <a href="tel:+380675101307" className={styles.contactLine}>
              067 510 13 07
            </a>
            <a href="mailto:tamisagro@gmail.com" className={styles.contactLine}>
              tamisagro@gmail.com
            </a>
          </div>

          {/* CTA */}
          <button
            type="button"
            className={styles.cta}
            onClick={handleCallback}
            data-testid="mobile-menu-cta-callback"
          >
            <span>Замовити дзвінок</span>
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M4 10H16M16 10L10 4M16 10L10 16"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </Portal>
  );
};

/* ─── Portal helper: render drawer into <body> so it isn't trapped by
   any ancestor's `backdrop-filter` (which would create a containing
   block for `position: fixed`, breaking full-screen layout). */
const Portal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  if (!mounted || typeof document === "undefined") return null;
  return ReactDOM.createPortal(children, document.body);
};

export default MobileMenu;
