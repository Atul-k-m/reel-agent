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

export const boldSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    durationInFrames: z.number().optional(),
});

export const calculateMetadata: CalculateMetadataFunction<z.infer<typeof boldSchema>> = ({ props }) => {
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

const BoldPoster = ({ scene, index }: { scene: z.infer<typeof sceneSchema>; index: number }) => {
    const { width } = useVideoConfig();

    // 🎨 DYNAMIC DESIGN ENGINE
    const config = useMemo(() => getDesignConfig("Bold", index), [index]);

    const text = scene.visual_text || scene.visual_prompt || "BOLD IMPACT";

    // Bold specific override: Ensure high contrast
    const bgColor = config.colors[0];
    const textColor = config.colors[1] || '#FFF';
    const accentColor = config.colors[2] || '#ff0000';

    return (
        <AbsoluteFill style={{ overflow: 'hidden' }}>
            {/* 1. Dynamic Background */}
            <DynamicBackground type={config.background} colors={[bgColor, accentColor, textColor]} />

            {/* 2. Main Content */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '50px'
            }}>
                <div style={{
                    border: `15px solid ${accentColor}`,
                    padding: '40px',
                    backgroundColor: bgColor, // Box background
                    maxWidth: '90%'
                }}>
                    <AnimatedText
                        text={text}
                        font={config.font}
                        effect={config.textEffect}
                        animation={config.animation}
                        color={textColor}
                        style={{
                            fontSize: '100px',
                            textTransform: 'uppercase',
                            textAlign: 'center',
                            lineHeight: 0.9,
                            margin: 0,
                            wordBreak: 'break-word',
                        }}
                    />
                </div>
            </div>

            {/* 3. Scene Transition (Entry) */}
            <SceneTransition type={config.transition} color={accentColor} />

        </AbsoluteFill>
    );
};

export const BoldComposition: React.FC<z.infer<typeof boldSchema>> = ({ audioSrc, scenes, durationInFrames }) => {
    const activeScenes = scenes && scenes.length > 0 ? scenes : [{ narration: "Intro", visual_text: "BOLD STYLE" }];
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
                        <BoldPoster scene={scene} index={i} />
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};
