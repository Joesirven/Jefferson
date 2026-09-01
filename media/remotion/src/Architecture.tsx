import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Arrow, C, NodeBox, Title, fontStack, monoStack, fade } from "./theme";

// 1280x720. Pipeline: sources -> persona generation -> Supabase -> simulation engine -> aggregation -> outputs
export const Architecture: React.FC = () => {
  const frame = useCurrentFrame();
  const endFade = fade(frame, 435, 450) === 0 ? 1 : 1 - fade(frame, 435, 450);

  const spineY = 300;
  const nodeH = 84;

  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: fontStack, opacity: endFade }}>
      <Title text="Jefferson: system architecture" sub="Silicon polling: synthetic voters grounded in real demographics" />

      {/* Sources (top row) */}
      <NodeBox x={60} y={150} w={250} h={70} at={30} color={C.orange} title="ACS Census data" sub="DP05 · DP03 · DP02 · S1501" fontSize={19} subSize={13} />
      <NodeBox x={340} y={150} w={250} h={70} at={38} color={C.orange} title="TOP survey data" sub="issues · vote history · news diet" fontSize={19} subSize={13} />
      <NodeBox x={620} y={150} w={250} h={70} at={46} color={C.orange} title="Local news scrapers" sub="SF Chronicle · Mission Local · Miami Herald" fontSize={19} subSize={13} />

      {/* Arrows from sources to persona generation */}
      <Arrow x1={185} y1={220} x2={185} y2={spineY} at={55} />
      <Arrow x1={465} y1={220} x2={250} y2={spineY} at={58} />

      {/* Main spine */}
      <NodeBox x={60} y={spineY} w={250} h={nodeH} at={62} color={C.blue} title="Persona generation" sub="sample demographics · match survey respondent" />
      <Arrow x1={310} y1={spineY + nodeH / 2} x2={392} y2={spineY + nodeH / 2} at={78} />
      <NodeBox x={392} y={spineY} w={230} h={nodeH} at={84} color={C.green} title="Supabase (Postgres)" sub="personas · surveys · news · simulations" />
      <Arrow x1={622} y1={spineY + nodeH / 2} x2={704} y2={spineY + nodeH / 2} at={100} />
      <NodeBox x={704} y={spineY} w={250} h={nodeH} at={106} color={C.purple} title="Simulation engine" sub="Prefect flows · 50 concurrent agents" />
      <Arrow x1={954} y1={spineY + nodeH / 2} x2={1036} y2={spineY + nodeH / 2} at={122} />
      <NodeBox x={1036} y={spineY} w={190} h={nodeH} at={128} color={C.pink} title="Aggregation" sub="counts · stats · crosstabs" />

      {/* News arrow into engine */}
      <Arrow x1={745} y1={220} x2={800} y2={spineY} at={61} />

      {/* LLM row under engine */}
      <NodeBox x={704} y={460} w={250} h={64} at={140} color={C.dim} title="Multi-LLM" sub="GLM · Gemini · Claude" fontSize={19} subSize={13} />
      <Arrow x1={829} y1={460} x2={829} y2={spineY + nodeH} at={152} />

      {/* Outputs under aggregation */}
      <NodeBox x={1036} y={460} w={190} h={64} at={160} color={C.dim} title="Click CLI" sub="jefferson poll" fontSize={18} subSize={13} />
      <NodeBox x={1036} y={540} w={190} h={64} at={168} color={C.dim} title="FastAPI" sub="/v1/poll/precinct" fontSize={18} subSize={13} />
      <NodeBox x={1036} y={620} w={190} h={64} at={176} color={C.dim} title="Next.js web" sub="jefferson-one.vercel.app" fontSize={18} subSize={12} />
      <Arrow x1={1131} y1={spineY + nodeH} x2={1131} y2={460} at={158} />

      {/* Footer note */}
      <div
        style={{
          position: "absolute",
          bottom: 26,
          width: "100%",
          textAlign: "center",
          color: C.dim,
          fontSize: 15,
          fontFamily: monoStack,
          opacity: fade(frame, 190, 205),
        }}
      >
        backend/ · Python 3.12 · uv  |  web/ · Next.js 15  |  docs/archive/ · earlier prototypes
      </div>
    </AbsoluteFill>
  );
};
