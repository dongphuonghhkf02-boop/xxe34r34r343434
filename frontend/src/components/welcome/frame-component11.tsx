import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import CardItem1 from "./card-item1";
import PrimaryButton1 from "./primary-button1";
import RevealHeading from "./reveal-heading";
import TiltCard from "./tilt-card";
import { useParallax } from "../../lib/use-parallax";
import { useSwipeable } from "../../lib/use-swipeable";
import { useCart } from "../../context/CartContext";
import { listProducts, pickProductCover, type Product as ApiProduct } from "../../lib/products-api";
import styles from "./frame-component11.module.css";

export type FrameComponent11Type = {
  className?: string;
};

/* ----------------------------- Catalog --------------------------------- */
type Product = {
  id: string;
  slug: string;
  photo: string;
  name: string;
  desc: string;
  showTag2: boolean;
  price: number;
  volume: string;
  rating: number;
  reviews: number;
  packing: string;
  norm: string;
};

const CARDS_PER_PAGE = 3;
const CARD_WIDTH = 544;
const CARD_GAP = 24;
const PAGE_STRIDE = CARDS_PER_PAGE * CARD_WIDTH + CARDS_PER_PAGE * CARD_GAP; // 3*544 + 3*24 = 1704

/* ----------------------------- Chevron --------------------------------- */
const ChevronIcon: React.FC<{ dir: "left" | "right" }> = ({ dir }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d={dir === "left" ? "M12.5 4L6.5 10L12.5 16" : "M7.5 4L13.5 10L7.5 16"}
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/* ----------------------------- Component -------------------------------- */
const FrameComponent11: React.FC<FrameComponent11Type> = ({
  className = "",
}) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(0);

  // Scroll parallax for the whole carousel block (subtle vertical drift,
  // identical strength to BlogPart1 for a coherent feel)
  const parallaxRef = useParallax<HTMLDivElement>(40);

  /* Tier 1 — adminкурований "Вибір агрономів". Якщо адмін не виставив жодного —
     показуємо fallback: топ-9 за `sort=rec` (is_hit DESC). */
  useEffect(() => {
    let cancelled = false;

    const mapItems = (items: ApiProduct[]): Product[] =>
      items.map((p: ApiProduct) => ({
        id: p.id,
        slug: p.slug,
        photo: pickProductCover(p),
        name: p.name,
        desc: p.short_desc,
        showTag2: !!p.is_hit,
        price: p.price,
        volume: p.default_volume,
        rating: p.rating,
        reviews: p.reviews,
        packing: p.packing,
        norm: p.norm,
      }));

    (async () => {
      try {
        // Primary: admin-curated selection (Вибір агрономів)
        const primary = await listProducts({ agronomist_choice: true, limit: 9 });
        if (!cancelled && (primary.items || []).length > 0) {
          setProducts(mapItems(primary.items));
          return;
        }
        // Fallback: топ-9 за рекомендованим сортуванням
        const fallback = await listProducts({ sort: "rec", limit: 9 });
        if (!cancelled) {
          setProducts(mapItems(fallback.items || []));
        }
      } catch {
        /* silently ignore — UI лишається порожнім каруселем */
      }
    })();

    return () => { cancelled = true; };
  }, []);

  const TOTAL_PAGES = Math.max(1, Math.ceil(products.length / CARDS_PER_PAGE));
  const canPrev = page > 0;
  const canNext = page < TOTAL_PAGES - 1;
  const translateX = -page * PAGE_STRIDE;

  // Swipe / drag — пальцем, мишею або тачпадом горизонтально.
  const carouselSwipeRef = useSwipeable<HTMLDivElement>({
    onNext: () => setPage((p) => Math.min(TOTAL_PAGES - 1, p + 1)),
    onPrev: () => setPage((p) => Math.max(0, p - 1)),
    threshold: 60,
    enabled: () => TOTAL_PAGES > 1,
  });

  const { addItem, openCart } = useCart();

  const handleAddProduct = (p: Product) => {
    addItem({
      id: `${p.id}-${p.volume}`,
      productId: p.id,
      name: p.name,
      category: p.desc,
      volume: p.volume,
      price: p.price,
      image: p.photo,
    });
    openCart();
  };

  const items = useMemo(
    () =>
      products.map((p) => ({
        device: "Desktop" as const,
        slug: p.slug,
        photo: p.photo,
        prop: p.name,
        prop1: p.desc,
        showTag2: p.showTag2,
        showTag1: true,
        cardItemHeight: "725px" as const, // standardize ALL cards
        contentFlex: undefined,
        contentHeight: undefined,
        iconStarSize: 16,
        iconStarSize1: 16,
        iconStarSize2: 16,
        iconStarSize3: 16,
        iconStarSize4: 16,
        iconStar: "/Star.svg",
        iconStar1: "/Star.svg",
        iconStar2: "/Star.svg",
        iconStar3: "/Star.svg",
        iconStar4: "/Star.svg",
        size: 16,
        size1: 16,
        size2: 24,
        size3: 16,
        showFire: true,
        onAddToCart: () => handleAddProduct(p),
        priceLabel: `від ${Math.round(p.price)} ₴/л`,
        taraLabel: p.packing ? `Тара: ${p.packing}` : undefined,
        normaLabel: p.norm ? `Норма: ${p.norm}` : undefined,
        ratingValue: p.rating,
        ratingCount: p.reviews,
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [products]
  );

  return (
    <section
      className={[styles.topProductSectionWrapper, className].join(" ")}
    >
      <div className={styles.topProductSection}>
        <div ref={parallaxRef} className={styles.parallaxLayer}>
        <RevealHeading
          as="div"
          className={styles.headline}
          lineClassName={[styles.div, styles.div2]}
          block
          baseDelay={100}
          stagger={85}
          lines={[
            [
              { text: "Вибір", className: styles.span },
              { text: "українських", className: styles.span3 },
            ],
            [{ text: "агрономів", className: styles.span4 }],
          ]}
        />

        <div className={styles.mainContent}>
          <div className={styles.carouselBlock}>
            <div className={styles.cardsWrapper}>
              {/* Arrow buttons */}
              <button
                type="button"
                aria-label="Попередній слайд"
                data-testid="carousel-prev"
                disabled={!canPrev}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className={[
                  styles.arrowBtn,
                  styles.arrowBtnLeft,
                  canPrev ? styles.arrowActive : styles.arrowInactive,
                ].join(" ")}
              >
                <ChevronIcon dir="left" />
              </button>
              <button
                type="button"
                aria-label="Наступний слайд"
                data-testid="carousel-next"
                disabled={!canNext}
                onClick={() =>
                  setPage((p) => Math.min(TOTAL_PAGES - 1, p + 1))
                }
                className={[
                  styles.arrowBtn,
                  styles.arrowBtnRight,
                  canNext ? styles.arrowActive : styles.arrowInactive,
                ].join(" ")}
              >
                <ChevronIcon dir="right" />
              </button>

              {/* Cards viewport */}
              <div
                className={styles.cardsViewport}
                ref={carouselSwipeRef}
                style={{ touchAction: "pan-y", userSelect: "none" }}
              >
                <div
                  className={styles.cardsGroup}
                  style={{ transform: `translate3d(${translateX}px,0,0)` }}
                >
                  {items.map((item, index) => (
                    <div key={index} className={styles.cardSlot}>
                      <TiltCard maxTilt={3} lift={4}>
                      <CardItem1
                        device={item.device}
                        photo={item.photo}
                        prop={item.prop}
                        prop1={item.prop1}
                        showTag2={item.showTag2}
                        showTag1={item.showTag1}
                        cardItemHeight={item.cardItemHeight}
                        contentFlex={item.contentFlex}
                        contentHeight={item.contentHeight}
                        iconStarSize={item.iconStarSize}
                        iconStarSize1={item.iconStarSize1}
                        iconStarSize2={item.iconStarSize2}
                        iconStarSize3={item.iconStarSize3}
                        iconStarSize4={item.iconStarSize4}
                        iconStar={item.iconStar}
                        iconStar1={item.iconStar1}
                        iconStar2={item.iconStar2}
                        iconStar3={item.iconStar3}
                        iconStar4={item.iconStar4}
                        size={item.size}
                        size1={item.size1}
                        size2={item.size2}
                        size3={item.size3}
                        showFire={item.showFire}
                        onAddToCart={item.onAddToCart}
                        slug={item.slug}
                        priceLabel={item.priceLabel}
                        taraLabel={item.taraLabel}
                        normaLabel={item.normaLabel}
                        ratingValue={item.ratingValue}
                        ratingCount={item.ratingCount}
                      />
                      </TiltCard>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Pagination dots */}
            <div className={styles.dots} role="tablist" aria-label="Слайди">
              {Array.from({ length: TOTAL_PAGES }).map((_, i) => (
                <button
                  key={i}
                  type="button"
                  role="tab"
                  aria-selected={i === page}
                  aria-label={`Слайд ${i + 1}`}
                  data-testid={`carousel-dot-${i}`}
                  onClick={() => setPage(i)}
                  className={[
                    styles.dot,
                    i === page ? styles.dotActive : "",
                  ].join(" ")}
                />
              ))}
            </div>
          </div>

          <PrimaryButton1
            state="Default"
            type="Filled"
            prop="Переглянути лінійку"
            primaryButtonPadding="18px 16px"
            primaryButtonWidth="540px"
            size="24"
            onClick={() => navigate("/catalog")}
          />
        </div>
        </div>
      </div>
    </section>
  );
};

export default FrameComponent11;
