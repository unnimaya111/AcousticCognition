import re

def update_file():
    with open('audio_processing.py', 'r', encoding='utf-8') as f:
        content = f.read()

    start_match = re.search(r'def process_audio\(.*?:\n', content)
    if not start_match:
        print("Could not find process_audio")
        return
        
    start_idx = start_match.start()
    
    end_match = re.search(r'def _default_features\(\):', content)
    if not end_match:
        print("Could not find _default_features")
        return
        
    end_idx = end_match.start()
    
    new_func = '''def process_audio(file_path_or_bytes, expected_sentence=""):
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
        if noise_floor < 0.005:
            noise_deduction = 0
        elif noise_floor < 0.01:
            noise_deduction = 2
        elif noise_floor < 0.02:
            noise_deduction = 5
        else:
            noise_deduction = 10

        # Apply simple noise gate
        gate_threshold = noise_floor * 1.5
        y_denoised = np.where(np.abs(y) < gate_threshold, 0, y)

        # Recalculate RMS for segmentation
        rms_denoised = librosa.feature.rms(y=y_denoised, frame_length=2048, hop_length=512)[0]
        threshold = max(0.01, float(np.mean(rms_denoised)) * 0.5)

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
        errors = 0
        similarity = 0.0
        if transcript_available and expected_sentence.strip():
            ref_words = re.findall(r'\\b\\w+\\b', expected_sentence.lower())
            hyp_words = re.findall(r'\\b\\w+\\b', transcript.lower())
            sm = difflib.SequenceMatcher(None, ref_words, hyp_words)
            matched = sum(triple.size for triple in sm.get_matching_blocks())
            errors = (len(ref_words) - matched) + (len(hyp_words) - matched)
            similarity = sm.ratio()
        elif not transcript_available and speech_duration >= 1.0:
            errors = 6
        
        # Deduct for Accuracy
        acc_deduction = 0
        if speech_duration < 1.0:
            acc_deduction = 50
        elif errors == 0:
            acc_deduction = 0
        elif errors == 1:
            acc_deduction = 5
        elif errors == 2:
            acc_deduction = 10
        elif errors <= 4:
            acc_deduction = 20
        else:
            acc_deduction = 35

        # Speaking Rate (WPM)
        word_count = len(expected_sentence.strip().split()) if expected_sentence else max(1, len(transcript.split()))
        effective_speech_time = max(speech_duration, 0.5)
        wpm = (word_count / effective_speech_time) * 60.0

        rate_deduction = 0
        if 110 <= wpm <= 170:
            rate_deduction = 0
        elif (95 <= wpm <= 109) or (171 <= wpm <= 190):
            rate_deduction = 3
        elif (80 <= wpm <= 94) or (191 <= wpm <= 210):
            rate_deduction = 7
        else:
            rate_deduction = 12

        # Pause Deduction
        pause_deduction = 0
        if long_pause_count <= 2:
            pause_deduction = 0
        elif long_pause_count <= 4:
            pause_deduction = 5
        elif long_pause_count <= 6:
            pause_deduction = 10
        else:
            pause_deduction = 15

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
            hesitation_deduction = 3
        elif hesitation_count <= 4:
            hesitation_deduction = 7
        else:
            hesitation_deduction = 12

        # Fluency Deduction
        total_issues = acc_deduction + rate_deduction + pause_deduction + hesitation_deduction
        fluency_deduction = 0
        if total_issues == 0:
            fluency_deduction = 0
        elif total_issues <= 10:
            fluency_deduction = 3
        elif total_issues <= 25:
            fluency_deduction = 8
        else:
            fluency_deduction = 15

        # Final Score
        final_score = 100.0 - acc_deduction - rate_deduction - pause_deduction - hesitation_deduction - fluency_deduction - noise_deduction
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

'''
    
    new_content = content[:start_idx] + new_func + content[end_idx:]
    with open('audio_processing.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

update_file()
