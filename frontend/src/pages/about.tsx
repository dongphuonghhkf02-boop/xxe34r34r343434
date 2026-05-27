import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import Seo from "../components/Seo";
import Navbar1 from "../components/figma/navbar1";
import Footer1 from "../components/figma/footer1";
import CtaSection1 from "../components/figma/cta-section1";
import LogisticsSection from "../components/figma/logistics-section";
import TrustSection from "../components/welcome/frame-component10";
import AnimatedNumber from "../components/about/animated-number";
import RevealHeading from "../components/welcome/reveal-heading";
import cardStyles from "../components/welcome/number-card1.module.css";
import styles from "./about.module.css";

/* =====================================================================
   /about — "Про нас" page for TAMIS АГРО.
   Implements the full Figma design (1920 design width).
   Header (Navbar1) and Footer (Footer1) are not modified.
   Sections (top → bottom):
     1. Hero (agrovideo background + headline)
     2. Numbers (+350 тис / 100% / +5000)
     3. Mission (green block with quote & founder)
     4. "Від лабораторії до вашого поля" — 4 cards 01-04
     5. "Логістика живих рішень" — dark teal w/ plant photo
     6. "+20 років" history timeline (2000-2025)
     7. "Нам довіряють" — partners' logos
     8. "Не знайшли ваш препарат?" (reused CtaSection1)
   ===================================================================== */

/* --------------------------------------------------------------------
   NUMBERS — step-based per-digit slot-machine counter.
   Логіка повністю перенесена 1:1 з Welcome (frame-component8.tsx),
   щоб одна імплементація працювала всюди.
   "350 ТИС +" та "5000 +" — покрокова анімація з cascade middle 4→5
   на останньому кроці. "100 %" — статичне.
   Цифри: масив "reels" — кожен reel це послідовність кадрів (length=1
   для статичних). Анімація прокручується одночасно для всіх трьох
   карток (синхронізовано один phase-machine).
-------------------------------------------------------------------- */

type DigitSequence = string[];

type NumberCard = {
  key: string;
  digits: DigitSequence[];
  label?: string;
  showPlus: boolean;
  desc: string;
  accent: boolean;
};

const NUMBERS: NumberCard[] = [
  {
    key: "ha",
    digits: [
      ["3"],
      ["4", "4", "4", "5"],
      ["7", "8", "9", "0"],
    ],
    label: "ТИС",
    showPlus: true,
    desc: "гектарів оброблених полів по всій Україні",
    accent: true,
  },
  {
    key: "soil",
    digits: [["1"], ["0"], ["0"]],
    label: "%",
    showPlus: false,
    desc: "покращення стану ґрунту після застосування",
    accent: false,
  },
  {
    key: "farmers",
    digits: [
      ["4", "4", "4", "5"],
      ["9", "9", "9", "0"],
      ["9", "9", "9", "0"],
      ["7", "8", "9", "0"],
    ],
    showPlus: true,
    desc: "задоволених фермерів, які обрали нашу продукцію",
    accent: false,
  },
];

/* Timing — ідентично Welcome (frame-component8.tsx). */
const RESET_MS = 60;        // snap-reset (no transition)
const INITIAL_HOLD = 600;   // hold першого кадру перед першим роллом
const ROLL_MS = 320;        // smooth roll between two adjacent frames
const HOLD_BETWEEN = 450;   // hold після кожного проміжного кроку
const FINAL_HOLD = 1900;    // hold фінального значення перед reset

const LAB_CARDS = [
  {
    num: "01",
    title: "Розробка",
    desc:
      "Кожен препарат починається з дослідження.\nНаша лабораторія тестує штами бактерій та підбирає оптимальну концентрацію під реальні польові умови.",
    img: "/lab-research.webp",
  },
  {
    num: "02",
    title: "Виробництво",
    desc:
      "Живі організми вирощуються в контрольованому середовищі. Кожна партія проходить 3 етапи перевірки якості перед тим, як потрапити на склад.",
    img: "/lab-production.webp",
  },
  {
    num: "03",
    title: "Зберігання +5…+10 °C",
    desc:
      "Біопрепарати — живі. Ми контролюємо температуру на кожному етапі: від виробництва до вашого складу. Це те, що конкуренти не роблять.",
    img: "/lab-storage.webp",
  },
  {
    num: "04",
    title: "Доставка",
    desc:
      "Термологістика до вашого поля.\nПрепарат приїжджає живим — і працює на повну з першої обробки.",
    img: "/Frame-1200@2x.webp",
  },
];

