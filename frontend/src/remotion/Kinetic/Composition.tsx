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

export const kineticSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof kineticSchema>> = ({ props }) => {
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

const KineticPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const config = useMemo(() => getDesignConfig("Kinetic", index), [index]);
    const text = scene.visual_text || scene.visual_prompt || "KINETIC ENERGY";

    // Kinetic: Bold colors, simple shapes
    const colors = config.colors;

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            <DynamicBackground type={'shapes'} colors={colors} />

            <div style={{
                position: 'absolute',
                top: 0, left: 0, width: '100%', height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                transform: `rotate(${index % 2 === 0 ? 5 : -5}deg)`
            }}>
                <AnimatedText
                    text={text}
                    font={config.font}
                    effect={'stagger'}
                    animation={'zoom'}
                    color={colors[1] || '#FFF'}
                    style={{
                        fontSize: '130px',
                        fontWeight: 900,
                        textAlign: 'center',
                        backgroundColor: colors[0],
                        padding: '20px',
                        lineHeight: 1
                    }}
                />
            </div>

            <SceneTransition type={'push'} color={colors[1] || '#FFF'} />
        </AbsoluteFill>
    );
};

export const KineticComposition: React.FC<z.infer<typeof kineticSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "KINETIC" }];
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
                        <KineticPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
