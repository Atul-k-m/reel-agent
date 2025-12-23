import React, { useMemo } from "react";
import {
    AbsoluteFill,
    useVideoConfig,
    Audio,
    Sequence,
} from "remotion";
import { z } from "zod";
import { CalculateMetadataFunction } from "remotion";
import { getDesignConfig } from "../design-engine";
import { DynamicBackground } from "../Shared/Backgrounds";
import { AnimatedText } from "../Shared/TextEffects";
import { SceneTransition } from "../Shared/Transitions";

const sceneSchema = z.object({
    narration: z.string(),
    visual_text: z.string().optional(),
    visual_prompt: z.string().optional(),
    duration_frames: z.number().optional(),
});

export const minimalSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof minimalSchema>> = ({ props }) => {
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

const MinimalPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Minimal", index), [index]);

    const text = scene.visual_text || scene.visual_prompt || "Minimal";

    // Minimal override: Mostly solid BG, clean text
    const bgColor = config.colors[0]; // Usually white
    const textColor = config.colors[1]; // Usually black

    // Force a simpler background for Minimal
    const bgType = index % 2 === 0 ? 'solid' : 'gradient';

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            <DynamicBackground type={bgType} colors={config.colors} />

            <div style={{
                position: 'absolute',
                top: 0, left: 0, width: '100%', height: '100%',
                padding: '80px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'flex-start'
            }}>
                <AnimatedText
                    text={text.toLowerCase()}
                    font={config.font}
                    effect={config.textEffect}
                    animation={config.animation}
                    color={textColor}
                    style={{
                        fontSize: '90px',
                        fontWeight: 700,
                        letterSpacing: '-2px',
                    }}
                />
                <div style={{
                    width: '100px',
                    height: '8px',
                    backgroundColor: textColor,
                    marginTop: '40px',
                }} />
            </div>

            <SceneTransition type={config.transition} color={textColor} />
        </AbsoluteFill>
    );
};

export const MinimalComposition: React.FC<z.infer<typeof minimalSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "Minimal" }];
    const fallback = Math.floor((durationInFrames || 300) / activeScenes.length);
    let current = 0;

    return (
        <AbsoluteFill>
            {audioSrc && <Audio src={audioSrc} />}
            {activeScenes.map((scene, i) => {
                const duration = scene.duration_frames ?? fallback;
                const from = current;
                current += duration;
                return (
                    <Sequence key={i} from={from} durationInFrames={duration}>
                        <MinimalPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
