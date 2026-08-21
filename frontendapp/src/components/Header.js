import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS, FONT_FAMILY } from '../theme/colors';

export default function Header({ connectionState = 'Connected', studentName }) {
  const getStatusColor = () => {
    switch (connectionState.toLowerCase()) {
      case 'connected':
        return COLORS.deepTeal;
      case 'connecting':
        return COLORS.warmYellow;
      case 'offline':
        return COLORS.errorRed;
      default:
        return COLORS.softGray;
    }
  };

  return (
    <View style={styles.headerContainer}>
      <View style={styles.brandRow}>
        {/* Product Brand Icon PNG */}
        <Image
          source={require('../../assets/icon.png')}
          style={styles.brandIconImage}
          resizeMode="contain"
        />
        <Text style={styles.brandText}>Bodh</Text>
      </View>

      <View style={styles.statusRow}>
        {studentName ? (
          <Text style={styles.studentBadge}>{studentName}</Text>
        ) : null}
        <View style={styles.statusPill}>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
          <Text style={styles.statusText}>{connectionState}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  headerContainer: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg, // 21px
    paddingVertical: SPACING.md, // 13px
    backgroundColor: COLORS.warmCream,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(38, 50, 56, 0.08)',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  brandIconImage: {
    width: 26,
    height: 26,
    borderRadius: 6,
    marginRight: SPACING.sm, // 8px
  },
  brandText: {
    color: COLORS.deepSlate,
    fontSize: FONTS.body, // 16px
    fontWeight: '700',
    letterSpacing: 0.5,
    fontFamily: FONT_FAMILY.semiBold,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  studentBadge: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    marginRight: SPACING.md, // 13px
    fontWeight: '400',
    fontFamily: FONT_FAMILY.regular,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: SPACING.md, // 13px
    paddingVertical: SPACING.xs, // 5px
    borderRadius: SHAPES.pillRadius,
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.2)',
  },
  statusDot: {
    width: SPACING.sm, // 8px
    height: SPACING.sm, // 8px
    borderRadius: SPACING.sm / 2,
    marginRight: SPACING.sm, // 8px
  },
  statusText: {
    color: COLORS.deepSlate,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '500',
    fontFamily: FONT_FAMILY.medium,
  },
});
