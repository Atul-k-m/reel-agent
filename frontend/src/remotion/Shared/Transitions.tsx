import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { TransitionType } from '../design-engine';

interface Props {
    type: TransitionType;
    color: string;
    duration?: number;
}

export const SceneTransition: React.FC<Props> = ({ type, color, duration = 15 }) => {
    const frame = useCurrentFrame();
    const { fps, width, height } = useVideoConfig();

    // We animate OUT (reveal the scene) from frame 0 to duration
    const progress = spring({
        frame,
        fps,
        config: { damping: 200 },
        durationInFrames: duration
    });

    if (type === 'none') return null;

    if (type === 'dissolve') {
        const opacity = interpolate(progress, [0, 1], [1, 0]);
        if (opacity <= 0) return null;
        return <AbsoluteFill style={{ backgroundColor: color, opacity }} />;
    }

    if (type === 'wipe') {
        const transX = interpolate(progress, [0, 1], [0, width]);
        if (progress >= 1) return null;
        return <AbsoluteFill style={{ backgroundColor: color, transform: `translateX(${transX}px)` }} />;
    }

    if (type === 'push') {
        const transY = interpolate(progress, [0, 1], [0, height]);
        if (progress >= 1) return null;
        return <AbsoluteFill style={{ backgroundColor: color, transform: `translateY(${transY}px)` }} />;
    }

    if (type === 'iris') {
        const radius = interpolate(progress, [0, 1], [0, Math.max(width, height) * 1.5]);
        if (progress >= 1) return null;

        return (
            <AbsoluteFill style={{ overflow: 'hidden' }}>
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    borderRadius: '50%',
                    boxShadow: `0 0 0 5000px ${color}`,
                    backgroundColor: 'transparent',
                    width: radius,
                    height: radius,
                }} />
            </AbsoluteFill>
        );
    }

    return null;
};
