import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, AlertCircle } from 'lucide-react';

interface AudioRecorderProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onTranscript, disabled = false }) => {
  const [isSupported, setIsSupported] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const textToAdd = finalTranscript || interimTranscript;
        if (textToAdd) {
          onTranscript(textToAdd);
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          setErrorMsg(`Microphone error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch (e) {
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
    };
  }, [onTranscript]);

  const toggleListening = () => {
    if (!recognitionRef.current || disabled) return;

    setErrorMsg(null);
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err: any) {
        setErrorMsg('Microphone permission required or already in use.');
        setIsListening(false);
      }
    }
  };

  if (!isSupported) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-gray-400 bg-white px-2.5 py-1.5 rounded-lg border border-gray-200">
        <AlertCircle className="w-3.5 h-3.5 text-gray-500" />
        <span>Voice input unsupported in this browser. Standard typing active.</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggleListening}
          disabled={disabled}
          title={isListening ? 'Stop listening' : 'Start voice dictation'}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            isListening
              ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 animate-pulse'
              : 'bg-gray-100 hover:bg-gray-300 text-gray-700 border border-gray-300'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          {isListening ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
              <MicOff className="w-3.5 h-3.5" />
              <span>Listening... Click to Stop</span>
            </>
          ) : (
            <>
              <Mic className="w-3.5 h-3.5 text-indigo-400" />
              <span>Voice Dictation (Mic)</span>
            </>
          )}
        </button>
      </div>
      {errorMsg && <p className="text-[11px] text-rose-400">{errorMsg}</p>}
    </div>
  );
};
