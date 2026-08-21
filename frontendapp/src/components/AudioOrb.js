import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Defs, RadialGradient, Stop, Circle, Line, Polygon } from 'react-native-svg';
import { COLORS } from '../theme/colors';

// Build a 3D Hexagonal Prism (Top Hexagon Ring + Bottom Hexagon Ring)
const RADIUS = 45;
const HALF_HEIGHT = 30;

const HEXAGON_3D_NODES = [];

// Top Hexagon Ring (6 vertices)
for (let i = 0; i < 6; i++) {
  const angle = (i * 60 * Math.PI) / 180;
  HEXAGON_3D_NODES.push({
    x: RADIUS * Math.cos(angle),
    y: -HALF_HEIGHT,
    z: RADIUS * Math.sin(angle),
  });
}

// Bottom Hexagon Ring (6 vertices)
for (let i = 0; i < 6; i++) {
  const angle = (i * 60 * Math.PI) / 180;
  HEXAGON_3D_NODES.push({
    x: RADIUS * Math.cos(angle),
    y: HALF_HEIGHT,
    z: RADIUS * Math.sin(angle),
  });
}

// Center Core Node
HEXAGON_3D_NODES.push({ x: 0, y: 0, z: 0 });

// Connect 3D Hexagonal Edges
const HEXAGON_EDGES = [
  // Top ring
  [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0],
  // Bottom ring
  [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 6],
  // Vertical pillars
  [0, 6], [1, 7], [2, 8], [3, 9], [4, 10], [5, 11],
  // Core star connections
  [0, 12], [2, 12], [4, 12], [7, 12], [9, 12], [11, 12]
];

export default function AudioOrb({ state = 'idle', isBargeIn = false, audioLevel = 0 }) {
  const [angle, setAngle] = useState(0);
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Frame-by-frame 3D Y-Axis Rotation
  useEffect(() => {
    let animationFrameId;
    let lastTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const delta = now - lastTime;
      lastTime = now;
      setAngle((prev) => (prev + delta * 0.035) % 360);
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // Smooth breathing pulse
  useEffect(() => {
    let pulseLoop;
    if (state === 'ai_speaking') {
      pulseLoop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.05 + audioLevel * 0.05,
            duration: 850,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0.96,
            duration: 850,
            useNativeDriver: true,
          }),
        ])
      );
      pulseLoop.start();
    } else {
      pulseLoop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.03,
            duration: 2600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0.97,
            duration: 2600,
            useNativeDriver: true,
          }),
        ])
      );
      pulseLoop.start();
    }

    return () => {
      if (pulseLoop) pulseLoop.stop();
    };
  }, [state, audioLevel, pulseAnim]);

  // Compute 3D Rotated Coordinates
  const rad = (angle * Math.PI) / 180;
  const cosA = Math.cos(rad);
  const sinA = Math.sin(rad);

  const rotatedNodes = HEXAGON_3D_NODES.map((node) => {
    const rx = node.x * cosA - node.z * sinA;
    const rz = node.x * sinA + node.z * cosA;
    const ry = node.y;
    return { x: rx, y: ry, z: rz };
  });

  const getThemeColor = () => {
    if (isBargeIn) return COLORS.warmYellowText;
    if (state === 'user_speaking') return COLORS.sage;
    return COLORS.deepTeal;
  };

  const themeColor = getThemeColor();

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.orbWrapper,
          {
            transform: [{ scale: pulseAnim }],
          },
        ]}
      >
        <Svg width={160} height={160} viewBox="0 0 160 160">
          <Defs>
            {/* Core Glow */}
            <RadialGradient id="hexCore" cx="50%" cy="50%" r="50%">
              <Stop offset="0%" stopColor={themeColor} stopOpacity="0.4" />
              <Stop offset="70%" stopColor={themeColor} stopOpacity="0.08" />
              <Stop offset="100%" stopColor="#FFF9F0" stopOpacity="0" />
            </RadialGradient>
          </Defs>

          {/* Core Soft Ambient Light */}
          <Circle cx="80" cy="80" r="50" fill="url(#hexCore)" />

          {/* Render 3D Hexagonal Wireframe Edges */}
          {HEXAGON_EDGES.map(([i, j], idx) => {
            const p1 = rotatedNodes[i];
            const p2 = rotatedNodes[j];
            const x1 = 80 + p1.x;
            const y1 = 80 + p1.y;
            const x2 = 80 + p2.x;
            const y2 = 80 + p2.y;
            const avgZ = (p1.z + p2.z) / 2;
            const opacity = Math.max(0.15, 0.3 + ((avgZ + RADIUS) / (2 * RADIUS)) * 0.65);

            return (
              <Line
                key={idx}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={themeColor}
                strokeWidth={p1.z > 0 && p2.z > 0 ? 1.8 : 1.1}
                strokeOpacity={opacity}
              />
            );
          })}

          {/* Render 3D Hexagonal Vertices */}
          {rotatedNodes.map((node, idx) => {
            const cx = 80 + node.x;
            const cy = 80 + node.y;
            const radius = Math.max(2.0, 2.6 + ((node.z + RADIUS) / (2 * RADIUS)) * 2.2);
            const opacity = Math.max(0.3, 0.45 + ((node.z + RADIUS) / (2 * RADIUS)) * 0.55);
            const isFront = node.z > 10;

            return (
              <Circle
                key={idx}
                cx={cx}
                cy={cy}
                r={radius}
                fill={isFront ? COLORS.deepSlate : themeColor}
                opacity={opacity}
              />
            );
          })}
        </Svg>
      </Animated.View>

      {/* Floating Badge */}
      <View style={styles.badgeContainer}>
        <Text style={styles.badgeText}>
          {isBargeIn
            ? 'Listening...'
            : state === 'ai_speaking'
            ? 'Speaking...'
            : state === 'user_speaking'
            ? 'Listening to you...'
            : "I'm listening."}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 190,
    width: 190,
    marginVertical: 12,
  },
  orbWrapper: {
    width: 160,
    height: 160,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeContainer: {
    position: 'absolute',
    bottom: 0,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.25)',
    shadowColor: COLORS.deepSlate,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  badgeText: {
    color: COLORS.deepSlate,
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.3,
  },
});
