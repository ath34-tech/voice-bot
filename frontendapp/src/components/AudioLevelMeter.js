import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '../theme/colors';

export default function AudioLevelMeter({ audioDetected = false, level = 0.6 }) {
  // Render 10 volume bar segments
  const segments = Array.from({ length: 10 }).map((_, i) => i / 10);

  return (
    <View style={styles.meterWrapper}>
      <Text style={styles.meterStatus}>
        {audioDetected ? 'Microphone detected' : "Speak normally... testing mic"}
      </Text>

      <View style={styles.barContainer}>
        {segments.map((seg, idx) => {
          const isActive = audioDetected && level >= seg;
          return (
            <View
              key={idx}
              style={[
                styles.segmentBar,
                {
                  backgroundColor: isActive
                    ? idx > 7
                      ? COLORS.saffronSpark
                      : COLORS.electricIris
                    : 'rgba(255, 255, 255, 0.1)',
                },
              ]}
            />
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  meterWrapper: {
    alignItems: 'center',
    marginVertical: 20,
  },
  meterStatus: {
    color: COLORS.ashGray,
    fontSize: 14,
    marginBottom: 12,
  },
  barContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
  },
  segmentBar: {
    width: 8,
    height: 28,
    borderRadius: 4,
  },
});
