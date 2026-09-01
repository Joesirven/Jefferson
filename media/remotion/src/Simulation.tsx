import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Arrow, C, NodeBox, Title, appear, fade, fontStack, monoStack } from "./theme";

const personas = [
  "42 · Hispanic · F · Mission",
  "67 · White · M · Sunset",
  "29 · Black · F · Wynwood",
  "55 · Asian · M · Little Havana",
  "34 · White · NB · Castro",
  "71 · Hispanic · F · Excelsior",
];

export const Simulation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const endFade = 1 - fade(frame, 435, 450);

  // bar chart animation
  const barT = fade(frame, 300, 340);
  const bars = [
    { label: "Yes", pct: 0.58, color: C.green },
    { label: "No", pct: 0.31, color: C.pink },
    { label: "Unsure", pct: 0.11, color: C.orange },
  ];

  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: fontStack, opacity: endFade }}>
      <Title text="How a poll runs" sub="run_simulation · poll_precinct · aggregate_responses" />

      {/* Question card */}
      <NodeBox x={60} y={170} w={340} h={92} at={25} color={C.blue} title="Poll question" sub='"Should we build more affordable housing?"' fontSize={20} subSize={14} />

      {/* Persona cards */}
      {personas.map((p, i) => {
        const at = 50 + i * 7;
        return (
          <div
            key={p}
            style={{
              position: "absolute",
              left: 90 + (i % 2) * 190,
              top: 300 + Math.floor(i / 2) * 64,
              width: 180,
              height: 52,
              background: C.panel,
              border: `1.5px solid ${C.border}`,
              borderRadius: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: C.text,
              fontSize: 13,
              fontFamily: monoStack,
              ...appear(frame, fps, at),
            }}
          >
            {p}
          </div>
        );
      })}

      <Arrow x1={230} y1={262} x2={230} y2={296} at={46} />

      {/* persona -> prompt annotation */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 505,
          width: 400,
          color: C.dim,
          fontSize: 13,
          fontFamily: monoStack,
          textAlign: "center",
          opacity: fade(frame, 100, 115),
        }}
      >
        each persona → in-character prompt
      </div>

      {/* LLM box */}
      <NodeBox x={520} y={300} w={220} h={80} at={115} color={C.purple} title="LLM" sub="batched · 50 concurrent" fontSize={22} />
      <Arrow x1={470} y1={390} x2={520} y2={345} at={108} />

      {/* responses */}
      <NodeBox x={520} y={430} w={220} h={64} at={170} color={C.dim} title="Responses" sub="one per agent, in character" fontSize={18} subSize={12} />
      <Arrow x1={630} y1={380} x2={630} y2={430} at={162} />

      {/* Aggregation panel with bar chart */}
      <div
        style={{
          position: "absolute",
          left: 830,
          top: 250,
          width: 390,
          height: 280,
          background: C.panel,
          border: `2px solid ${C.pink}`,
          borderRadius: 12,
          padding: 18,
          boxSizing: "border-box",
          ...appear(frame, fps, 240),
        }}
      >
        <div style={{ color: C.text, fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Aggregate</div>
        <div style={{ color: C.dim, fontSize: 13, fontFamily: monoStack, marginBottom: 18 }}>
          choice → counts · scale → mean/min/max
        </div>
        {bars.map((b) => (
          <div key={b.label} style={{ marginBottom: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", color: C.text, fontSize: 14, marginBottom: 4 }}>
              <span>{b.label}</span>
              <span style={{ fontFamily: monoStack }}>{Math.round(b.pct * barT * 100)}%</span>
            </div>
            <div style={{ height: 16, background: C.bg, borderRadius: 8, overflow: "hidden" }}>
              <div style={{ width: `${b.pct * barT * 100}%`, height: "100%", background: b.color, borderRadius: 8 }} />
            </div>
          </div>
        ))}
        <div style={{ color: C.dim, fontSize: 12, fontFamily: monoStack, marginTop: 6 }}>
          crosstab by age · race · education · party
        </div>
      </div>
      <Arrow x1={740} y1={462} x2={830} y2={400} at={232} />

      {/* Save to Supabase */}
      <NodeBox x={880} y={580} w={290} h={64} at={330} color={C.green} title="save_results → Supabase" sub="then: CLI · FastAPI · web" fontSize={17} subSize={13} />
      <Arrow x1={1025} y1={530} x2={1025} y2={580} at={322} />

      {/* loop hint */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 610,
          width: 700,
          color: C.dim,
          fontSize: 14,
          fontFamily: monoStack,
          opacity: fade(frame, 350, 365),
        }}
      >
        repeat per question × per precinct: ~2,000-8,000 agents per run
      </div>
    </AbsoluteFill>
  );
};
