import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate, random } from 'remotion';
import { TextEffect, AnimationType } from '../design-engine';

interface Props {
    text: string;
    font: string;
    effect: TextEffect;
    animation: AnimationType; // Entry animation
    color: string;
    style?: React.CSSProperties;
}

export const AnimatedText: React.FC<Props> = ({ text, font, effect, animation, color, style }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const progress = spring({ frame, fps, config: { damping: 100 } });

    // Base Styles
    const baseStyle: React.CSSProperties = {
        fontFamily: font,
        color: color,
        ...style
    };

    // ----- ENTRY ANIMATION (Whole Block) -----
    let containerStyle: React.CSSProperties = { ...baseStyle };
    if (animation === 'fade') {
        containerStyle.opacity = progress;
    } else if (animation === 'slide') {
        containerStyle.transform = `translateY(${interpolate(progress, [0, 1], [100, 0])}px)`;
        containerStyle.opacity = progress;
    } else if (animation === 'zoom') {
        containerStyle.transform = `scale(${interpolate(progress, [0, 1], [0.5, 1])})`;
        containerStyle.opacity = progress;
    } else if (animation === 'bounce') {
        const bounce = spring({ frame, fps, config: { damping: 10, mass: 0.5 } });
        containerStyle.transform = `scale(${interpolate(bounce, [0, 1], [0, 1])})`;
    } else if (animation === 'rotate') {
        containerStyle.transform = `rotate(${interpolate(progress, [0, 1], [-10, 0])}deg) scale(${progress})`;
        containerStyle.opacity = progress;
    }


    // ----- PER-CHARACTER EFFECTS -----

    if (effect === 'typewriter') {
        const chars = text.length;
        const visibleChars = Math.floor(interpolate(frame, [0, chars * 2], [0, chars], { extendRight: true }));
        return <h1 style={containerStyle}>{text.slice(0, visibleChars)}</h1>;
    }

    if (effect === 'stagger') {
        return (
            <h1 style={{ ...containerStyle, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
                {text.split(' ').map((word, i) => {
                    const wordProgress = spring({ frame: frame - i * 5, fps });
                    return (
                        <span key={i} style={{
                            marginRight: '0.3em',
                            opacity: wordProgress,
                            transform: `translateY(${interpolate(wordProgress, [0, 1], [20, 0])}px)`
                        }}>
                            {word}
                        </span>
                    );
                })}
            </h1>
        );
    }

    if (effect === 'blur') {
        const blurAmount = interpolate(progress, [0, 1], [10, 0]);
        return <h1 style={{ ...containerStyle, filter: `blur(${blurAmount}px)` }}>{text}</h1>;
    }

    if (effect === 'glitch') {
        const p = 0.9 + random(frame) * 0.2;
        const skew = (random(frame + 1) - 0.5) * 20;
        return <h1 style={{ ...containerStyle, opacity: p, transform: `${containerStyle.transform || ''} skewX(${skew}deg)` }}>{text}</h1>;
    }

    // Default: None or Wavy?
    return <h1 style={containerStyle}>{text}</h1>;
};
