import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const C = {
  bg: "#0d1117",
  panel: "#161b22",
  border: "#30363d",
  text: "#e6edf3",
  dim: "#8b949e",
  blue: "#58a6ff",
  green: "#3fb950",
  orange: "#d29922",
  purple: "#bc8cff",
  pink: "#f778ba",
};

export const fontStack =
  '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
export const monoStack =
  'ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace';

export const appear = (
  frame: number,
  fps: number,
  at: number
): { opacity: number; transform: string } => {
  const s = spring({ frame: frame - at, fps, config: { damping: 200 } });
  const y = interpolate(s, [0, 1], [14, 0]);
  return { opacity: s, transform: `translateY(${y}px)` };
};

export const fade = (frame: number, from: number, to: number): number =>
  Math.min(1, Math.max(0, interpolate(frame, [from, to], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })));

export const NodeBox: React.FC<{
  x: number;
  y: number;
  w: number;
  h?: number;
  title: string;
  sub?: string;
  color?: string;
  at: number;
  fontSize?: number;
  subSize?: number;
}> = ({ x, y, w, h = 84, title, sub, color = C.blue, at, fontSize = 21, subSize = 14 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        background: C.panel,
        border: `2px solid ${color}`,
        borderRadius: 12,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 4,
        padding: "0 12px",
        boxSizing: "border-box",
        fontFamily: fontStack,
        ...appear(frame, fps, at),
      }}
    >
      <div style={{ color: C.text, fontSize, fontWeight: 700, textAlign: "center", lineHeight: 1.15 }}>
        {title}
      </div>
      {sub ? (
        <div style={{ color: C.dim, fontSize: subSize, textAlign: "center", lineHeight: 1.25, fontFamily: monoStack }}>
          {sub}
        </div>
      ) : null}
    </div>
  );
};

export const Arrow: React.FC<{
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  at: number;
  color?: string;
}> = ({ x1, y1, x2, y2, at, color = C.dim }) => {
  const frame = useCurrentFrame();
  const progress = Math.min(1, Math.max(0, (frame - at) / 18));
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const ex = x1 + dx * progress;
  const ey = y1 + dy * progress;
  const left = Math.min(x1, x2) - 12;
  const top = Math.min(y1, y2) - 12;
  const w = Math.abs(dx) + 24;
  const h = Math.abs(dy) + 24;
  const ax = x1 - left;
  const ay = y1 - top;
  const bx = ex - left;
  const by = ey - top;
  const headLen = 9;
  const ux = len === 0 ? 0 : dx / len;
  const uy = len === 0 ? 0 : dy / len;
  const hx = bx - ux * headLen;
  const hy = by - uy * headLen;
  const px = -uy;
  const py = ux;
  return (
    <svg style={{ position: "absolute", left, top, overflow: "visible" }} width={w} height={h}>
      <line x1={ax} y1={ay} x2={bx} y2={by} stroke={color} strokeWidth={2.5} />
      {progress > 0.95 ? (
        <polygon
          points={`${bx},${by} ${hx + px * 5},${hy + py * 5} ${hx - px * 5},${hy - py * 5}`}
          fill={color}
        />
      ) : null}
    </svg>
  );
};

export const Title: React.FC<{ text: string; sub?: string; until?: number }> = ({ text, sub, until = 30 }) => {
  const frame = useCurrentFrame();
  const o = fade(frame, 0, 15);
  return (
    <div
      style={{
        position: "absolute",
        top: 30,
        left: 0,
        width: "100%",
        textAlign: "center",
        fontFamily: fontStack,
        opacity: o,
      }}
    >
      <div style={{ color: C.text, fontSize: 40, fontWeight: 800, letterSpacing: -0.5 }}>{text}</div>
      {sub ? <div style={{ color: C.dim, fontSize: 19, marginTop: 6 }}>{sub}</div> : null}
    </div>
  );
};
