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

export const swissSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof swissSchema>> = ({ props }) => {
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

const SwissPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Swiss", index), [index]);
    const text = scene.visual_text || scene.visual_prompt || "HELVETICA";

    // Swiss Palette: Black/White/Red/Yellow
    const colors = config.colors.length > 2 ? config.colors : ["#FFF", "#000", "#F00"];

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            <DynamicBackground type={'solid'} colors={[colors[0], colors[1], colors[2]]} />

            {/* Swiss Grid Decor */}
            <div style={{
                position: 'absolute',
                top: 50, left: 50, right: 50, bottom: 50,
                border: `4px solid ${colors[1]}`,
                display: 'flex',
                alignItems: 'flex-start',
                padding: '40px'
            }}>
                <div style={{
                    position: 'absolute', top: 0, right: 20,
                    fontSize: 24, fontWeight: 'bold', fontFamily: config.font, color: colors[1]
                }}>
                    No. {index + 1}
                </div>
            </div>

            <div style={{
                position: 'absolute',
                top: '30%', left: '100px', right: '100px'
            }}>
                <AnimatedText
                    text={text}
                    font={config.font}
                    effect={'none'} // Swiss is usually clean
                    animation={config.animation}
                    color={colors[1]}
                    style={{
                        fontSize: '120px',
                        fontWeight: 900,
                        lineHeight: 0.85,
                        letterSpacing: '-4px'
                    }}
                />
                <div style={{
                    marginTop: '30px',
                    width: '150px',
                    height: '150px',
                    backgroundColor: colors[2] || '#F00',
                    borderRadius: '50%'
                }} />
            </div>

            <SceneTransition type={'wipe'} color={colors[1]} />
        </AbsoluteFill>
    );
};

export const SwissComposition: React.FC<z.infer<typeof swissSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "SWISS STYLE" }];
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
                        <SwissPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
