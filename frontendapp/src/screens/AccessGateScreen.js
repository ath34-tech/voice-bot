import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS, FONT_FAMILY } from '../theme/colors';

export default function AccessGateScreen({ onSubmitAccess }) {
  const [schoolCode, setSchoolCode] = useState('SCH-804');
  const [studentId, setStudentId] = useState('STU-1029');
  const [name, setName] = useState('Alex');
  const [grade, setGrade] = useState('Grade 8');
  
  const [focusedInput, setFocusedInput] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleStart = async () => {
    if (!schoolCode.trim()) {
      setErrorMsg('Please enter your school code.');
      return;
    }
    if (!studentId.trim()) {
      setErrorMsg('Please enter your student ID.');
      return;
    }

    setErrorMsg('');
    setIsLoading(true);

    try {
      await onSubmitAccess({
        schoolCode: schoolCode.trim().toUpperCase(),
        studentId: studentId.trim().toUpperCase(),
        name: name.trim() || 'Student',
        grade,
      });
    } catch (err) {
      setErrorMsg(err.message || 'Unable to connect. Check your internet connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.cardWrapper}>
        <Text style={styles.appBadge}>BODH</Text>
        <Text style={styles.mainTitle}>Ready to talk?</Text>
        <Text style={styles.subTitle}>
          Enter the details provided by your school.{'\n'}No account or password is needed.
        </Text>

        {errorMsg ? <Text style={styles.errorBanner}>{errorMsg}</Text> : null}

        {/* School Code Input */}
        <View style={styles.fieldGroup}>
          <Text style={styles.inputLabel}>SCHOOL CODE</Text>
          <TextInput
            style={[
              styles.textInput,
              focusedInput === 'schoolCode' && styles.focusedInput,
            ]}
            placeholder="SCH-804"
            placeholderTextColor={COLORS.softGray}
            value={schoolCode}
            onChangeText={setSchoolCode}
            onFocus={() => setFocusedInput('schoolCode')}
            onBlur={() => setFocusedInput(null)}
            autoCapitalize="characters"
          />
        </View>

        {/* Student ID Input */}
        <View style={styles.fieldGroup}>
          <Text style={styles.inputLabel}>STUDENT ID</Text>
          <TextInput
            style={[
              styles.textInput,
              focusedInput === 'studentId' && styles.focusedInput,
            ]}
            placeholder="STU-1029"
            placeholderTextColor={COLORS.softGray}
            value={studentId}
            onChangeText={setStudentId}
            onFocus={() => setFocusedInput('studentId')}
            onBlur={() => setFocusedInput(null)}
            autoCapitalize="characters"
          />
        </View>

        {/* Student Name Input (Optional) */}
        <View style={styles.fieldGroup}>
          <Text style={styles.inputLabel}>YOUR NAME (OPTIONAL)</Text>
          <TextInput
            style={[
              styles.textInput,
              focusedInput === 'name' && styles.focusedInput,
            ]}
            placeholder="Alex"
            placeholderTextColor={COLORS.softGray}
            value={name}
            onChangeText={setName}
            onFocus={() => setFocusedInput('name')}
            onBlur={() => setFocusedInput(null)}
          />
        </View>

        {/* Grade Selection */}
        <View style={styles.fieldGroup}>
          <Text style={styles.inputLabel}>GRADE / CLASS</Text>
          <View style={styles.gradeToggleRow}>
            {['Grade 7', 'Grade 8'].map((g) => (
              <TouchableOpacity
                key={g}
                style={[
                  styles.gradeChip,
                  grade === g && styles.gradeChipActive,
                ]}
                onPress={() => setGrade(g)}
                activeOpacity={0.75}
              >
                <Text
                  style={[
                    styles.gradeChipText,
                    grade === g && styles.gradeChipTextActive,
                  ]}
                >
                  {g}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Primary CTA */}
        <TouchableOpacity
          style={[styles.primaryCta, isLoading && styles.disabledCta]}
          onPress={handleStart}
          disabled={isLoading}
          activeOpacity={0.8}
        >
          {isLoading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.ctaText}>START VOICE SURVEY →</Text>
          )}
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
  appBadge: {
    color: COLORS.deepTeal,
    fontSize: FONTS.caption, // 11px
    fontWeight: '700',
    letterSpacing: 1.618,
    marginBottom: SPACING.sm, // 8px
  },
  mainTitle: {
    color: COLORS.deepSlate,
    fontSize: FONTS.heading, // 34px
    fontWeight: '400',
    marginBottom: SPACING.xs, // 5px
  },
  subTitle: {
    color: COLORS.softGray,
    fontSize: FONTS.body, // 16px
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: SPACING.xl, // 34px
  },
  errorBanner: {
    color: COLORS.errorRed,
    fontSize: FONTS.bodySmall, // 13px
    marginBottom: SPACING.md, // 13px
    textAlign: 'center',
  },
  fieldGroup: {
    width: '100%',
    marginBottom: SPACING.lg, // 21px
  },
  inputLabel: {
    color: COLORS.deepSlate,
    fontSize: FONTS.caption, // 11px
    fontWeight: '600',
    letterSpacing: 1.0,
    marginBottom: SPACING.sm, // 8px
  },
  textInput: {
    width: '100%',
    height: 55, // Golden Ratio height
    backgroundColor: '#FFFFFF',
    borderRadius: SHAPES.inputRadius, // 16px
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.2)',
    color: COLORS.deepSlate,
    paddingHorizontal: SPACING.lg, // 21px
    fontSize: FONTS.body, // 16px
  },
  focusedInput: {
    borderColor: COLORS.deepTeal,
    backgroundColor: '#FFFFFF',
    shadowColor: COLORS.deepTeal,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
  },
  gradeToggleRow: {
    flexDirection: 'row',
    gap: SPACING.md, // 13px
  },
  gradeChip: {
    flex: 1,
    height: 48,
    borderRadius: SHAPES.inputRadius, // 16px
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  gradeChipActive: {
    backgroundColor: 'rgba(143, 185, 168, 0.25)',
    borderColor: COLORS.deepTeal,
  },
  gradeChipText: {
    color: COLORS.softGray,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '500',
  },
  gradeChipTextActive: {
    color: COLORS.deepSlate,
    fontWeight: '700',
  },
  primaryCta: {
    width: '100%',
    height: 55, // Golden Ratio height (55px)
    backgroundColor: COLORS.deepTeal,
    borderRadius: SHAPES.buttonRadius, // 21px
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: SPACING.md, // 13px
    shadowColor: COLORS.deepTeal,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: SPACING.md, // 13px
  },
  disabledCta: {
    opacity: 0.6,
  },
  ctaText: {
    color: '#FFFFFF',
    fontSize: FONTS.body, // 16px
    fontWeight: '600',
    letterSpacing: 1.0,
  },
});
