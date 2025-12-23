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

export const glitchSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof glitchSchema>> = ({ props }) => {
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

const GlitchPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Glitch", index), [index]);
    const text = scene.visual_text || scene.visual_prompt || "SYSTEM FAULT";

    // Glitch Override: Prefer Glitch effect
    const effect = index % 2 === 0 ? 'glitch' : config.textEffect;

    // Colors: Matrix Green, Cyber Cyan, Error Red
    const colors = config.colors;

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            {/* Dark BG usually */}
            <DynamicBackground type={'grid'} colors={colors} />

            {/* Scanlines Overlay */}
            <div style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, rgba(0, 0, 0, 0.5) 3px)',
                pointerEvents: 'none'
            }} />

            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '100%',
                textAlign: 'center'
            }}>
                <AnimatedText
                    text={text}
                    font={config.font}
                    effect={effect}
                    animation={config.animation}
                    color={colors[1] || '#0f0'}
                    style={{
                        fontSize: '110px',
                        textShadow: `4px 4px 0px ${colors[2] || '#f0f'}`,
                    }}
                />
            </div>

            <SceneTransition type={'dissolve'} color={'#000'} />
        </AbsoluteFill>
    );
};

export const GlitchComposition: React.FC<z.infer<typeof glitchSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "GLITCH" }];
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
                        <GlitchPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
