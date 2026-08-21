import { Platform } from 'react-native';

// Golden Ratio Constant: phi = 1.61803398875
export const PHI = 1.618;

// Golden Ratio Spacing Scale (in px): 5 -> 8 -> 13 -> 21 -> 34 -> 55 -> 89
export const SPACING = {
  xs: 5,
  sm: 8,
  md: 13,
  lg: 21,
  xl: 34,
  xxl: 55,
  xxxl: 89,
};

// Plus Jakarta Sans & System Font Family Tokens
export const FONT_FAMILY = {
  regular: Platform.select({ web: "'Plus Jakarta Sans', system-ui, sans-serif", ios: 'System', android: 'sans-serif' }),
  medium: Platform.select({ web: "'Plus Jakarta Sans', system-ui, sans-serif", ios: 'System', android: 'sans-serif-medium' }),
  semiBold: Platform.select({ web: "'Plus Jakarta Sans', system-ui, sans-serif", ios: 'System', android: 'sans-serif-medium' }),
  bold: Platform.select({ web: "'Plus Jakarta Sans', system-ui, sans-serif", ios: 'System', android: 'sans-serif-bold' }),
};

// Golden Ratio Font Scale (in px): 11 -> 13 -> 16 -> 21 -> 34 -> 55
export const FONTS = {
  caption: 11,
  bodySmall: 13,
  body: 16,
  subheading: 21,
  heading: 34,
  display: 55,
};

// Curated Organic Soothing Palette
export const COLORS = {
  // Brand Color Palette
  sage: '#8FB9A8',            // Primary brand color
  softSky: '#A8DADC',         // Secondary accent
  warmYellow: '#F4D58D',      // Positive highlights (background/accents)
  warmYellowText: '#B45309',  // High-contrast Warm Amber for text on light background
  warmCream: '#FFF9F0',       // Main background
  deepSlate: '#263238',       // Main text
  softGray: '#66757F',        // Secondary text
  deepTeal: '#3F7D73',        // Active / interactive states

  // Theme Mappings
  void: '#FFF9F0',           // Warm Cream background
  voidPure: '#FFF9F0',
  boneWhite: '#263238',       // Deep Slate main text
  ashGray: '#66757F',         // Soft Gray secondary text
  silverMist: '#455A64',
  electricIris: '#3F7D73',     // Active Deep Teal
  electricIrisGlow: 'rgba(63, 125, 115, 0.25)',
  electricIrisDark: '#2C5A53',
  saffronSpark: '#B45309',    // Rich Amber Text Highlight
  deepVerdant: '#8FB9A8',     // Sage

  // UI Surfaces & Inputs
  inputBg: 'rgba(38, 50, 56, 0.04)',
  inputBorder: 'rgba(38, 50, 56, 0.14)',
  cardBg: '#FFFFFF',          // Clean White card surface
  cardBorder: 'rgba(63, 125, 115, 0.16)',
  modalOverlay: 'rgba(38, 50, 56, 0.65)',
  errorRed: '#E63946',
};

export const SHAPES = {
  buttonRadius: Math.round(13 * PHI), // 21px
  inputRadius: Math.round(10 * PHI),  // 16px
  cardRadius: Math.round(21 * PHI),   // 34px
  pillRadius: 9999,
};

export default COLORS;
