import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS } from '../theme/colors';

export default function ProgressTracker({ sectionName = 'Section B · Teaching Style & Comprehension', currentStep = 6, totalSteps = 10 }) {
  const percentage = Math.min(Math.max((currentStep / totalSteps) * 100, 0), 100);

  return (
    <View style={styles.trackerContainer}>
      <View style={styles.headerRow}>
        <Text style={styles.sectionLabel} numberOfLines={1}>{sectionName.toUpperCase()}</Text>
        <Text style={styles.stepText}>{currentStep} / {totalSteps}</Text>
      </View>

      <View style={styles.trackBackground}>
        <View style={[styles.trackFill, { width: `${percentage}%` }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  trackerContainer: {
    width: '100%',
    maxWidth: 440,
    marginVertical: SPACING.sm, // 8px
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.xs, // 5px
  },
  sectionLabel: {
    color: COLORS.warmYellowText, // High-contrast Warm Amber (#B45309) on light background
    fontSize: FONTS.caption, // 11px
    fontWeight: '700',
    letterSpacing: 1.2,
    flexShrink: 1,
    marginRight: SPACING.sm,
  },
  stepText: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '600',
  },
  trackBackground: {
    width: '100%',
    height: 5,
    backgroundColor: 'rgba(38, 50, 56, 0.1)',
    borderRadius: SHAPES.pillRadius,
    overflow: 'hidden',
  },
  trackFill: {
    height: '100%',
    backgroundColor: COLORS.deepTeal,
    borderRadius: SHAPES.pillRadius,
  },
});
