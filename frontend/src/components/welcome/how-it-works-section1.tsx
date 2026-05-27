import React, { useCallback, useEffect, useRef, useState } from "react";
import CardStep1 from "./card-step1";
import styles from "./how-it-works-section1.module.css";
import { useCallbackModal } from "../../context/CallbackContext";

export type HowItWorksSection1Type = {
  className?: string;
};

/**
 * «ТЕХНОЛОГІЯ ВРОЖАЮ» — sticky-блок з hard scroll-lock (як x2ycreative.com).
 *
 *  Поведінка:
 *   • Коли блок наближається до центру viewport (toleranceZone), JS примусово
 *     ставить scrollY у точку snap-center (точна фіксація блоку на екрані).
 *   • З цього моменту wheel/touch event preventDefault'-ом блокують
 *     природний scroll сторінки. Будь-який вхідний event переключає
 *     активну картку 01 → 02 → 03 → 04 (або назад).
 *   • Lock не знімається, поки користувач не «скрутить» в крайню сторону
 *     понад порог (overshoot threshold) — лише тоді сторінка йде далі.
 *   • Картки змінюються з slide-анімацією (нова знизу при scroll-down,
 *     зверху при scroll-up).
 *   • Точки-індикатор клікабельні — стрибок на конкретний крок.
 */

const N_CARDS = 4;
const SLIDE_FROM_DESIGN_PX = 760;
const WHEEL_THRESHOLD = 40;        // px deltaY для одного snap
const SNAP_LOCK_MS = 550;          // мінімальна пауза між переключеннями
const TRANSITION_MS = 600;
const ENTRY_TOLERANCE_PX = 220;    // зона входу в lock (центр блоку vs центр vp)
const EXIT_OVERSHOOT_PX = 220;     // накопичений «overshoot» для exit lock
const EXIT_COOLDOWN_MS = 1500;     // після exit — пауза перед повторним enter

