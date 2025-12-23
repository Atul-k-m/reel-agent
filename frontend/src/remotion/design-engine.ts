import { random } from "remotion";

// ==================== 1. FONTS (5 per style) ====================
export const FONT_MAPPING: Record<string, string[]> = {
    "Bold": ["Oswald", "Impact", "Anton", "Bebas Neue", "Fjalla One"],
    "Minimal": ["Inter", "Roboto", "Lato", "Montserrat", "Open Sans"],
    "Glitch": ["VT323", "Share Tech Mono", "Rubik Glitch", "Source Code Pro", "Press Start 2P"],
    "Retro": ["Press Start 2P", "Pacifico", "Righteous", "Audiowide", "Monoton"],
    "Swiss": ["Arial", "Inter", "Roboto", "Poppins", "Raleway"],
    "Neon": ["Iceberg", "Orbitron", "Audiowide", "Monoton", "Righteous"],
    "Kinetic": ["Oswald", "Anton", "Roboto", "Montserrat", "Poppins"],
    // Fallback
    "Bauhaus": ["Arial", "Oswald", "Inter", "Roboto", "Poppins"],
};

export const getFont = (styleId: string, seed: number) => {
    const fonts = FONT_MAPPING[styleId] || FONT_MAPPING["Bold"];
    return fonts[Math.floor(random(seed) * fonts.length)];
};

// ==================== 2. ANIMATIONS (5 Types) ====================
export type AnimationType = "fade" | "slide" | "zoom" | "bounce" | "rotate";

export const getAnimation = (seed: number): AnimationType => {
    const types: AnimationType[] = ["fade", "slide", "zoom", "bounce", "rotate"];
    return types[Math.floor(random(seed + 100) * types.length)];
};

// ==================== 3. TEXT EFFECTS (5 Types) ====================
export type TextEffect = "none" | "typewriter" | "stagger" | "blur" | "glitch";

export const getTextEffect = (seed: number): TextEffect => {
    const types: TextEffect[] = ["none", "typewriter", "stagger", "blur", "glitch"];
    // Give "none" a lower probability if desired, but here uniform
    return types[Math.floor(random(seed + 200) * types.length)];
};

// ==================== 4. TRANSITIONS (5 Types) ====================
export type TransitionType = "none" | "wipe" | "dissolve" | "push" | "iris";

export const getTransition = (seed: number): TransitionType => {
    const types: TransitionType[] = ["none", "wipe", "dissolve", "push", "iris"];
    return types[Math.floor(random(seed + 300) * types.length)];
};

// ==================== 5. BACKGROUND ELEMENTS ====================
export type BackgroundType = "solid" | "gradient" | "grid" | "particles" | "shapes";

export const getBackground = (seed: number): BackgroundType => {
    const types: BackgroundType[] = ["solid", "gradient", "grid", "particles", "shapes"];
    return types[Math.floor(random(seed + 400) * types.length)];
};

//Helper Config Object
export interface DesignConfig {
    font: string;
    animation: AnimationType;
    textEffect: TextEffect;
    transition: TransitionType;
    background: BackgroundType;
    colors: string[];
}

export const getDesignConfig = (styleId: string, seed: number): DesignConfig => {
    return {
        font: getFont(styleId, seed),
        animation: getAnimation(seed),
        textEffect: getTextEffect(seed),
        transition: getTransition(seed),
        background: getBackground(seed),
        colors: getRandomPalette(styleId, seed)
    }
};

const PALETTES: Record<string, string[][]> = {
    "Bold": [["#000", "#FFF", "#F00"], ["#111", "#FFD700", "#FFF"]],
    "Minimal": [["#FFF", "#000"], ["#F5F5F5", "#333"]],
    "Glitch": [["#000", "#0F0", "#F0F"], ["#111", "#0FF", "#F00"]],
    "Retro": [["#2b002b", "#0FF", "#F0F"], ["#000033", "#D4AF37", "#FF0099"]],
    // Add more as needed
};

const getRandomPalette = (styleId: string, seed: number): string[] => {
    const palettes = PALETTES[styleId] || [["#000", "#FFF"]];
    return palettes[Math.floor(random(seed + 500) * palettes.length)];
};
