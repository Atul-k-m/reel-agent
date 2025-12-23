import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, random, interpolate } from 'remotion';
import { BackgroundType } from '../design-engine';

interface Props {
    type: BackgroundType;
    colors: string[];
}

export const DynamicBackground: React.FC<Props> = ({ type, colors }) => {
    const frame = useCurrentFrame();
    const { width, height } = useVideoConfig();
    const [c1, c2, c3] = colors;

    if (type === 'solid') {
        return <AbsoluteFill style={{ backgroundColor: c1 }} />;
    }

    if (type === 'gradient') {
        return <AbsoluteFill style={{
            background: `linear-gradient(${frame % 360}deg, ${c1}, ${c2 || c1})`
        }} />;
    }

    if (type === 'grid') {
        return (
            <AbsoluteFill style={{ backgroundColor: c1 }}>
                <div style={{
                    width: '100%',
                    height: '100%',
                    backgroundImage: `linear-gradient(${c2} 1px, transparent 1px), linear-gradient(90deg, ${c2} 1px, transparent 1px)`,
                    backgroundSize: '50px 50px',
                    transform: `translateY(${frame}px)`,
                    opacity: 0.3
                }} />
            </AbsoluteFill>
        );
    }

    if (type === 'particles') {
        return (
            <AbsoluteFill style={{ backgroundColor: c1 }}>
                {new Array(30).fill(0).map((_, i) => {
                    const seed = i * 23;
                    const x = (random(seed) * width + Math.sin(frame / 50 + seed) * 50) % width;
                    const y = (random(seed + 1) * height + frame * (random(seed + 2) * 5 + 2)) % height;
                    const size = random(seed + 3) * 10 + 2;
                    return (
                        <div key={i} style={{
                            position: 'absolute',
                            left: x,
                            top: y,
                            width: size,
                            height: size,
                            borderRadius: '50%',
                            backgroundColor: c2 || '#FFF'
                        }} />
                    );
                })}
            </AbsoluteFill>
        );
    }

    if (type === 'shapes') {
        return (
            <AbsoluteFill style={{ backgroundColor: c1 }}>
                {new Array(5).fill(0).map((_, i) => {
                    const size = 300;
                    const rotate = frame * (i % 2 === 0 ? 1 : -1) + i * 45;
                    return (
                        <div key={i} style={{
                            position: 'absolute',
                            left: interpolate(random(i), [0, 1], [0, width]) - size / 2,
                            top: interpolate(random(i + 1), [0, 1], [0, height]) - size / 2,
                            width: size,
                            height: size,
                            border: `4px solid ${c2 || '#FFF'}`,
                            transform: `rotate(${rotate}deg)`,
                            opacity: 0.2
                        }} />
                    );
                })}
            </AbsoluteFill>
        );
    }

    return <AbsoluteFill style={{ backgroundColor: '#000' }} />;
};
