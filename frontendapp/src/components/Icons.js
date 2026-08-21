import React from 'react';
import Svg, { Path, Line, Rect } from 'react-native-svg';
import { COLORS } from '../theme/colors';

export function MicIcon({ size = 20, color = COLORS.boneWhite }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <Path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
      <Path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <Line x1="12" y1="19" x2="12" y2="22" />
    </Svg>
  );
}

export function MicOffIcon({ size = 20, color = COLORS.errorRed }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <Line x1="1" y1="1" x2="23" y2="23" />
      <Path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V5a3 3 0 0 0-5.94-.6" />
      <Path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
      <Line x1="12" y1="19" x2="12" y2="22" />
    </Svg>
  );
}

export function VolumeIcon({ size = 20, color = COLORS.deepTeal, isBold = false }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={isBold ? "3" : "2.2"} strokeLinecap="round" strokeLinejoin="round">
      <Path d="M11 5L6 9H2V15H6L11 19V5Z" fill={isBold ? color : "none"} />
      <Path d="M15.54 8.46a5 5 0 0 1 0 7.07" strokeWidth={isBold ? "3.2" : "2.2"} />
      <Path d="M19.07 4.93a10 10 0 0 1 0 14.14" strokeWidth={isBold ? "3.2" : "2.2"} />
    </Svg>
  );
}

export function VolumeMutedIcon({ size = 20, color = COLORS.softGray }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <Line x1="1" y1="1" x2="23" y2="23" />
      <Path d="M11 5L6 9H2V15H6L11 19V5Z" />
      <Line x1="23" y1="9" x2="17" y2="15" />
      <Line x1="17" y1="9" x2="23" y2="15" />
    </Svg>
  );
}

export function EndCallIcon({ size = 18, color = COLORS.ashGray }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <Rect x="4" y="4" width="16" height="16" rx="3" fill={color} opacity="0.2" />
      <Path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a1 1 0 0 1 1.05-.24 11.64 11.64 0 0 0 3.58.57 1 1 0 0 1 1 1V19a1 1 0 0 1-1 1 17 17 0 0 1-15-15 1 1 0 0 1 1-1h3a1 1 0 0 1 1 1 11.64 11.64 0 0 0 .57 3.58 1 1 0 0 1-.25 1.07l-1.26 1.26" />
    </Svg>
  );
}
