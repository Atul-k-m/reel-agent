import React, { useMemo } from "react";
import {
    AbsoluteFill,
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

export const retroSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof retroSchema>> = ({ props }) => {
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

const RetroPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Retro", index), [index]);
    const text = scene.visual_text || scene.visual_prompt || "RETRO WAVE";

    // Retro Override: Gradient background preferred
    const colors = config.colors;

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            <DynamicBackground type={'gradient'} colors={colors} />

            {/* Retro Sun / Grid Overlay */}
            {index % 2 === 0 && (
                <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    width: '100%',
                    height: '50%',
                    background: `linear-gradient(to top, ${colors[0]} 2px, transparent 2px)`,
                    backgroundSize: '100% 40px',
                    opacity: 0.5,
                    transform: 'perspective(500px) rotateX(60deg)'
                }} />
            )}

            <div style={{
                position: 'absolute',
                top: 0, left: 0, width: '100%', height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <AnimatedText
                    text={text}
                    font={config.font}
                    effect={config.textEffect}
                    animation={config.animation}
                    color={colors[1] || '#0ff'}
                    style={{
                        fontSize: '90px',
                        textShadow: `5px 5px 0px ${colors[2] || '#f0f'}`,
                        textAlign: 'center'
                    }}
                />
            </div>

            <SceneTransition type={'iris'} color={'#fff'} />
        </AbsoluteFill>
    );
};

export const RetroComposition: React.FC<z.infer<typeof retroSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "RETRO" }];
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
                        <RetroPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
