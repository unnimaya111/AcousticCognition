import io
import streamlit as st
import librosa
import numpy as np


def _low_voice_result(score, reason):
    """Return a result dictionary for recordings that fail hard gates."""
    return {
        "speech_rate_wpm": 0.0,
        "hesitations_per_min": 0.0,
        "pause_count": 0,
        "avg_pause_duration": 0.0,
        "long_pauses": 0,
        "silence_ratio": 1.0,
        "speaking_time": 0.0,
        "silence_time": 0.0,
        "fluency_score": float(score),
        "acoustic_explanation": reason,
        "speech_rate": 0.0,
        "pause_frequency": 0.0,
        "hesitation_duration": 0.0,
        "hesitation_count": 0,
        "total_duration": 0.0,
        "mfcc_mean": [0.0] * 13,
        "transcript": "",
        # Required alias keys
        "speech_duration": 0.0,
        "speech_ratio": 0.0,
        "transcript_similarity": 0.0,
        "voice_score": float(score),
        "performance_score": float(score),
        "acoustic_score": float(score),
    }


def process_audio(file_path_or_bytes, expected_sentence=""):
    """
    Deduction-based voice analysis scoring.
    Base score = 100. Deductions for missing words, speaking rate, pauses, hesitations, fluency, and noise.
    """
    import re
    import difflib
    try:
        if hasattr(file_path_or_bytes, "seek"):
            file_path_or_bytes.seek(0)

        # 1. Load Audio
        y, sr = librosa.load(file_path_or_bytes, sr=16000)

        if len(y) == 0:
            return _low_voice_result(0, "Empty audio file.")

        total_duration = librosa.get_duration(y=y, sr=sr)
        if total_duration < 1.0:
            return _low_voice_result(5, "Very little speech detected.")

        # 2. Preprocessing: Remove DC offset & Normalize
        y = y - np.mean(y)
        y = librosa.util.normalize(y)

        # 3. VAD and Silence Removal
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        rms_mean = float(np.mean(rms))
        
        # Noise profile estimation (lowest 10% of energy frames)
        sorted_rms = np.sort(rms)
        noise_floor = np.mean(sorted_rms[:max(1, len(sorted_rms)//10)])
        
        # Determine background noise deduction
        noise_deduction = 0
        if noise_floor < 0.015:
            noise_deduction = 0
        elif noise_floor < 0.03:
            noise_deduction = 2
        else:
            noise_deduction = 5

        # Apply simple noise gate
        gate_threshold = noise_floor * 1.5
        y_denoised = np.where(np.abs(y) < gate_threshold, 0, y)

        # Recalculate RMS for segmentation
        rms_denoised = librosa.feature.rms(y=y_denoised, frame_length=2048, hop_length=512)[0]
        threshold = max(0.005, float(np.mean(rms_denoised)) * 0.25)

        speech_frames = rms_denoised > threshold
        hop_duration = 512.0 / sr

        speech_segments = []
        in_speech = False
        seg_start = 0.0

        for i, is_speech in enumerate(speech_frames):
            t = i * hop_duration
            if is_speech and not in_speech:
                seg_start = t
                in_speech = True
            elif not is_speech and in_speech:
                seg_end = t
                speech_segments.append((seg_start, seg_end))
                in_speech = False
        if in_speech:
            speech_segments.append((seg_start, len(rms_denoised) * hop_duration))

        speech_duration = sum(end - start for start, end in speech_segments)
        silence_duration = total_duration - speech_duration
        speech_ratio = speech_duration / total_duration if total_duration > 0 else 0.0
        silence_ratio = silence_duration / total_duration if total_duration > 0 else 0.0
        
        # Pauses (Long Pauses > 0.6s)
        pauses = []
        for i in range(1, len(speech_segments)):
            gap = speech_segments[i][0] - speech_segments[i - 1][1]
            if gap >= 0.2:
                pauses.append(gap)

        long_pause_count = sum(1 for p in pauses if p >= 0.6)
        
        # Speech Recognition
        transcript = ""
        transcript_available = False
        try:
            import speech_recognition as sr_recognizer
            r = sr_recognizer.Recognizer()
            if hasattr(file_path_or_bytes, "seek"):
                file_path_or_bytes.seek(0)
            with sr_recognizer.AudioFile(file_path_or_bytes) as source:
                audio_data = r.record(source)
            transcript = r.recognize_google(audio_data).strip()
            transcript_available = bool(transcript)
        except Exception:
            transcript = ""
            transcript_available = False

        # Sentence Accuracy (Missing/Incorrect Words)
        similarity = 0.0
        if transcript_available and expected_sentence and expected_sentence.strip():
            ref_clean = re.sub(r'[^\w\s]', '', expected_sentence.lower())
            hyp_clean = re.sub(r'[^\w\s]', '', transcript.lower())
            articles = {'a', 'an', 'the'}
            ref_words = [w for w in ref_clean.split() if w not in articles]
            hyp_words = [w for w in hyp_clean.split() if w not in articles]
            ref_str = " ".join(ref_words)
            hyp_str = " ".join(hyp_words)
            sm = difflib.SequenceMatcher(None, ref_str, hyp_str)
            similarity = sm.ratio()
        elif not transcript_available and speech_duration >= 1.0:
            similarity = 0.0
        
        # Deduct for Accuracy
        acc_deduction = 0
        if speech_duration < 1.0:
            acc_deduction = 50
        elif similarity >= 0.95:
            acc_deduction = 0
        elif similarity >= 0.90:
            acc_deduction = 2
        elif similarity >= 0.85:
            acc_deduction = 5
        elif similarity >= 0.80:
            acc_deduction = 8
        elif similarity >= 0.70:
            acc_deduction = 15
        elif similarity >= 0.50:
            acc_deduction = 25
        else:
            acc_deduction = 35

        # Speaking Rate (WPM)
        word_count = len(expected_sentence.strip().split()) if expected_sentence else max(1, len(transcript.split()))
        effective_speech_time = max(total_duration, 1.0)
        wpm = (word_count / effective_speech_time) * 60.0

        rate_deduction = 0
        if 90 <= wpm <= 180:
            rate_deduction = 0
        elif (80 <= wpm <= 89) or (181 <= wpm <= 200):
            rate_deduction = 2
        else:
            rate_deduction = 5

        # Pause Deduction
        pause_deduction = 0
        if long_pause_count <= 3:
            pause_deduction = 0
        elif long_pause_count <= 5:
            pause_deduction = 3
        elif long_pause_count <= 7:
            pause_deduction = 6
        else:
            pause_deduction = 10

        # Hesitation Detection
        hesitation_count = 0
        if transcript_available:
            filler_words = {"um", "uh", "erm", "hmm", "ah", "aa", "er", "uhh", "umm", "hm", "aah", "ehh", "eh"}
            words_in_transcript = transcript.lower().split()
            for w in words_in_transcript:
                clean_w = re.sub(r'[^a-z]', '', w)
                if clean_w in filler_words:
                    hesitation_count += 1
            # Check repeated words and syllables
            for i in range(1, len(words_in_transcript)):
                if words_in_transcript[i] == words_in_transcript[i-1]:
                    hesitation_count += 1
        
        hesitation_deduction = 0
        if hesitation_count == 0:
            hesitation_deduction = 0
        elif hesitation_count <= 2:
            hesitation_deduction = 2
        elif hesitation_count <= 4:
            hesitation_deduction = 5
        else:
            hesitation_deduction = 8

        fluency_deduction = 0
        if similarity >= 0.90 and long_pause_count < 3 and hesitation_count < 2:
            fluency_deduction = 0
        else:
            total_issues = acc_deduction + rate_deduction + pause_deduction + hesitation_deduction
            if total_issues > 10:
                fluency_deduction = 5

        # Final Score
        final_score = 100.0 - acc_deduction - rate_deduction - pause_deduction - hesitation_deduction - noise_deduction - fluency_deduction
        
        if similarity >= 0.90 and speech_ratio >= 0.6 and total_duration >= 3.0:
            final_score = max(final_score, 95.0)
            
        final_score = round(max(0.0, min(100.0, float(final_score))), 1)

        # Explanations
        explanations = []
        if acc_deduction == 50:
            explanations.append("Very little speech was detected.")
        elif acc_deduction >= 35:
            explanations.append("Sentence contained many missing or incorrect words.")
        elif acc_deduction > 0:
            explanations.append("Sentence contained missing words.")
            
        if rate_deduction > 0:
            if wpm < 110:
                explanations.append("Speaking rate was slower than normal.")
            else:
                explanations.append("Speaking rate was faster than normal.")
                
        if pause_deduction > 0:
            explanations.append("Multiple prolonged pauses were detected.")
            
        if hesitation_deduction > 0:
            if hesitation_count > 2:
                explanations.append("Frequent hesitation was detected.")
            else:
                explanations.append("Minor hesitation was detected.")
                
        if noise_deduction > 0:
            explanations.append("Background noise was detected but minimally affected the analysis.")

        if not explanations:
            acoustic_explanation = "Speech patterns appear completely normal and fluent."
        else:
            if len(explanations) > 1:
                joined = " ".join(explanations)
                acoustic_explanation = joined
            else:
                acoustic_explanation = explanations[0]

        return {
            "speech_rate_wpm": round(wpm, 1),
            "hesitations_per_min": float(hesitation_count),
            "pause_count": len(pauses),
            "avg_pause_duration": round(sum(pauses)/len(pauses) if pauses else 0, 2),
            "long_pauses": long_pause_count,
            "silence_ratio": round(silence_ratio, 2),
            "speaking_time": round(speech_duration, 2),
            "silence_time": round(silence_duration, 2),
            "fluency_score": final_score,
            "acoustic_explanation": acoustic_explanation,
            "speech_rate": round(wpm / 60, 2),
            "pause_frequency": float(hesitation_count),
            "hesitation_duration": float(hesitation_count * 0.3),
            "hesitation_count": hesitation_count,
            "total_duration": round(total_duration, 2),
            "mfcc_mean": [0.0] * 13,
            "transcript": transcript,
            "speech_duration": round(speech_duration, 2),
            "speech_ratio": round(speech_ratio, 3),
            "transcript_similarity": round(similarity, 3),
            "voice_score": final_score,
            "performance_score": final_score,
            "acoustic_score": final_score,
        }

    except Exception as e:
        import traceback
        st.error(f"Analysis error: {e}")
        return _low_voice_result(0, f"Analysis error: {e}")

def _default_features():
    """Safe fallback when audio cannot be analysed."""
    return {
        "speech_rate_wpm": 0.0, "hesitations_per_min": 0.0, "pause_count": 0,
        "avg_pause_duration": 0.0, "long_pauses": 0, "silence_ratio": 0.0,
        "speaking_time": 0.0, "silence_time": 0.0, "fluency_score": 0.0,
        "acoustic_explanation": "No valid speech detected or sentence could not be recognized.",
        "speech_rate": 0.0, "pause_frequency": 0.0, "hesitation_duration": 0.0,
        "hesitation_count": 0, "total_duration": 0.0, "mfcc_mean": [0.0] * 13,
        "transcript": "",
        "speech_duration": 0.0, "speech_ratio": 0.0, "transcript_similarity": 0.0,
        "voice_score": 0.0, "performance_score": 0.0, "acoustic_score": 0.0,
    }
