import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Easing } from 'react-native';
import Svg, { Defs, LinearGradient, RadialGradient, Stop, Path, G, Polygon } from 'react-native-svg';
import { COLORS } from '../theme/colors';

const AnimatedG = Animated.createAnimatedComponent(G);

export default function Star3DIcon({ size = 80 }) {
  const spinAnim = useRef(new Animated.Value(0)).current;
  const floatAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // 3D Rotation Animation
    const spinLoop = Animated.loop(
      Animated.timing(spinAnim, {
        toValue: 1,
        duration: 7000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );

    // Floating breathing animation
    const floatLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(floatAnim, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        }),
        Animated.timing(floatAnim, {
          toValue: 0,
          duration: 1500,
          useNativeDriver: true,
        }),
      ])
    );

    spinLoop.start();
    floatLoop.start();

    return () => {
      spinLoop.stop();
      floatLoop.stop();
    };
  }, [spinAnim, floatAnim]);

  const rotateY = spinAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const translateY = floatAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -6],
  });

  return (
    <Animated.View
      style={[
        styles.container,
        {
          width: size,
          height: size,
          transform: [{ translateY }],
        },
      ]}
    >
      <Svg width={size} height={size} viewBox="0 0 100 100">
        <Defs>
          {/* 3D Gold / Saffron Facet Gradient */}
          <LinearGradient id="goldFacetLeft" x1="0%" y1="0%" x2="100%" y2="100%">
            <Stop offset="0%" stopColor="#ffffff" stopOpacity="0.9" />
            <Stop offset="50%" stopColor="#ffb829" stopOpacity="1" />
            <Stop offset="100%" stopColor="#d97706" stopOpacity="1" />
          </LinearGradient>

          <LinearGradient id="goldFacetRight" x1="100%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor="#ffb829" stopOpacity="1" />
            <Stop offset="70%" stopColor="#b45309" stopOpacity="1" />
            <Stop offset="100%" stopColor="#78350f" stopOpacity="1" />
          </LinearGradient>

          {/* 3D Core Violet Star Gradient */}
          <RadialGradient id="irisCoreGlow" cx="50%" cy="50%" r="50%">
            <Stop offset="0%" stopColor="#8052ff" stopOpacity="0.8" />
            <Stop offset="100%" stopColor="#000000" stopOpacity="0" />
          </RadialGradient>
        </Defs>

        {/* Ambient Floor Glow */}
        <AnimatedG style={{ opacity: 0.6 }}>
          <Path
            d="M50 5 L61 35 L95 38 L68 60 L76 94 L50 76 L24 94 L32 60 L5 38 L39 35 Z"
            fill="url(#irisCoreGlow)"
            transform="scale(1.15) translate(-6.5, -6.5)"
          />
        </AnimatedG>

        {/* 3D Faceted Star Geometry */}
        <AnimatedG
          origin="50, 50"
          style={{
            transform: [{ rotate: rotateY }],
          }}
        >
          {/* Facet 1 (Top Tip Left) */}
          <Polygon points="50,5 50,50 61,35" fill="url(#goldFacetLeft)" />
          <Polygon points="50,5 50,50 39,35" fill="url(#goldFacetRight)" />

          {/* Facet 2 (Right Tip Top) */}
          <Polygon points="95,38 50,50 61,35" fill="url(#goldFacetRight)" />
          <Polygon points="95,38 50,50 68,60" fill="url(#goldFacetLeft)" />

          {/* Facet 3 (Bottom Right Tip) */}
          <Polygon points="76,94 50,50 68,60" fill="url(#goldFacetRight)" />
          <Polygon points="76,94 50,50 50,76" fill="url(#goldFacetLeft)" />

          {/* Facet 4 (Bottom Left Tip) */}
          <Polygon points="24,94 50,50 50,76" fill="url(#goldFacetRight)" />
          <Polygon points="24,94 50,50 32,60" fill="url(#goldFacetLeft)" />

          {/* Facet 5 (Left Tip Bottom) */}
          <Polygon points="5,38 50,50 32,60" fill="url(#goldFacetRight)" />
          <Polygon points="5,38 50,50 39,35" fill="url(#goldFacetLeft)" />
        </AnimatedG>
      </Svg>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
});
