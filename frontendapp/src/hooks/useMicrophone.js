import { useState, useEffect, useRef, useCallback } from 'react';
import { Platform } from 'react-native';

export function useMicrophone() {
  const [permissionStatus, setPermissionStatus] = useState('undetermined'); // 'undetermined' | 'granted' | 'denied'
  const [audioLevel, setAudioLevel] = useState(0); // 0.0 to 1.0
  const [hasAudioInput, setHasAudioInput] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const streamRef = useRef(null);
  const audioCtxRef = useRef(null);
  const animFrameRef = useRef(null);

  // Request Microphone Permission for Web and Native Expo Go
  const requestPermission = useCallback(async () => {
    try {
      setErrorMsg('');

      // Web Environment (browser & Expo Web)
      if (Platform.OS === 'web' && typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        setPermissionStatus('granted');

        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          const audioCtx = new AudioContext();
          audioCtxRef.current = audioCtx;
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 256;
          source.connect(analyser);

          const bufferLength = analyser.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);

          const checkAudioLevel = () => {
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
              sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const normalizedLevel = Math.min(1.0, Math.max(0.0, average / 128));

            setAudioLevel(normalizedLevel);
            if (normalizedLevel > 0.06) {
              setHasAudioInput(true);
            }

            animFrameRef.current = requestAnimationFrame(checkAudioLevel);
          };

          checkAudioLevel();
        } else {
          setHasAudioInput(true);
        }
      } else {
        // Native Mobile Environment (Expo Go on Android / iOS)
        try {
          const { Audio } = require('expo-av');
          const response = await Audio.requestPermissionsAsync();
          if (response.granted) {
            await Audio.setAudioModeAsync({
              allowsRecordingIOS: true,
              playsInSilentModeIOS: true,
            });
            setPermissionStatus('granted');
            setHasAudioInput(true);
          } else {
            setPermissionStatus('denied');
            setErrorMsg('Microphone access is blocked. Allow microphone access in your device settings.');
          }
        } catch (nativeErr) {
          setPermissionStatus('granted');
          setHasAudioInput(true);
        }
      }
    } catch (err) {
      console.warn('Microphone permission error:', err);
      setPermissionStatus('denied');
      setErrorMsg('Microphone access is blocked. Allow microphone access in your device/browser settings before continuing.');
    }
  }, []);

  // Mute / Unmute Local Microphone Track
  const toggleMute = useCallback((shouldMute) => {
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !shouldMute;
      });
    }
  }, []);

  // Cleanup Stream and AudioContext
  const stopMicrophone = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
    }
    if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
      audioCtxRef.current.close();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      stopMicrophone();
    };
  }, [stopMicrophone]);

  return {
    permissionStatus,
    audioLevel,
    hasAudioInput,
    errorMsg,
    requestPermission,
    toggleMute,
    stopMicrophone,
  };
}
