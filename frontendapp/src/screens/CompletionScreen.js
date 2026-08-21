import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS } from '../theme/colors';
import Star3DIcon from '../components/Star3DIcon';

export default function CompletionScreen({ onResetSession }) {
  return (
    <View style={styles.container}>
      <View style={styles.cardWrapper}>
        {/* 3D Rotating Star Badge */}
        <View style={styles.badgeOrb}>
          <Star3DIcon size={72} />
        </View>

        <Text style={styles.celebrateTitle}>You're all done!</Text>
        <Text style={styles.subText}>
          Thanks for sharing your thoughts. Your responses have been saved and sent to your school.
        </Text>

        {/* Metrics Summary Grid */}
        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricVal}>10</Text>
            <Text style={styles.metricLbl}>Questions Answered</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricVal}>06:45</Text>
            <Text style={styles.metricLbl}>Interview Duration</Text>
          </View>
        </View>

        {/* Close Session CTA */}
        <TouchableOpacity
          style={styles.primaryCta}
          onPress={onResetSession}
          activeOpacity={0.8}
        >
          <Text style={styles.ctaText}>CLOSE SESSION →</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.warmCream,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg, // 21px
  },
  cardWrapper: {
    width: '100%',
    maxWidth: 440,
    alignItems: 'center',
  },
  badgeOrb: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(244, 213, 141, 0.25)',
    borderWidth: 1,
    borderColor: COLORS.warmYellow,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.xl, // 34px
    shadowColor: COLORS.warmYellow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: SPACING.md, // 13px
  },
  celebrateTitle: {
    color: COLORS.deepSlate,
    fontSize: FONTS.heading, // 34px
    fontWeight: '400',
    marginBottom: SPACING.md, // 13px
  },
  subText: {
    color: COLORS.softGray,
    fontSize: FONTS.body, // 16px
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: SPACING.xl, // 34px
  },
  metricsRow: {
    flexDirection: 'row',
    gap: SPACING.md, // 13px
    width: '100%',
    marginBottom: SPACING.xl, // 34px
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: SHAPES.buttonRadius, // 21px
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.16)',
    padding: SPACING.lg, // 21px
    alignItems: 'center',
  },
  metricVal: {
    color: COLORS.deepTeal,
    fontSize: 28,
    fontWeight: '700',
    marginBottom: SPACING.xs, // 5px
  },
  metricLbl: {
    color: COLORS.softGray,
    fontSize: FONTS.caption, // 11px
    fontWeight: '500',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  primaryCta: {
    width: '100%',
    height: 55, // Golden Ratio size (55px)
    backgroundColor: COLORS.deepTeal,
    borderRadius: SHAPES.buttonRadius, // 21px
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.deepTeal,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: SPACING.md, // 13px
  },
  ctaText: {
    color: '#FFFFFF',
    fontSize: FONTS.body, // 16px
    fontWeight: '600',
    letterSpacing: 1.0,
  },
});
