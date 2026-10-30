import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

interface VoiceSpeakerProps {
  textToSpeak: string;
}

export const VoiceSpeaker: React.FC<VoiceSpeakerProps> = ({ textToSpeak }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      setIsSupported(false);
    }

    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleSpeak = () => {
    if (!isSupported) return;

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    window.speechSynthesis.cancel(); // Clear any ongoing speech
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 0.95; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    utterance.onstart = () => setIsPlaying(true);
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.speak(utterance);
  };

  if (!isSupported) return null;

  return (
    <button
      type="button"
      onClick={handleSpeak}
      title={isPlaying ? 'Stop audio' : 'Listen to question'}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
        isPlaying
          ? 'bg-indigo-600/30 text-indigo-300 border-indigo-500/50 animate-pulse'
          : 'bg-slate-850 hover:bg-gray-100 text-gray-700 border-gray-300'
      }`}
    >
      {isPlaying ? (
        <>
          <VolumeX className="w-3.5 h-3.5 text-indigo-400" />
          <span>Stop Voice</span>
        </>
      ) : (
        <>
          <Volume2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Listen</span>
        </>
      )}
    </button>
  );
};
