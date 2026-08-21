import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS, FONT_FAMILY } from '../theme/colors';
import AudioOrb from '../components/AudioOrb';
import AudioLevelMeter from '../components/AudioLevelMeter';
import { useMicrophone } from '../hooks/useMicrophone';

export default function MicCheckScreen({ onProceedToInterview }) {
  const {
    permissionStatus,
    audioLevel,
    hasAudioInput,
    errorMsg,
    requestPermission,
  } = useMicrophone();

  // Automatically request microphone permission on screen mount
  useEffect(() => {
    requestPermission();
  }, [requestPermission]);

  return (
    <View style={styles.container}>
      <View style={styles.contentCard}>
        <Text style={styles.sectionBadge}>STEP 2 · AUDIO TEST</Text>
        <Text style={styles.mainHeading}>One quick check.</Text>
        <Text style={styles.subHeading}>Let's make sure we can hear you.</Text>

        {/* Central Audio Orb (Reacting to Real Microphone Amplitude) */}
        <AudioOrb
          state={permissionStatus === 'granted' ? 'user_speaking' : 'idle'}
          audioLevel={audioLevel}
        />

        {/* Real Audio Level Meter */}
        <AudioLevelMeter
          audioDetected={hasAudioInput || permissionStatus === 'granted'}
          level={audioLevel}
        />

        {/* Error / Permission Blocked Message */}
        {permissionStatus === 'denied' || errorMsg ? (
          <View style={styles.permissionBlockedCard}>
            <Text style={styles.blockedTitle}>Microphone Access Blocked</Text>
            <Text style={styles.blockedText}>
              {errorMsg || 'Please allow microphone access in your browser settings to continue with your voice survey.'}
            </Text>
            <TouchableOpacity
              style={styles.retryPermissionBtn}
              onPress={requestPermission}
              activeOpacity={0.8}
            >
              <Text style={styles.retryBtnText}>ALLOW MICROPHONE ACCESS</Text>
            </TouchableOpacity>
          </View>
        ) : null}

        {/* Primary CTA */}
        {permissionStatus === 'granted' && (
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={onProceedToInterview}
            activeOpacity={0.8}
          >
            <Text style={styles.ctaText}>JOIN INTERVIEW →</Text>
          </TouchableOpacity>
        )}

        {permissionStatus === 'undetermined' && (
          <View style={styles.requestingBox}>
            <ActivityIndicator color={COLORS.deepTeal} style={{ marginBottom: 8 }} />
            <Text style={styles.requestingText}>Requesting microphone permission...</Text>
          </View>
        )}
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
  contentCard: {
    width: '100%',
    maxWidth: 480,
    alignItems: 'center',
  },
  sectionBadge: {
    color: COLORS.deepTeal,
    fontSize: FONTS.caption, // 11px
    fontWeight: '700',
    letterSpacing: 1.618,
    marginBottom: SPACING.sm, // 8px
  },
  mainHeading: {
    color: COLORS.deepSlate,
    fontSize: FONTS.heading, // 34px
    fontWeight: '400',
    marginBottom: SPACING.xs, // 5px
    fontFamily: FONT_FAMILY.medium,
  },
  subHeading: {
    color: COLORS.softGray,
    fontSize: FONTS.body, // 16px
    textAlign: 'center',
    marginBottom: SPACING.md, // 13px
    fontFamily: FONT_FAMILY.regular,
  },
  permissionBlockedCard: {
    width: '100%',
    backgroundColor: 'rgba(230, 57, 70, 0.08)',
    borderRadius: SHAPES.inputRadius,
    borderWidth: 1,
    borderColor: 'rgba(230, 57, 70, 0.3)',
    padding: SPACING.md,
    marginVertical: SPACING.md,
    alignItems: 'center',
  },
  blockedTitle: {
    color: COLORS.errorRed,
    fontSize: FONTS.bodySmall,
    fontWeight: '700',
    marginBottom: 4,
  },
  blockedText: {
    color: COLORS.deepSlate,
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 18,
    marginBottom: 12,
  },
  retryPermissionBtn: {
    backgroundColor: COLORS.errorRed,
    paddingHorizontal: SPACING.lg,
    paddingVertical: 10,
    borderRadius: SHAPES.buttonRadius,
  },
  retryBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  requestingBox: {
    alignItems: 'center',
    marginVertical: SPACING.md,
  },
  requestingText: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall,
  },
  primaryCta: {
    width: '100%',
    height: 55, // Golden Ratio height
    backgroundColor: COLORS.deepTeal,
    borderRadius: SHAPES.buttonRadius, // 21px
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: SPACING.lg, // 21px
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
    fontFamily: FONT_FAMILY.semiBold,
  },
});