const TIMELINE_PERIODS = [
  {
    id: "2000",
    label: "Ідея",
    title: "Ідея",
    desc:
      "Народження концепції. Перші лабораторні дослідження штамів корисних бактерій та грибів — закладаємо фундамент майбутніх біопрепаратів задовго до офіційного запуску компанії.",
    img: "/history-lab.webp",
    icon: "/year-icon-2000.webp",
  },
  {
    id: "2005",
    label: "2005",
    title: "Заснування компанії",
    desc:
      "Офіційне заснування ТАМІС АГРО. Комерціалізуємо багаторічні розробки — запускаємо лінійку біоінокулянтів для зернових та бобових. Перші фермери довіряють нашій технології.",
    img: "/history-lab.webp",
    icon: "/year-icon-2005.webp",
  },
  {
    id: "2010",
    label: "2010",
    title: "Масштабування виробництва",
    desc:
      "Власне виробництво з холодильними камерами. Контрольована термологістика на кожному етапі — від штаму до поля клієнта.",
    img: "/lab-production.webp",
    icon: "/year-icon-2010.webp",
  },
  {
    id: "2015",
    label: "2015",
    title: "Міжнародні стандарти",
    desc:
      "Отримання сертифікацій якості. Виходимо на нові регіони України та налагоджуємо партнерства з провідними агрохолдингами.",
    img: "/lab-research.webp",
    icon: "/year-icon-2015.webp",
  },
  {
    id: "2020",
    label: "2020",
    title: "Технології та Сервіс",
    desc:
      "Комплексні рішення. Запуск власного агроконсалтингу. Ми перестали просто продавати препарати — ми почали продавати технологію вирощування «під ключ».",
    img: "/history-lab.webp",
    icon: "/year-icon-2020.webp",
  },
  {
    id: "2025",
    label: "2025",
    title: "Лідерство в галузі",
    desc:
      "Понад 5000 задоволених фермерів та 350+ тис. оброблених гектарів. Продовжуємо розробляти нові штами та цифрові інструменти моніторингу.",
    img: "/lab-storage.webp",
    icon: "/year-icon-2025.webp",
  },
];

/* Lab-cards stack animation constants — kept in DESIGN-PX (1920 width).
   They MUST stay in sync with about.module.css (.labCardTrack height,
   .labCardStage height, .labCardDeck height). */
const LAB_STAGE_HEIGHT = 855;        // title + gap + deck (in design-px)
const LAB_TRACK_HEIGHT = 2955;       // stage + (N-1) * scrollPerCard
const LAB_PIN_TOP = 140;             // pin offset from viewport top
const LAB_SCROLL_PER_CARD = 700;     // scroll-room each card transition

