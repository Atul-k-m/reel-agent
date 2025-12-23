import React from "react";
import {
    AbsoluteFill,
    useVideoConfig,
    useCurrentFrame,
    interpolate,
    spring,
    Audio,
    Sequence,
    random,
} from "remotion";
import { z } from "zod";
import { CalculateMetadataFunction } from "remotion";

/* -------------------- SCHEMAS -------------------- */

const sceneSchema = z.object({
    narration: z.string(),
    visual_text: z.string().optional(),
    visual_prompt: z.string().optional(),
    duration_frames: z.number().optional(),
});

export const bauhausSchema = z.object({
    text: z.string().optional(),
    audioSrc: z.string().optional(),
    scenes: z.array(sceneSchema).optional(),
    timestamps: z.any().optional(),

    // 🔑 REQUIRED FOR LONG VIDEOS
    durationInFrames: z.number().optional(),
});

/* ---------------- METADATA HOOK ------------------ */

export const calculateMetadata: CalculateMetadataFunction<
    z.infer<typeof bauhausSchema>
> = ({ props }) => {
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

/* ------------------ CONSTANTS ------------------- */

const COLORS = [
    "#D93025", // Red
    "#1A3F99", // Blue
    "#F2C500", // Yellow
    "#202020", // Black
    "#F0EAD6", // Eggshell
];

/* ---------------- SHAPES ------------------------ */

const Circle = ({
    size,
    color,
    x,
    y,
    scale,
}: {
    size: number;
    color: string;
    x: number;
    y: number;
    scale: number;
}) => (
    <div
        style={{
            position: "absolute",
            left: x,
            top: y,
            width: size,
            height: size,
            borderRadius: "50%",
            backgroundColor: color,
            transform: `scale(${scale})`,
        }}
    />
);

const Rect = ({
    width,
    height,
    color,
    x,
    y,
    rotate,
    scale,
}: {
    width: number;
    height: number;
    color: string;
    x: number;
    y: number;
    rotate: number;
    scale: number;
}) => (
    <div
        style={{
            position: "absolute",
            left: x,
            top: y,
            width,
            height,
            backgroundColor: color,
            transform: `rotate(${rotate}deg) scale(${scale})`,
        }}
    />
);

/* ---------------- TEXT -------------------------- */

const PosterText = ({
    text,
    color,
    frame,
    fps,
}: {
    text: string;
    color: string;
    frame: number;
    fps: number;
}) => {
    const words = text.split(" ");

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                width: "100%",
                height: "100%",
                padding: 100,
            }}
        >
            {words.map((word, i) => {
                const delay = i * 5;
                const progress = spring({
                    frame: frame - delay,
                    fps,
                    config: { damping: 12 },
                });

                return (
                    <h1
                        key={i}
                        style={{
                            fontFamily:
                                'Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif',
                            fontSize: 120,
                            lineHeight: 0.9,
                            textTransform: "uppercase",
                            color,
                            margin: 0,
                            opacity: interpolate(progress, [0, 1], [0, 1]),
                            transform: `translateY(${interpolate(
                                progress,
                                [0, 1],
                                [100, 0]
                            )}px)`,
                        }}
                    >
                        {word}
                    </h1>
                );
            })}
        </div>
    );
};

/* ---------------- SCENE ------------------------- */

const BauhausPoster = ({
    scene,
    index,
}: {
    scene: z.infer<typeof sceneSchema>;
    index: number;
}) => {
    const { width, height, fps } = useVideoConfig();
    const frame = useCurrentFrame();

    const seed = index + 1;
    const bgColor = random(seed) > 0.5 ? "#F0EAD6" : "#202020";
    const fgColor = bgColor === "#F0EAD6" ? "#202020" : "#F0EAD6";

    const shapeScale = spring({ frame, fps });

    const displayText =
        scene.visual_text || scene.visual_prompt || "BAUHAUS";

    return (
        <AbsoluteFill style={{ backgroundColor: bgColor }}>
            <Circle
                size={800}
                color={COLORS[0]}
                x={width * random(seed * 4) - 200}
                y={height * random(seed * 5) - 200}
                scale={shapeScale}
            />

            <Rect
                width={150}
                height={1200}
                color={COLORS[1]}
                x={width * random(seed * 6)}
                y={-100}
                rotate={random(seed * 7) * 45}
                scale={shapeScale}
            />

            <PosterText
                text={displayText}
                color={fgColor}
                frame={frame}
                fps={fps}
            />
        </AbsoluteFill>
    );
};

/* ---------------- MAIN -------------------------- */

export const BauhausComposition: React.FC<
    z.infer<typeof bauhausSchema>
> = ({ audioSrc, scenes, durationInFrames = 300 }) => {
    const activeScenes =
        scenes && scenes.length > 0
            ? scenes
            : [
                { narration: "Intro", visual_text: "THE BAUHAUS MOVEMENT" },
                { narration: "Middle", visual_text: "FORM FOLLOWS FUNCTION" },
                { narration: "End", visual_text: "LESS IS MORE" },
            ];

    const fallback = Math.floor(durationInFrames / activeScenes.length);

    let current = 0;

    const timeline = activeScenes.map((scene) => {
        const duration = scene.duration_frames ?? fallback;
        const from = current;
        current += duration;
        return { scene, from, duration };
    });

    return (
        <AbsoluteFill>
            {audioSrc && <Audio src={audioSrc} />}
            {timeline.map(({ scene, from, duration }, i) => (
                <Sequence key={i} from={from} durationInFrames={duration}>
                    <BauhausPoster scene={scene} index={i} />
                </Sequence>
            ))}
        </AbsoluteFill>
    );
};
