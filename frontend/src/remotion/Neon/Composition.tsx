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

export const neonSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof neonSchema>> = ({ props }) => {
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

const NeonPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Neon", index), [index]);
    const text = scene.visual_text || scene.visual_prompt || "NEON LIGHTS";

    const colors = config.colors;
    const neonColor = colors[1] || '#0FF';

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            <DynamicBackground type={'particles'} colors={['#000', neonColor, '#111']} />

            <div style={{
                position: 'absolute',
                top: 0, left: 0, width: '100%', height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <div style={{
                    padding: '20px',
                    border: `4px solid ${neonColor}`,
                    boxShadow: `0 0 20px ${neonColor}, inset 0 0 20px ${neonColor}`,
                    borderRadius: '10px'
                }}>
                    <AnimatedText
                        text={text}
                        font={config.font}
                        effect={'none'}
                        animation={config.animation}
                        color={'#FFF'}
                        style={{
                            fontSize: '90px',
                            textShadow: `0 0 10px ${neonColor}, 0 0 20px ${neonColor}, 0 0 30px ${neonColor}`,
                            textAlign: 'center'
                        }}
                    />
                </div>
            </div>

            <SceneTransition type={'dissolve'} color={'#000'} />
        </AbsoluteFill>
    );
};

export const NeonComposition: React.FC<z.infer<typeof neonSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "NEON" }];
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
                        <NeonPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