const About: React.FC = () => {
  // History/timeline interactive state — defaults to "2005" period (idx 1).
  const [activePeriodIdx, setActivePeriodIdx] = useState(1);
  const activePeriod = TIMELINE_PERIODS[activePeriodIdx];

  // Mobile detector — tracked via matchMedia(<=768px). Used to:
  //   • skip the scroll-driven LAB cards animation
  //   • disable hover-to-change on timeline
  //   • render mobile carousel arrows under the history card
  const [isMobile, setIsMobile] = useState<boolean>(() =>
    typeof window !== "undefined"
      ? window.matchMedia("(max-width: 768px)").matches
      : false,
  );
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mql = window.matchMedia("(max-width: 768px)");
    const onChange = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    setIsMobile(mql.matches);
    if (mql.addEventListener) mql.addEventListener("change", onChange);
    else mql.addListener(onChange);
    return () => {
      if (mql.removeEventListener) mql.removeEventListener("change", onChange);
      else mql.removeListener(onChange);
    };
  }, []);

  // History carousel helpers (mobile only — under card)
  const periodsCount = TIMELINE_PERIODS.length;
  const goPrevPeriod = () =>
    setActivePeriodIdx((i) => (i - 1 + periodsCount) % periodsCount);
  const goNextPeriod = () =>
    setActivePeriodIdx((i) => (i + 1) % periodsCount);

  // -------------------------------------------------------------------
  // Step-based slot-machine counter (перенесено 1:1 з Welcome /
  // frame-component8.tsx). Глобальний "step" індекс синхронно тягне
  // всі reels до targetIndex=step. Статичні reels (length=1) ігнорують
  // step. "+" з'являється fade-in одночасно з фінальним роллом.
  // Phase cycle:
  //   tick 0: snap reset (60ms)
  //   tick 1: hold 600ms       (показуємо "347" / "4997")
  //   tick 2: roll 320+450ms   (→ "348" / "4998")
  //   tick 3: roll 320+450ms   (→ "349" / "4999")
  //   tick 4: roll 320ms + "+" fade-in + hold 1900ms (→ "350+" / "5000+")
  //   loop
  // -------------------------------------------------------------------
  const numbersRef = useRef<HTMLDivElement | null>(null);
  const [numbersStarted, setNumbersStarted] = useState(false);
  const [step, setStep] = useState(0);
  const [snap, setSnap] = useState(true);
  const [showPlus, setShowPlus] = useState(false);

  // Trigger on viewport entry.
  useEffect(() => {
    const el = numbersRef.current;
    if (!el || numbersStarted) return;
    if (!("IntersectionObserver" in window)) {
      setNumbersStarted(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setNumbersStarted(true);
            io.disconnect();
            break;
          }
        }
      },
      { threshold: 0.3 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [numbersStarted]);

  // Step-based phase machine — мирорує Welcome 1:1.
  useEffect(() => {
    if (!numbersStarted) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const at = (ms: number, fn: () => void) => {
      timer = setTimeout(() => {
        if (!cancelled) fn();
      }, ms);
    };

    const startCycle = () => {
      if (cancelled) return;
      // 1. SNAP RESET
      setSnap(true);
      setShowPlus(false);
      setStep(0);

      at(RESET_MS, () => {
        setSnap(false);
        // 2. HOLD INITIAL
        at(INITIAL_HOLD, () => {
          // 3. ROLL → step 1
          setStep(1);
          at(ROLL_MS + HOLD_BETWEEN, () => {
            // 4. ROLL → step 2
            setStep(2);
            at(ROLL_MS + HOLD_BETWEEN, () => {
              // 5. ROLL → step 3 (FINAL) + "+" fade-in одночасно
              setStep(3);
              setShowPlus(true);
              // 6. ЗУПИНКА на фінальному значенні (без loop).
              //    Анімація запускається одноразово при вході в viewport.
            });
          });
        });
      });
    };

    startCycle();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [numbersStarted]);

  // Refs used by the scroll-driven card stack animation.
  const labTrackRef = useRef<HTMLDivElement | null>(null);
  const labStageRef = useRef<HTMLDivElement | null>(null);
  const labCardsRef = useRef<HTMLDivElement[]>([]);

  // useLayoutEffect (not useEffect) so we run BEFORE the browser paints,
  // avoiding a flash where cards appear at translateY 100% briefly.
  useLayoutEffect(() => {
    // Skip the scroll-driven pin/stack animation on mobile — there cards
    // render as a simple stacked column (see about.module.css @media).
    if (typeof window !== "undefined" &&
        window.matchMedia &&
        window.matchMedia("(max-width: 768px)").matches) {
      return;
    }
    const track = labTrackRef.current;
    const stage = labStageRef.current;
    const cards = labCardsRef.current.filter(Boolean);
    if (!track || !stage || cards.length === 0) return;

    const getScale = () => {
      const raw = getComputedStyle(document.documentElement)
        .getPropertyValue("--app-scale")
        .trim();
      const s = parseFloat(raw);
      return Number.isFinite(s) && s > 0 ? s : 1;
    };

    const clamp = (v: number, min: number, max: number) =>
      v < min ? min : v > max ? max : v;

    // Cached document-space top of the track.
    let trackDocTop = 0;
    const measureTrackDocTop = () => {
      const r = track.getBoundingClientRect();
      trackDocTop = window.scrollY + r.top;
    };

    // Last-applied transform values per element. We only write to the
    // DOM when the rounded integer value actually changes — eliminates
    // sub-pixel flicker that arises from the scaled parent.
    let lastStageY = -1;
    const lastCardY: number[] = new Array(cards.length).fill(-1);

    const computeAndApply = () => {
      const scale = getScale();
      const pinReal = LAB_PIN_TOP * scale;
      const stageReal = LAB_STAGE_HEIGHT * scale;
      const trackHeightReal = LAB_TRACK_HEIGHT * scale;
      const scrollPerCardReal = LAB_SCROLL_PER_CARD * scale;

      const trackTopReal = trackDocTop - window.scrollY;
      const passedReal = pinReal - trackTopReal;

      // Stage pin: clamp so it never leaves the track bounds.
      const maxStageOffsetReal = Math.max(0, trackHeightReal - stageReal);
      const stageOffsetReal = clamp(passedReal, 0, maxStageOffsetReal);
      // Convert real-px back to design-px (since the child of the
      // scaled container applies transforms in design space).
      const stageOffsetDesign = Math.round(stageOffsetReal / scale);

      if (stageOffsetDesign !== lastStageY) {
        lastStageY = stageOffsetDesign;
        stage.style.transform = `translate3d(0, ${stageOffsetDesign}px, 0)`;
      }

      // Per-card transitions.
      cards.forEach((card, i) => {
        let pct: number;
        if (i === 0) {
          pct = 0;
        } else {
          const sliceStart = (i - 1) * scrollPerCardReal;
          const sliceEnd = i * scrollPerCardReal;
          const local = clamp(
            (passedReal - sliceStart) / (sliceEnd - sliceStart),
            0,
            1,
          );
          pct = (1 - local) * 100;
        }
        // Snap to 0.1% steps so tiny scroll changes don't repaint.
        const snapped = Math.round(pct * 10) / 10;
        if (snapped !== lastCardY[i]) {
          lastCardY[i] = snapped;
          card.style.transform = `translate3d(0, ${snapped}%, 0)`;
        }
      });
    };

    // Continuous RAF loop while the section is in (or near) the pin
    // range. This decouples updates from the lagging scroll event and
    // ensures transforms commit in the SAME compositor frame as the
    // page scroll, producing rock-solid pixel-perfect pinning.
    let rafId: number | null = null;
    let isActive = false;
    const tick = () => {
      computeAndApply();
      if (isActive) {
        rafId = window.requestAnimationFrame(tick);
      } else {
        rafId = null;
      }
    };
    const startLoop = () => {
      if (isActive) return;
      isActive = true;
      if (rafId == null) rafId = window.requestAnimationFrame(tick);
    };
    const stopLoop = () => {
      isActive = false;
      if (rafId != null) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
    };

    // Use IntersectionObserver to toggle the RAF loop only while the
    // section is within (or near) the viewport. This avoids burning
    // CPU on every frame when the section is off-screen.
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            measureTrackDocTop();
            startLoop();
          } else {
            // Apply one last update so the cards settle at the
            // correct end state, then stop the loop.
            computeAndApply();
            stopLoop();
          }
        }
      },
      {
        // Generous rootMargin so we start updating BEFORE the section
        // is visually visible — eliminates any pop-in flicker on
        // entry/exit.
        rootMargin: "200px 0px 200px 0px",
        threshold: 0,
      },
    );
    io.observe(track);

    // Initial paint: measure & apply once synchronously, then again
    // after layout settles (double-RAF safety net for late CSS scale).
    measureTrackDocTop();
    computeAndApply();
    let raf1: number | null = null;
    let raf2: number | null = null;
    raf1 = window.requestAnimationFrame(() => {
      raf2 = window.requestAnimationFrame(() => {
        measureTrackDocTop();
        computeAndApply();
      });
    });

    const onResize = () => {
      measureTrackDocTop();
      computeAndApply();
    };
    window.addEventListener("resize", onResize);

    return () => {
      io.disconnect();
      stopLoop();
      window.removeEventListener("resize", onResize);
      if (raf1 != null) cancelAnimationFrame(raf1);
      if (raf2 != null) cancelAnimationFrame(raf2);
    };
  }, []);

    // Silence unused-var lint when useEffect is imported but unused here.
  void useEffect;

  return (
    <div className={styles.page} data-testid="about-page">
      <Seo
        title="Про нас — Не просто продаємо препарати"
        description="ТАМІС АГРО — український виробник живих біопрепаратів. +20 років історії, від лабораторних досліджень до повного циклу: розробка, виробництво, зберігання та доставка."
        canonical="/about"
        image="/agrovideo-1@2x.webp"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "AboutPage",
          name: "Про ТАМІС АГРО",
          inLanguage: "uk",
          url: "https://tamis-agro.ua/about",
        }}
      />
      {/* ===== Header (unchanged) ===== */}
      <Navbar1 device="Desktop" state="Default" size="20" size1="20" size2="16" />

      {/* ============ 1. HERO ============ */}
      <section className={styles.heroWrap}>
        <div className={styles.hero}>
          {/* Hero animation: lightweight MP4/WebM (1MB vs 16MB animated PNG).
              `agrovideo-1@2x.webp` залишено як poster/fallback. */}
          <video
            className={styles.heroBg}
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            poster="/agrovideo-1@2x.webp"
            aria-hidden="true"
          >
            <source src="/agrovideo-1.webm" type="video/webm" />
            <source src="/agrovideo-1.mp4" type="video/mp4" />
          </video>
          <div className={styles.heroInner}>
            <RevealHeading
              as="h1"
              className={styles.heroTitle}
              data-testid="about-hero-title"
              baseDelay={100}
              stagger={80}
              block
              lines={[[{ text: "не просто продаємо препарати" }]]}
            />
            <RevealHeading
              as="h2"
              className={styles.heroSubtitle}
              baseDelay={100 + 4 * 80}
              stagger={80}
              block
              lines={[[{ text: "Ми повертаємо землі силу" }]]}
            />
          </div>
        </div>
      </section>

      {/* ============ 2. NUMBERS ============ */}
      <section className={styles.numbersWrap} data-testid="about-numbers">
        <div className={styles.numbersInner} ref={numbersRef}>
          <div className={styles.numbersRow}>
            {NUMBERS.map((n) => {
              const finalValue =
                n.digits.map((d) => d[d.length - 1]).join("") +
                (n.label ? ` ${n.label}` : "") +
                (n.showPlus ? "+" : "");
              return (
                <div className={styles.numberCard} key={n.key}>
                  <div
                    className={`${styles.numberCardLine} ${
                      n.accent ? styles.numberCardLineAccent : ""
                    }`}
                  />
                  <div className={styles.numberCardContent}>
                    <h2
                      className={`${styles.numberCardTitle} ${
                        n.accent ? styles.numberCardTitleAccent : ""
                      }`}
                      data-testid={`about-num-${n.key}`}
                      aria-label={finalValue}
                    >
                      <span className={cardStyles.statRow}>
                        <span
                          className={cardStyles.digits}
                          aria-hidden="true"
                        >
                          {n.digits.map((d, i) => {
                            const isStatic = d.length === 1;
                            const targetIndex = isStatic
                              ? 0
                              : Math.min(step, d.length - 1);
                            return (
                              <AnimatedNumber
                                key={i}
                                sequence={d}
                                targetIndex={targetIndex}
                                snap={snap || isStatic}
                                rollMs={ROLL_MS}
                              />
                            );
                          })}
                        </span>
                        {n.label && (
                          <span
                            className={cardStyles.statLabel}
                            aria-hidden="true"
                          >
                            {n.label}
                          </span>
                        )}
                        {n.showPlus && (
                          <span
                            className={cardStyles.statPlus}
                            style={{
                              opacity: showPlus ? 1 : 0,
                              transition: snap
                                ? "none"
                                : `opacity ${ROLL_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
                            }}
                            aria-hidden="true"
                          >
                            +
                          </span>
                        )}
                      </span>
                    </h2>
                    <h3 className={styles.numberCardDesc}>{n.desc}</h3>
                  </div>
                </div>
              );
            })}
          </div>
          <div className={styles.numbersHr} />
        </div>
      </section>

      {/* ============ 3. MISSION ============ */}
      <section className={styles.missionWrap} data-testid="about-mission">
        <div className={styles.mission}>
          <img loading="lazy" decoding="async"
            className={styles.missionLeafBg}
            src="/anna-50943-A-green-leaf-puzzle-piece-clicking-into-place-comple-1a20d17d-b582-43eb-9096-247f63b56145-Photoroom-1@2x.webp"
            alt=""
          />
          <RevealHeading
            as="h2"
            className={styles.missionTitle}
            baseDelay={100}
            stagger={70}
            lines={[
              [
                { text: "Ціна помилки в агро — не просто цифри у звіті." },
                {
                  text: "Це здоров’я землі на роки вперед.",
                  className: styles.missionTitleAccent,
                },
              ],
            ]}
          />
          <div className={styles.missionRow}>
            <img loading="lazy" decoding="async"
              className={styles.missionLeafImg}
              src="/close-up-green-leaf-with-water-drops-1@2x.webp"
              alt=""
              width={732}
              height={915}
            />
            <div className={styles.missionTextCol}>
              <div className={styles.missionTextTop}>
                <h3 className={styles.missionLead}>
                  Хімія дає ілюзію швидкості, часто ціною опіків та виснаження
                  ґрунту.
                </h3>
                <div className={styles.missionStatement}>
                  <h2 className={styles.missionStatementTitle}>Наша місія</h2>
                  <div className={styles.missionStatementBody}>
                    <p className={styles.missionStatementText}>
                      шлях без компромісів: ми інтегруємо мікробіологію в існуючі
                      технології так, щоб ви отримали і рекордний врожай, і
                      чистий продукт з високою ринковою цінністю.
                    </p>
                    <p className={styles.missionStatementText}>
                      Біопрепарати сьогодні -  найрозумніша інвестиція в землю та
                      життя майбутнього покоління.
                    </p>
                  </div>
                </div>
              </div>
              <div className={styles.missionAuthor}>
                <h3 className={styles.missionAuthorName}>
                  Михайло Севастьянов
                </h3>
                <h4 className={styles.missionAuthorRole}>
                  Засновник &amp; власник
                </h4>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 4. LAB → FIELD ============ */}
      <section className={styles.labWrap} data-testid="about-lab">
        <div className={styles.labInner}>
          <div className={styles.labCardTrack} ref={labTrackRef}>
            <div className={styles.labCardStage} ref={labStageRef}>
              <h2 className={styles.labTitle}>
                <span className={styles.labTitleAccent}>Від лабораторії </span>
                до вашого поля
              </h2>
              <div className={styles.labCardDeck}>
                {LAB_CARDS.map((c, idx) => (
                  <div
                    className={styles.labCard}
                    key={c.num}
                    ref={(el) => {
                      if (el) labCardsRef.current[idx] = el;
                    }}
                  >
                    <div className={styles.labCardLeft}>
                      <h3 className={styles.labCardNumber}>{c.num}</h3>
                      <div className={styles.labCardContent}>
                        <h4 className={styles.labCardSubtitle}>{c.title}</h4>
                        <p className={styles.labCardDesc}>{c.desc}</p>
                      </div>
                    </div>
                    <img loading="lazy" decoding="async" className={styles.labCardImg} src={c.img} alt="" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 5. LOGISTICS (reused from Welcome) ============ */}
      <section data-testid="about-logistics">
        <LogisticsSection />
      </section>

      {/* ============ 6. HISTORY ============ */}
      <section className={styles.historyWrap} data-testid="about-history">
        <div className={styles.historyInner}>
          <div className={styles.historyHeader}>
            <RevealHeading
              as="h2"
              className={styles.historyTitle}
              baseDelay={100}
              stagger={80}
              block
              lines={[[{ text: "+20 років" }]]}
            />
            <RevealHeading
              as="h3"
              className={styles.historySubtitle}
              baseDelay={100 + 2 * 80}
              stagger={80}
              block
              lines={[[{ text: "нашої історії ефективності" }]]}
            />
          </div>

          <div className={styles.historyCard}>
            <img loading="lazy" decoding="async"
              key={activePeriod.id}
              className={styles.historyCardImage}
              src={activePeriod.img}
              alt={activePeriod.title}
            />
            <div className={styles.historyCardText}>
              <h3 className={styles.historyCardTitle}>{activePeriod.title}</h3>
              <p className={styles.historyCardDesc}>{activePeriod.desc}</p>
            </div>
          </div>

          {/* Sunflower timeline */}
          <div className={styles.timelineWrap}>
            {/* Vertical connector — 108 × 1px line linking the active card
                to the active sunflower below it. Slides horizontally on
                period change. Position formula matches flex space-between:
                center_i = 70px + i * (100% - 140px) / 5  (n=6, icon=140) */}
            <span
              className={styles.timelineConnector}
              aria-hidden="true"
              style={{
                left: `calc(${activePeriodIdx} * (100% - 140px) / 5 + 70px)`,
              }}
            />
            <div className={styles.timelineLine} aria-hidden="true" />
            <ul className={styles.timelineRow} role="tablist">
              {TIMELINE_PERIODS.map((p, idx) => {
                const isActive = idx === activePeriodIdx;
                return (
                  <li key={p.id} className={styles.timelineItem}>
                    <button
                      type="button"
                      role="tab"
                      aria-selected={isActive}
                      aria-label={`${p.id} — ${p.title}`}
                      data-testid={`history-period-${p.id}`}
                      className={
                        isActive
                          ? `${styles.timelineIcon} ${styles.timelineIconActive}`
                          : styles.timelineIcon
                      }
                      onClick={() => setActivePeriodIdx(idx)}
                      onMouseEnter={isMobile ? undefined : () => setActivePeriodIdx(idx)}
                    >
                      <img loading="lazy" decoding="async"
                        src={p.icon}
                        alt={`${p.id} — ${p.title}`}
                        draggable={false}
                      />
                    </button>
                    <span
                      className={
                        isActive
                          ? `${styles.timelineYearLabel} ${styles.timelineYearLabelActive}`
                          : styles.timelineYearLabel
                      }
                    >
                      {p.label}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Mobile-only carousel arrows for history (timeline hidden via CSS) */}
          <div className={styles.historyArrows} aria-hidden={isMobile ? "false" : "true"}>
            <button
              type="button"
              className={styles.historyArrowBtn}
              onClick={goPrevPeriod}
              aria-label="Попередній період"
              data-testid="history-carousel-prev"
            >
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
                <path d="M14 5L8 11L14 17" stroke="#1B4332" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <div className={styles.historyArrowsCenter}>
              <img
                src={activePeriod.icon}
                alt=""
                className={styles.historyArrowsIcon}
                aria-hidden="true"
                draggable={false}
              />
              <span className={styles.historyArrowsYear} data-testid="history-carousel-year">
                {activePeriod.label}
              </span>
            </div>
            <button
              type="button"
              className={styles.historyArrowBtn}
              onClick={goNextPeriod}
              aria-label="Наступний період"
              data-testid="history-carousel-next"
            >
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
                <path d="M8 5L14 11L8 17" stroke="#1B4332" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* ============ 7. TRUST (reused from Welcome) ============ */}
      <section data-testid="about-trust">
        <TrustSection />
      </section>

      {/* ============ 8. CTA (reused) ============ */}
      <CtaSection1 />

      {/* ===== Footer (unchanged) ===== */}
      <Footer1 device="Desktop" />
    </div>
  );
};

export default About;
