import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS, FONT_FAMILY } from '../theme/colors';

export default function TranscriptBox({ aiQuestion, studentSpeech, statusState }) {
  return (
    <View style={styles.transcriptCard}>
      {/* AI Question */}
      <Text style={styles.aiQuestionText}>
        {aiQuestion || 'Connecting to your AI interviewer...'}
      </Text>

      {/* Live Student Speech (Nested Inline Text Paragraph) */}
      {studentSpeech ? (
        <View style={styles.studentSpeechWrapper}>
          <Text style={styles.studentSpeechParagraph}>
            <Text style={styles.studentLabel}>You: </Text>
            {studentSpeech}
          </Text>
        </View>
      ) : statusState === 'thinking' ? (
        <Text style={styles.statusHint}>Thinking...</Text>
      ) : statusState === 'listening' ? (
        <Text style={styles.statusHint}>Listening...</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  transcriptCard: {
    width: '100%',
    maxWidth: 440,
    backgroundColor: '#FFFFFF',
    borderRadius: SHAPES.cardRadius, // 34px
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.16)',
    padding: SPACING.lg, // 21px
    marginVertical: SPACING.md, // 13px
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.deepSlate,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: SPACING.md, // 13px
  },
  aiQuestionText: {
    color: COLORS.deepSlate,
    fontSize: FONTS.subheading, // 21px
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 30,
    marginBottom: SPACING.sm, // 8px
    fontFamily: FONT_FAMILY.medium,
  },
  studentSpeechWrapper: {
    width: '100%',
    marginTop: SPACING.xs, // 5px
    paddingTop: SPACING.sm, // 8px
    borderTopWidth: 1,
    borderTopColor: 'rgba(38, 50, 56, 0.08)',
  },
  studentSpeechParagraph: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '400',
    lineHeight: 20,
    textAlign: 'left',
    fontFamily: FONT_FAMILY.regular,
  },
  studentLabel: {
    color: COLORS.deepTeal,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '800',
    fontFamily: FONT_FAMILY.bold,
  },
  statusHint: {
    color: COLORS.deepTeal,
    fontSize: FONTS.bodySmall, // 13px
    fontStyle: 'italic',
    marginTop: SPACING.xs, // 5px
    fontFamily: FONT_FAMILY.medium,
  },
});
