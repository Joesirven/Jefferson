import React from "react";
import { Composition } from "remotion";
import { Architecture } from "./Architecture";
import { Simulation } from "./Simulation";

export const Root: React.FC = () => {
  return (
    <>
      <Composition id="Architecture" component={Architecture} durationInFrames={450} fps={30} width={1280} height={720} />
      <Composition id="Simulation" component={Simulation} durationInFrames={450} fps={30} width={1280} height={720} />
    </>
  );
};
