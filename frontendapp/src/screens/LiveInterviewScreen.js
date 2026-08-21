import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import { COLORS, SPACING } from '../theme/colors';
import Header from '../components/Header';
import AudioOrb from '../components/AudioOrb';
import TranscriptBox from '../components/TranscriptBox';
import ProgressTracker from '../components/ProgressTracker';
import ControlDock from '../components/ControlDock';
import EndSurveyModal from '../components/EndSurveyModal';
import { useMicrophone } from '../hooks/useMicrophone';

export default function LiveInterviewScreen({ sessionData, onCompleteSurvey }) {
  const [connectionState, setConnectionState] = useState('Connected');
  const [orbState, setOrbState] = useState('ai_speaking'); // 'idle' | 'ai_speaking' | 'user_speaking'
  const [isBargeIn, setIsBargeIn] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [showEndModal, setShowEndModal] = useState(false);

  // Real physical microphone stream hook
  const { audioLevel, toggleMute, requestPermission } = useMicrophone();

  useEffect(() => {
    requestPermission();
  }, [requestPermission]);

  // Survey Session State
  const [currentStep, setCurrentStep] = useState(3);
  const totalSteps = 10;
  const [sectionName, setSectionName] = useState('Section B · Teaching Style & Comprehension');

  const [aiQuestion, setAiQuestion] = useState(
    'Do you usually understand the topics taught by your teacher in class?'
  );
  const [studentSpeech, setStudentSpeech] = useState('');
  const [statusState, setStatusState] = useState('listening');

  // Interactive Voice Interview Turns
  const turns = useRef([
    {
      question: 'Do you usually understand the topics taught by your teacher in class?',
      section: 'Section B · Teaching Style',
      step: 3,
      userReply: 'No, I often struggle when they read directly from textbooks.',
    },
    {
      question: 'How comfortable do you feel asking questions or talking to your teacher in class?',
      section: 'Section B · Teaching Style',
      step: 4,
      userReply: 'I feel uncomfortable because they can be strict.',
    },
    {
      question: 'Which things help you understand and stay interested in a topic the most?',
      section: 'Section B · Teaching Style',
      step: 5,
      userReply: 'Examples, real-life stories, and hands-on activities.',
    },
    {
      question: 'If you study a topic today, how much of it do you usually remember the next day?',
      section: 'Section C · Learning Psychology',
      step: 6,
      userReply: 'I remember about half of it.',
    },
    {
      question: 'What is your favourite subject?',
      section: 'Section C · Learning Psychology',
      step: 7,
      userReply: 'Math, because I like using my brain and solving logic problems.',
    },
  ]).current;

  const currentTurnIdx = useRef(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const turn = turns[currentTurnIdx.current];
      if (!turn) {
        onCompleteSurvey();
        return;
      }

      setAiQuestion(turn.question);
      setSectionName(turn.section);
      setCurrentStep(turn.step);

      // AI speaks
      setOrbState('ai_speaking');
      setStatusState('thinking');
      setStudentSpeech('');

      // After AI finishes speaking, wait for user speech
      setTimeout(() => {
        setOrbState('user_speaking');
        setStatusState('listening');
        setStudentSpeech(turn.userReply);

        setTimeout(() => {
          currentTurnIdx.current += 1;
          if (currentTurnIdx.current >= turns.length) {
            onCompleteSurvey();
          }
        }, 4000);
      }, 3500);
    }, 9000);

    return () => clearInterval(interval);
  }, [turns, onCompleteSurvey]);

  // Toggle local hardware microphone track
  const handleToggleMute = () => {
    const nextMuteState = !isMuted;
    setIsMuted(nextMuteState);
    toggleMute(nextMuteState);
    if (!nextMuteState) {
      setIsBargeIn(false);
    }
  };

  const handleToggleVolume = () => {
    // Toggle volume audio gain
  };

  return (
    <View style={styles.container}>
      {/* Top Header */}
      <Header
        connectionState={connectionState}
        studentName={sessionData?.name || 'Alex'}
      />

      <View style={styles.mainContent}>
        {/* Progress Tracker */}
        <ProgressTracker
          sectionName={sectionName}
          currentStep={currentStep}
          totalSteps={totalSteps}
        />

        {/* Central Animated Audio Orb (Reacting to Real Mic Amplitude) */}
        <AudioOrb
          state={orbState}
          isBargeIn={isBargeIn}
          audioLevel={orbState === 'ai_speaking' ? 0.7 : Math.max(audioLevel, 0.3)}
        />

        {/* Subtitle / Transcript Box */}
        <TranscriptBox
          aiQuestion={aiQuestion}
          studentSpeech={studentSpeech}
          statusState={statusState}
        />

        {/* Bottom Control Dock */}
        <ControlDock
          isMuted={isMuted}
          onToggleMute={handleToggleMute}
          onToggleVolume={handleToggleVolume}
          onEndSurvey={() => setShowEndModal(true)}
        />
      </View>

      {/* Confirmation Exit Modal */}
      <EndSurveyModal
        visible={showEndModal}
        onContinue={() => setShowEndModal(false)}
        onConfirmEnd={() => {
          setShowEndModal(false);
          onCompleteSurvey();
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.warmCream,
  },
  mainContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.lg,
    paddingBottom: 20,
  },
});
