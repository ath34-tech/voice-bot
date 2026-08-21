import React, { useState } from 'react';
import { StyleSheet, View, SafeAreaView, Platform } from 'react-native';
import { StatusBar } from 'expo-status-bar';

import { COLORS } from './src/theme/colors';
import AmbientParticles from './src/components/AmbientParticles';
import AccessGateScreen from './src/screens/AccessGateScreen';
import MicCheckScreen from './src/screens/MicCheckScreen';
import LiveInterviewScreen from './src/screens/LiveInterviewScreen';
import CompletionScreen from './src/screens/CompletionScreen';
import { requestStartCall } from './src/services/api';

export default function App() {
  // Finite State Machine: 'ACCESS' | 'MIC_CHECK' | 'INTERVIEW' | 'COMPLETE'
  const [appState, setAppState] = useState('ACCESS');
  const [sessionData, setSessionData] = useState(null);

  // Screen 1 Action: Submit Access Gate
  const handleAccessSubmit = async (formData) => {
    const res = await requestStartCall(formData);
    setSessionData({ ...formData, ...res });
    setAppState('MIC_CHECK');
  };

  // Screen 2 Action: Proceed from Mic Check to Live Interview Room
  const handleProceedToInterview = () => {
    setAppState('INTERVIEW');
  };

  // Screen 3 Action: Survey Complete
  const handleCompleteSurvey = () => {
    setAppState('COMPLETE');
  };

  // Screen 4 Action: Reset Session back to Access Gate
  const handleResetSession = () => {
    setSessionData(null);
    setAppState('ACCESS');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="light" backgroundColor={COLORS.void} />
      
      {/* Constellation Particle Field */}
      <AmbientParticles />

      {/* Main Screen Router */}
      <View style={styles.screenContainer}>
        {appState === 'ACCESS' && (
          <AccessGateScreen onSubmitAccess={handleAccessSubmit} />
        )}

        {appState === 'MIC_CHECK' && (
          <MicCheckScreen onProceedToInterview={handleProceedToInterview} />
        )}

        {appState === 'INTERVIEW' && (
          <LiveInterviewScreen
            sessionData={sessionData}
            onCompleteSurvey={handleCompleteSurvey}
          />
        )}

        {appState === 'COMPLETE' && (
          <CompletionScreen onResetSession={handleResetSession} />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.void,
    paddingTop: Platform.OS === 'android' ? 30 : 0,
  },
  screenContainer: {
    flex: 1,
  },
});

import { registerRootComponent } from 'expo';
registerRootComponent(App);
