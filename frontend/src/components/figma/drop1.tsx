import React from "react";
import { useMemo, type CSSProperties } from "react";
import styles from "./drop1.module.css";

export type Drop1Type = {
  className?: string;

  /** Variant props */
  size?: any;

  /** Style props */
  dropHeight?: any;
  dropWidth?: any;
};

const Drop1: React.FC<Drop1Type> = ({
  className = "",
  size = 16,
  dropHeight,
  dropWidth,
}) => {
  const dropStyle: CSSProperties = useMemo(() => {
    return {
      height: dropHeight,
      width: dropWidth,
    };
  }, [dropHeight, dropWidth]);

  return (
    <div
      className={[styles.root, className].join(" ")}
      data-size={size}
      style={dropStyle}
    >
      <img loading="lazy" decoding="async"
        className={styles.vectorIcon}
        width={10.6}
        height={13.4}
        alt=""
        src="/Vector6.svg"
      />
    </div>
  );
};

export default Drop1;
