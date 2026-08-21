import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { COLORS, SHAPES, SPACING, FONTS } from '../theme/colors';
import { MicIcon, MicOffIcon, VolumeIcon, VolumeMutedIcon, EndCallIcon } from './Icons';

export default function ControlDock({ isMuted = false, onToggleMute, onToggleVolume, onEndSurvey }) {
  const [isVolumeActive, setIsVolumeActive] = useState(true);

  const handleVolumePress = () => {
    setIsVolumeActive(!isVolumeActive);
    if (onToggleVolume) {
      onToggleVolume(!isVolumeActive);
    }
  };

  return (
    <View style={styles.dockWrapper}>
      {/* Mic Button */}
      <TouchableOpacity
        style={[styles.iconCircleBtn, isMuted ? styles.mutedCircleBtn : styles.activeMicBtn]}
        onPress={onToggleMute}
        activeOpacity={0.8}
      >
        {isMuted ? (
          <MicOffIcon size={20} color={COLORS.errorRed} />
        ) : (
          <MicIcon size={20} color="#FFFFFF" />
        )}
      </TouchableOpacity>

      {/* Speaker / Volume Button (Bold Active State) */}
      <TouchableOpacity
        style={[styles.iconCircleBtn, isVolumeActive ? styles.activeVolumeBtn : styles.inactiveVolumeBtn]}
        onPress={handleVolumePress}
        activeOpacity={0.8}
      >
        {isVolumeActive ? (
          <VolumeIcon size={20} color="#FFFFFF" isBold={true} />
        ) : (
          <VolumeMutedIcon size={20} color={COLORS.softGray} />
        )}
      </TouchableOpacity>

      {/* End Survey Button */}
      <TouchableOpacity
        style={styles.endPillBtn}
        onPress={onEndSurvey}
        activeOpacity={0.8}
      >
        <EndCallIcon size={16} color={COLORS.softGray} />
        <Text style={styles.endBtnText}>End</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  dockWrapper: {
    width: '100%',
    maxWidth: 320,
    height: 56,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: SPACING.md, // 13px
    backgroundColor: '#FFFFFF',
    borderRadius: SHAPES.pillRadius,
    borderWidth: 1,
    borderColor: 'rgba(63, 125, 115, 0.2)',
    marginVertical: SPACING.md, // 13px
    shadowColor: COLORS.deepSlate,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: SPACING.md, // 13px
  },
  iconCircleBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
  },
  activeMicBtn: {
    backgroundColor: COLORS.deepTeal,
    borderColor: COLORS.deepTeal,
    shadowColor: COLORS.deepTeal,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  mutedCircleBtn: {
    backgroundColor: 'rgba(230, 57, 70, 0.12)',
    borderColor: 'rgba(230, 57, 70, 0.35)',
  },
  activeVolumeBtn: {
    backgroundColor: COLORS.deepTeal,
    borderColor: COLORS.deepTeal,
    shadowColor: COLORS.deepTeal,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  inactiveVolumeBtn: {
    backgroundColor: 'rgba(38, 50, 56, 0.05)',
    borderColor: 'rgba(38, 50, 56, 0.12)',
  },
  endPillBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 42,
    paddingHorizontal: SPACING.lg, // 21px
    borderRadius: SHAPES.pillRadius,
    backgroundColor: 'rgba(38, 50, 56, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(38, 50, 56, 0.12)',
    gap: SPACING.sm, // 8px
  },
  endBtnText: {
    color: COLORS.deepSlate,
    fontSize: FONTS.bodySmall, // 13px
    fontWeight: '600',
    letterSpacing: 0.5,
  },
});
