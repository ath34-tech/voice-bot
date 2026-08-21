import React from 'react';
import { View, Text, TouchableOpacity, Modal, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS } from '../theme/colors';

export default function EndSurveyModal({ visible, onContinue, onConfirmEnd }) {
  if (!visible) return null;

  return (
    <Modal transparent animationType="fade" visible={visible}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalCard}>
          <Text style={styles.modalTitle}>End the survey?</Text>
          <Text style={styles.modalCopy}>
            Your answers so far will be saved and submitted to your school.
          </Text>

          <View style={styles.buttonCol}>
            <TouchableOpacity
              style={styles.primaryContinueBtn}
              onPress={onContinue}
              activeOpacity={0.8}
            >
              <Text style={styles.primaryBtnText}>Continue Survey</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryEndBtn}
              onPress={onConfirmEnd}
              activeOpacity={0.8}
            >
              <Text style={styles.secondaryBtnText}>End Survey</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: COLORS.modalOverlay,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg, // 21px
  },
  modalCard: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: COLORS.warmCream,
    borderRadius: SHAPES.cardRadius, // 34px
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.2)',
    padding: SPACING.xl, // 34px
    alignItems: 'center',
    shadowColor: COLORS.deepSlate,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: SPACING.xl, // 34px
  },
  modalTitle: {
    color: COLORS.deepSlate,
    fontSize: FONTS.subheading, // 21px
    fontWeight: '600',
    marginBottom: SPACING.md, // 13px
  },
  modalCopy: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    textAlign: 'center',
    lineHeight: 21,
    marginBottom: SPACING.xl, // 34px
  },
  buttonCol: {
    width: '100%',
    gap: SPACING.md, // 13px
  },
  primaryContinueBtn: {
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
  primaryBtnText: {
    color: '#FFFFFF',
    fontSize: FONTS.body, // 16px
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  secondaryEndBtn: {
    width: '100%',
    height: 48,
    backgroundColor: 'transparent',
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryBtnText: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '500',
  },
});
