import React from "react";
import { useMemo, type CSSProperties } from "react";
import styles from "./temperature1.module.css";

export type Temperature1Type = {
  className?: string;

  /** Variant props */
  size?: any;

  /** Style props */
  temperatureHeight?: any;
  temperatureWidth?: any;
};

const Temperature1: React.FC<Temperature1Type> = ({
  className = "",
  size = 20,
  temperatureHeight,
  temperatureWidth,
}) => {
  const temperatureStyle: CSSProperties = useMemo(() => {
    return {
      height: temperatureHeight,
      width: temperatureWidth,
    };
  }, [temperatureHeight, temperatureWidth]);

  return (
    <div
      className={[styles.root, className].join(" ")}
      data-size={size}
      style={temperatureStyle}
    >
      <img loading="lazy" decoding="async"
        className={styles.vectorIcon}
        width={10}
        height={18}
        alt=""
        src="/Vector7.svg"
      />
    </div>
  );
};

export default Temperature1;
