import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Dimensions } from 'react-native';
import { COLORS } from '../theme/colors';

const { width, height } = Dimensions.get('window');

// Generate 18 ambient floating constellation particles in soothing colors
const PARTICLES = Array.from({ length: 18 }).map((_, i) => ({
  id: i,
  x: Math.random() * width,
  y: Math.random() * height,
  size: Math.random() * 5 + 3,
  color: i % 3 === 0 ? COLORS.sage : i % 2 === 0 ? COLORS.softSky : COLORS.warmYellow,
  duration: 5000 + Math.random() * 6000,
}));

export default function AmbientParticles() {
  const animValues = useRef(PARTICLES.map(() => new Animated.Value(0))).current;

  useEffect(() => {
    const animations = animValues.map((anim, idx) => {
      return Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: 1,
            duration: PARTICLES[idx].duration,
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: 0,
            duration: PARTICLES[idx].duration,
            useNativeDriver: true,
          }),
        ])
      );
    });

    animations.forEach(a => a.start());
  }, [animValues]);

  return (
    <View style={StyleSheet.absoluteFillObject} pointerEvents="none">
      {PARTICLES.map((p, idx) => {
        const translateY = animValues[idx].interpolate({
          inputRange: [0, 1],
          outputRange: [0, -30],
        });
        const opacity = animValues[idx].interpolate({
          inputRange: [0, 0.5, 1],
          outputRange: [0.15, 0.4, 0.15],
        });

        return (
          <Animated.View
            key={p.id}
            style={[
              styles.particle,
              {
                left: p.x,
                top: p.y,
                width: p.size,
                height: p.size,
                borderRadius: p.size / 2,
                backgroundColor: p.color,
                opacity: opacity,
                transform: [{ translateY }],
              },
            ]}
          />
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  particle: {
    position: 'absolute',
  },
});
