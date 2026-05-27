import React from "react";
import { type CSSProperties } from "react";
import styles from "./drop1.module.css";

export type Drop1Type = {
  className?: string;

  /** Variant props */
  size?: any;
};

const Drop1: React.FC<Drop1Type> = ({ className = "", size = 16 }) => {
  return (
    <div className={[styles.iconDrop, className].join(" ")} data-size={size}>
      <img loading="lazy" decoding="async"
        className={styles.vectorIcon}
        width={10.6}
        height={13.4}
        alt=""
        src="/Vector8.svg"
      />
    </div>
  );
};

export default Drop1;
