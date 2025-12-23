import React from "react";
import { Composition } from "remotion";

import {
    BauhausComposition,
    bauhausSchema,
    calculateMetadata as bauhausMetadata,
} from "./Bauhaus/Composition";

import { SwissComposition, swissSchema } from "./Swiss/Composition";
import { NeonComposition, neonSchema } from "./Neon/Composition";
import { KineticComposition, kineticSchema } from "./Kinetic/Composition";

import { BoldComposition, boldSchema, calculateMetadata as boldMetadata } from "./Bold/Composition";
import { MinimalComposition, minimalSchema, calculateMetadata as minimalMetadata } from "./Minimal/Composition";
import { GlitchComposition, glitchSchema, calculateMetadata as glitchMetadata } from "./Glitch/Composition";
import { RetroComposition, retroSchema, calculateMetadata as retroMetadata } from "./Retro/Composition";


// Generic fallback metadata for compositions that may not export calculateMetadata
const genericMetadata = ({ props }: any) => {
    if (props.durationInFrames == null) {
        throw new Error('durationInFrames is required but missing in props');
    }
    return {
        durationInFrames: props.durationInFrames,
        fps: 30,
        width: 1080,
        height: 1920,
    };
};


export const RemotionRoot: React.FC = () => {
    return (
        <>
            {/* ✅ Bauhaus - calculateMetadata reads durationInFrames from props */}
            <Composition
                id="Bauhaus"
                component={BauhausComposition}

                fps={30}
                width={1080}
                height={1920}
                schema={bauhausSchema}
                calculateMetadata={bauhausMetadata}
                defaultProps={{
                    text: "BAUHAUS",
                    audioSrc: "",
                }}
            />

            {/* ✅ Swiss */}
            <Composition
                id="Swiss"
                component={SwissComposition}

                fps={30}
                width={1080}
                height={1920}
                schema={swissSchema}
                calculateMetadata={genericMetadata}
                defaultProps={{ text: "SWISS" }}
            />

            {/* ✅ Neon */}
            <Composition
                id="Neon"
                component={NeonComposition}

                fps={30}
                width={1080}
                height={1920}
                schema={neonSchema}
                calculateMetadata={genericMetadata}
                defaultProps={{ text: "NEON" }}
            />

            {/* ✅ Kinetic */}
            {/* ✅ Kinetic */}
            <Composition
                id="Kinetic"
                component={KineticComposition}
                fps={30}
                width={1080}
                height={1920}
                schema={kineticSchema}
                calculateMetadata={genericMetadata}
                defaultProps={{ text: "KINETIC" }}
            />

            {/* ✅ V2.0 NEW: Bold */}
            <Composition
                id="Bold"
                component={BoldComposition}
                fps={30}
                width={1080}
                height={1920}
                schema={boldSchema}
                calculateMetadata={boldMetadata}
                defaultProps={{ text: "BOLD" }}
            />

            {/* ✅ V2.0 NEW: Minimal */}
            <Composition
                id="Minimal"
                component={MinimalComposition}
                fps={30}
                width={1080}
                height={1920}
                schema={minimalSchema}
                calculateMetadata={minimalMetadata}
                defaultProps={{ text: "MINIMAL" }}
            />

            {/* ✅ V2.0 NEW: Glitch */}
            <Composition
                id="Glitch"
                component={GlitchComposition}
                fps={30}
                width={1080}
                height={1920}
                schema={glitchSchema}
                calculateMetadata={glitchMetadata}
                defaultProps={{ text: "GLITCH" }}
            />

            {/* ✅ V2.0 NEW: Retro */}
            <Composition
                id="Retro"
                component={RetroComposition}
                fps={30}
                width={1080}
                height={1920}
                schema={retroSchema}
                calculateMetadata={retroMetadata}
                defaultProps={{ text: "RETRO" }}
            />
        </>
    );
};