const HowItWorksSection1: React.FC<HowItWorksSection1Type> = ({
  className = "",
}) => {
  const { openModal: openCallback } = useCallbackModal();
  const sectionRef = useRef<HTMLElement | null>(null);
  const cardsRef = useRef<HTMLDivElement | null>(null);

  const [activeIdx, setActiveIdx] = useState<number>(0);
  const [locked, setLocked] = useState<boolean>(false);

  const activeIdxRef = useRef(0);
  const lockedRef = useRef(false);
  const lockedTargetScrollRef = useRef(0);
  const accumRef = useRef(0);
  const overshootRef = useRef(0);
  const lockUntilRef = useRef(0);
  const exitUntilRef = useRef(0); // cooldown після exit lock
  const lastScrollYRef = useRef(0);
  const lastScrollDirRef = useRef<"down" | "up">("down");

  useEffect(() => {
    activeIdxRef.current = activeIdx;
  }, [activeIdx]);
  useEffect(() => {
    lockedRef.current = locked;
  }, [locked]);

  /* ---- Анімація карток ---- */
  useEffect(() => {
    const holder = cardsRef.current;
    if (!holder) return;
    /* Mobile: render every card visible inline (no transform / opacity
       manipulation) — they stack via CSS instead. */
    const isMobile =
      typeof window !== "undefined" && window.innerWidth < 768;
    const cards = holder.querySelectorAll<HTMLElement>("[data-card-idx]");
    if (isMobile) {
      cards.forEach((el) => {
        el.style.transform = "";
        el.style.opacity = "1";
        el.style.zIndex = "1";
        el.style.pointerEvents = "auto";
        el.style.position = "relative";
      });
      return;
    }
    cards.forEach((el, i) => {
      if (i === activeIdx) {
        el.style.transform = "translate3d(0, 0, 0)";
        el.style.opacity = "1";
        el.style.zIndex = "50";
        el.style.pointerEvents = "auto";
      } else if (i > activeIdx) {
        el.style.transform = `translate3d(0, ${SLIDE_FROM_DESIGN_PX}px, 0)`;
        el.style.opacity = "0";
        el.style.zIndex = String(10 + i);
        el.style.pointerEvents = "none";
      } else {
        el.style.transform = `translate3d(0, -${SLIDE_FROM_DESIGN_PX}px, 0)`;
        el.style.opacity = "0";
        el.style.zIndex = String(10 + i);
        el.style.pointerEvents = "none";
      }
    });
  }, [activeIdx]);

  /* ---- Вирахування цільового scrollY для snap-центру ---- */
  const computeSnapTarget = useCallback((): number => {
    const sec = sectionRef.current;
    if (!sec) return window.scrollY;
    const r = sec.getBoundingClientRect();
    const sectionDocTop = r.top + window.scrollY;
    const vh = window.innerHeight;
    /* Центр секції повинен співпасти з центром viewport. */
    return sectionDocTop + r.height / 2 - vh / 2;
  }, []);

  /* ---- Enter lock ---- */
  const enterLock = useCallback(
    (initialIdx: number) => {
      if (lockedRef.current) return;
      const target = computeSnapTarget();
      lockedTargetScrollRef.current = target;
      /* Жорстко snap scroll до центру блоку. */
      window.scrollTo({ top: target, behavior: "auto" });
      accumRef.current = 0;
      overshootRef.current = 0;
      lockUntilRef.current = Date.now() + 200; // короткий settle
      setActiveIdx(initialIdx);
      setLocked(true);
    },
    [computeSnapTarget]
  );

  /* ---- Exit lock ---- */
  const exitLock = useCallback((dir: "down" | "up") => {
    if (!lockedRef.current) return;
    setLocked(false);
    accumRef.current = 0;
    overshootRef.current = 0;
    exitUntilRef.current = Date.now() + EXIT_COOLDOWN_MS;
    /* Зразу зсуваємо scroll трохи в напрямку виходу, щоб блок почав
       зникати, а не одразу втягнувся знову. */
    const sec = sectionRef.current;
    if (sec) {
      const r = sec.getBoundingClientRect();
      const vh = window.innerHeight;
      const shift = dir === "down" ? r.height / 2 + vh / 2 + 1 : -(r.height / 2 + vh / 2 + 1);
      window.scrollBy({ top: shift, behavior: "auto" });
    }
  }, []);

  /* ---- Spectacle: scroll handler перевіряє чи треба зайти в lock ---- */
  useEffect(() => {
    /* Mobile: disable scroll-jacking entirely so the page scrolls
       naturally. Cards still display via simple vertical layout
       (driven by CSS @media max-width:768px in the module file). */
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      return;
    }
    lastScrollYRef.current = window.scrollY;

    const onScroll = () => {
      const cur = window.scrollY;
      const prev = lastScrollYRef.current;
      const dir: "down" | "up" = cur > prev ? "down" : "up";
      lastScrollYRef.current = cur;
      lastScrollDirRef.current = dir;

      if (lockedRef.current) {
        /* Тримаємо scrollY на snap-таргеті жорстко. */
        if (Math.abs(cur - lockedTargetScrollRef.current) > 1) {
          window.scrollTo({ top: lockedTargetScrollRef.current, behavior: "auto" });
        }
        return;
      }

      const sec = sectionRef.current;
      if (!sec) return;
      const r = sec.getBoundingClientRect();
      const vh = window.innerHeight;
      const blockCenter = r.top + r.height / 2;
      const vhCenter = vh / 2;
      const delta = Math.abs(blockCenter - vhCenter);

      if (delta < ENTRY_TOLERANCE_PX) {
        /* Не входити повторно в lock протягом EXIT_COOLDOWN_MS після exit. */
        if (Date.now() < exitUntilRef.current) return;
        /* Зайти в lock з відповідною першою карткою. */
        const initial = dir === "down" ? 0 : N_CARDS - 1;
        enterLock(initial);
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [enterLock]);

  /* ---- Wheel / Touch / Key, активні ТІЛЬКИ в lock ---- */
  useEffect(() => {
    /* Mobile: skip wheel/touch hijacking so users can scroll naturally. */
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      return;
    }
    const trySnap = (dir: 1 | -1): boolean => {
      const cur = activeIdxRef.current;
      const now = Date.now();
      if (now < lockUntilRef.current) return false;
      if (dir > 0 && cur < N_CARDS - 1) {
        setActiveIdx(cur + 1);
        accumRef.current = 0;
        overshootRef.current = 0;
        lockUntilRef.current = now + SNAP_LOCK_MS;
        return true;
      }
      if (dir < 0 && cur > 0) {
        setActiveIdx(cur - 1);
        accumRef.current = 0;
        overshootRef.current = 0;
        lockUntilRef.current = now + SNAP_LOCK_MS;
        return true;
      }
      return false;
    };

    const onWheel = (e: WheelEvent) => {
      if (!lockedRef.current) return;
      /* В режимі lock — завжди preventDefault (жорстка фіксація). */
      e.preventDefault();

      const cur = activeIdxRef.current;
      const dy = e.deltaY;
      const now = Date.now();
      if (now < lockUntilRef.current) {
        /* У дебоунсі — нічого. */
        return;
      }

      if (dy > 0) {
        if (cur < N_CARDS - 1) {
          accumRef.current += dy;
          if (accumRef.current >= WHEEL_THRESHOLD) trySnap(1);
        } else {
          /* На крайньому положенні «вниз». Накопичуємо overshoot. */
          overshootRef.current += dy;
          if (overshootRef.current >= EXIT_OVERSHOOT_PX) {
            exitLock("down");
          }
        }
      } else if (dy < 0) {
        if (cur > 0) {
          accumRef.current += dy;
          if (accumRef.current <= -WHEEL_THRESHOLD) trySnap(-1);
        } else {
          overshootRef.current += dy;
          if (overshootRef.current <= -EXIT_OVERSHOOT_PX) {
            exitLock("up");
          }
        }
      }
    };

    /* Touch ---- */
    let touchStartY = 0;
    const onTouchStart = (e: TouchEvent) => {
      if (!lockedRef.current) return;
      touchStartY = e.touches[0].clientY;
    };
    const onTouchMove = (e: TouchEvent) => {
      if (!lockedRef.current) return;
      e.preventDefault();
      const dy = touchStartY - e.touches[0].clientY;
      const cur = activeIdxRef.current;
      const now = Date.now();
      if (now < lockUntilRef.current) return;

      if (dy > 0) {
        if (cur < N_CARDS - 1) {
          if (dy >= 60) {
            trySnap(1);
            touchStartY = e.touches[0].clientY;
          }
        } else {
          overshootRef.current += Math.max(0, dy);
          if (overshootRef.current >= EXIT_OVERSHOOT_PX) exitLock("down");
        }
      } else if (dy < 0) {
        if (cur > 0) {
          if (dy <= -60) {
            trySnap(-1);
            touchStartY = e.touches[0].clientY;
          }
        } else {
          overshootRef.current += Math.min(0, dy);
          if (overshootRef.current <= -EXIT_OVERSHOOT_PX) exitLock("up");
        }
      }
    };

    /* Keyboard ---- */
    const onKey = (e: KeyboardEvent) => {
      if (!lockedRef.current) return;
      if (
        e.key === "ArrowDown" ||
        e.key === "PageDown" ||
        e.key === " " ||
        e.key === "Spacebar"
      ) {
        e.preventDefault();
        if (activeIdxRef.current < N_CARDS - 1) trySnap(1);
        else exitLock("down");
      } else if (e.key === "ArrowUp" || e.key === "PageUp") {
        e.preventDefault();
        if (activeIdxRef.current > 0) trySnap(-1);
        else exitLock("up");
      }
    };

    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("touchstart", onTouchStart);
      window.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("keydown", onKey);
    };
  }, [exitLock]);

  /* ---- Кліки по точках-індикатору переключають картку ---- */
  const onDotClick = useCallback((i: number) => {
    accumRef.current = 0;
    overshootRef.current = 0;
    lockUntilRef.current = Date.now() + SNAP_LOCK_MS;
    setActiveIdx(i);
  }, []);

  const cardStyleVars = {
    ["--card-transition-ms"]: `${TRANSITION_MS}ms`,
  } as React.CSSProperties;

  return (
    <section
      ref={sectionRef}
      className={[styles.howItWorksSection, className].join(" ")}
      data-testid="how-it-works-section"
      data-locked={locked ? "true" : undefined}
    >
      <div className={styles.stickyInner}>
        {/* Decorative organic background layers (replaces the cropped leaf):
            soft bokeh orbs + topographic veins + subtle dot grid.
            Anim/text/CTA untouched. */}
        <div className={styles.bgDecor} aria-hidden="true">
          <span className={[styles.orb, styles.orbA].join(" ")} />
          <span className={[styles.orb, styles.orbB].join(" ")} />
          <span className={[styles.orb, styles.orbC].join(" ")} />
          <svg
            className={styles.veins}
            viewBox="0 0 1920 715"
            preserveAspectRatio="xMidYMid slice"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="veinFade" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#b3d217" stopOpacity="0.0" />
                <stop offset="40%" stopColor="#b3d217" stopOpacity="0.18" />
                <stop offset="100%" stopColor="#b3d217" stopOpacity="0.0" />
              </linearGradient>
              <pattern id="dotGrid" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="1" fill="#b3d217" fillOpacity="0.10" />
              </pattern>
            </defs>

            {/* Subtle dot grid covering the whole sticky area */}
            <rect x="0" y="0" width="1920" height="715" fill="url(#dotGrid)" />

            {/* Organic curved veins reminiscent of plant nervures / roots */}
            <g stroke="url(#veinFade)" strokeWidth="1.2" fill="none">
              <path d="M-50 120 C 320 60, 720 220, 1100 180 S 1980 340, 2050 280" />
              <path d="M-50 280 C 280 240, 640 380, 1040 360 S 1860 520, 2050 470" />
              <path d="M-50 440 C 340 400, 700 540, 1100 520 S 1920 660, 2050 620" />
              <path d="M-50 600 C 360 560, 720 700, 1120 680 S 1980 800, 2050 780" />
            </g>

            {/* A few sparse spores / leaf-tips highlights */}
            <g fill="#b3d217" fillOpacity="0.16">
              <circle cx="180" cy="180" r="2.5" />
              <circle cx="1480" cy="120" r="3" />
              <circle cx="1780" cy="380" r="2" />
              <circle cx="320" cy="540" r="2.5" />
              <circle cx="900" cy="640" r="2" />
              <circle cx="1180" cy="520" r="3" />
            </g>
          </svg>
        </div>

        <div className={styles.leftColumn}>
          <h2 className={styles.title}>
            <span className={styles.titleBold}>технологія</span>
            <span>{` `}</span>
            <span className={styles.titleRegular}>врожаю</span>
          </h2>
          <h3 className={styles.subtitle}>
            Від старту насіння до захисту у коморі.
            <br />
            Оберіть технологію, що працює на ваш прибуток.
          </h3>
          <button
            type="button"
            className={styles.ctaButton}
            data-testid="how-it-works-cta"
            onClick={openCallback}
          >
            <span className={styles.ctaIcon} aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.37 1.9.72 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.35 1.85.59 2.81.72A2 2 0 0122 16.92z"
                  stroke="#FFFFFF"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <span className={styles.ctaLabel}>Замовити дзвінок</span>
          </button>
        </div>

        {/* Step indicator: 4 КЛІКАБЕЛЬНІ точки. */}
        <div
          className={styles.stepIndicator}
          role="tablist"
          aria-label="Кроки технології"
        >
          {Array.from({ length: N_CARDS }).map((_, i) => (
            <button
              key={i}
              type="button"
              role="tab"
              aria-selected={i === activeIdx}
              aria-label={`Перейти до кроку ${i + 1}`}
              onClick={() => onDotClick(i)}
              className={styles.stepDot}
              data-active={i === activeIdx ? "true" : undefined}
            />
          ))}
        </div>

        <div
          ref={cardsRef}
          className={styles.cardsHolder}
          style={cardStyleVars}
        >
          <div data-card-idx={0} className={styles.cardSlot}>
            <CardStep1
              stepNumber="01"
              title="Внесення"
              description="Живі мікроорганізми потрапляють на насіння, лист або у ґрунт. Завдяки правильному зберіганню вони перебувають у стані максимальної активності та готові до роботи."
            />
          </div>
          <div data-card-idx={1} className={styles.cardSlot}>
            <CardStep1
              stepNumber="02"
              title="Активація"
              description="У природному середовищі бактерії «прокидаються», миттєво розмножуються та вступають із рослинами у взаємодію, стимулюючи їх природний імунітет."
            />
          </div>
          <div data-card-idx={2} className={styles.cardSlot}>
            <CardStep1
              stepNumber="03"
              title="Захист"
              description="Корисна мікрофлора витісняє хвороби та знищує шкідників без «хімічного стресу» для культури. Рослина розвивається природно і без затримок у рості."
            />
          </div>
          <div data-card-idx={3} className={styles.cardSlot}>
            <CardStep1
              stepNumber="04"
              title="Результат"
              description="Ви отримуєте максимальний врожай без залишків пестицидів. Ґрунт з кожним роком відтворюється, а продукція стає безпечною, якісною та придатною для тривалого зберігання."
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection1;
