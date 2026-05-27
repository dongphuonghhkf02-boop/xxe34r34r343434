import React from "react";
import { type CSSProperties } from "react";
import styles from "./jerrycan1.module.css";

export type Jerrycan1Type = {
  className?: string;

  /** Variant props */
  size?: any;
};

const Jerrycan1: React.FC<Jerrycan1Type> = ({ className = "", size = 16 }) => {
  return (
    <div
      className={[styles.iconJerrycan, className].join(" ")}
      data-size={size}
    >
      <img loading="lazy" decoding="async"
        className={styles.vectorIcon}
        width={9.3}
        height={12.7}
        alt=""
        src="/Vector25.svg"
      />
    </div>
  );
};

export default Jerrycan1;
