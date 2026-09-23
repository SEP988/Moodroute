"""NLP Mood Detection using HuggingFace distilRoBERTa.

Classifies text into 7 emotions then maps to MoodRoute categories.
Falls back to keyword-based detection when the model is unavailable.

Production behaviour on Render (no local cache, TRANSFORMERS_OFFLINE=1):
  - _load_model() detects offline mode immediately
  - Falls back to keyword detector in <1ms, never times out
  - No network calls, no gunicorn worker timeout

Local behaviour (model cached in ~/.cache/huggingface/):
  - Loads from disk, no download
  - Full transformer inference available
"""
import os
import re


class MoodDetector:
    _instance = None
    _classifier = None
    # None = not yet attempted, True = loaded, False = permanently unavailable
    _model_available = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── Public entry point ────────────────────────────────────────────────────

    def initialize(self):
        """Call this once at application startup (before gunicorn forks workers).
        
        Safe to call multiple times — only runs once due to the class-level guard.
        """
        self._load_model()

    def detect(self, mood_text: str) -> dict:
        """Detect mood from text. Uses transformer model if available, else keywords."""
        if self._model_available is None:
            # Not yet attempted in this process — load now (first request path)
            self._load_model()

        if self._model_available and self._classifier is not None:
            print('[NLP] Inference started')
            return self._detect_with_model(mood_text)
        else:
            return self._detect_with_keywords(mood_text)

    # ── Model loading ─────────────────────────────────────────────────────────

    def _load_model(self):
        """Attempt to load the distilRoBERTa model.

        Production safety rules:
          1. If TRANSFORMERS_OFFLINE=1 is set, skip immediately (no network calls).
          2. If model is not in local cache, skip immediately (no download attempt).
          3. Only load from disk — never trigger a download during this call.
          4. Once determined (True or False), never attempt again in this process.
        """
        # Guard: already determined in this process
        if self._model_available is not None:
            return

        print('[NLP] Initializing model...')

        # Rule 1: Respect TRANSFORMERS_OFFLINE — skip without any network attempt
        if os.environ.get('TRANSFORMERS_OFFLINE', '0') == '1':
            print('[NLP] TRANSFORMERS_OFFLINE=1 — using keyword fallback.')
            MoodDetector._model_available = False
            self._model_available = False
            return

        # Rule 2: Only load if the model is already cached locally
        if not self._is_model_cached():
            print('[NLP] Model not in local cache — using keyword fallback.')
            print('[NLP] To enable the transformer model, run:')
            print('[NLP]   python3 -c "from transformers import pipeline; pipeline(\'text-classification\', model=\'j-hartmann/emotion-english-distilroberta-base\', top_k=None)"')
            MoodDetector._model_available = False
            self._model_available = False
            return

        # Rule 3: Load from disk only — local_files_only=True prevents any download
        try:
            from transformers import pipeline

            self._classifier = pipeline(
                'text-classification',
                model='j-hartmann/emotion-english-distilroberta-base',
                top_k=None,
                device=-1,            # CPU only
                local_files_only=True # Never download — fail fast if not cached
            )
            MoodDetector._model_available = True
            self._model_available = True
            print('[NLP] Model loaded successfully')

        except Exception as load_error:
            MoodDetector._model_available = False
            self._model_available = False
            print(f'[NLP] Initialization failed: {type(load_error).__name__}: {load_error}')
            print('[NLP] Using keyword fallback for all requests.')

    def _is_model_cached(self) -> bool:
        """Return True only if the model files exist in the local HuggingFace cache."""
        cache_dir = os.path.expanduser('~/.cache/huggingface/hub')
        if not os.path.exists(cache_dir):
            return False
        try:
            for entry in os.listdir(cache_dir):
                if 'distilroberta' in entry.lower() or 'hartmann' in entry.lower():
                    return True
        except OSError:
            pass
        return False

    # ── Transformer inference ─────────────────────────────────────────────────

    def _detect_with_model(self, mood_text: str) -> dict:
        """Use HuggingFace distilRoBERTa for emotion detection."""
        classifier_results = self._classifier(mood_text[:512])[0]
        classifier_results.sort(key=lambda item: item['score'], reverse=True)

        top_emotion = classifier_results[0]['label']
        confidence = classifier_results[0]['score']
        all_emotion_scores = {
            result['label']: round(result['score'], 4)
            for result in classifier_results
        }
        mood_category = self._map_emotion_to_mood(top_emotion, all_emotion_scores)

        return {
            'detected_emotion': top_emotion,
            'mood_category': mood_category,
            'confidence': round(confidence, 3),
            'all_scores': all_emotion_scores,
            'description': self._get_mood_description(mood_category),
            'method': 'distilRoBERTa'
        }

    # ── Keyword fallback ──────────────────────────────────────────────────────

    def _detect_with_keywords(self, mood_text: str) -> dict:
        """Keyword-based mood detection used when transformer model is unavailable."""
        lowered_text = mood_text.lower().strip()

        emotion_keywords = {
            'anger': {
                'angry': 2, 'furious': 3, 'frustrated': 2, 'irritated': 2,
                'annoyed': 2, 'rage': 3, 'mad': 2, 'pissed': 3,
                'hate': 2, 'fed up': 2, "can't stand": 2
            },
            'disgust': {
                'disgusted': 3, 'gross': 2, 'sick of': 2, 'revolting': 3,
                'repulsed': 3, 'awful': 1, 'terrible': 1
            },
            'fear': {
                'afraid': 3, 'scared': 3, 'terrified': 3, 'anxious': 3,
                'anxiety': 3, 'worried': 2, 'nervous': 2, 'panic': 3,
                'dread': 3, 'uneasy': 2, 'restless': 2, 'fear': 3,
                'tense': 2, 'on edge': 2, 'freaking out': 3
            },
            'joy': {
                'happy': 3, 'great': 2, 'wonderful': 3, 'amazing': 3,
                'excited': 3, 'joyful': 3, 'love': 2, 'fantastic': 3,
                'good': 1, 'cheerful': 2, 'elated': 3, 'pleased': 2,
                'delighted': 3, 'thrilled': 3, 'blessed': 2, 'grateful': 2,
                'content': 2, 'brilliant': 2
            },
            'sadness': {
                'sad': 3, 'depressed': 3, 'unhappy': 2, 'upset': 2,
                'down': 2, 'low': 2, 'lonely': 3, 'grief': 3,
                'miss': 2, 'crying': 3, 'hopeless': 3, 'gloomy': 2,
                'miserable': 3, 'heartbroken': 3, 'empty': 2, 'numb': 2,
                'melancholy': 3
            },
            'surprise': {
                'surprised': 3, 'shocked': 3, 'amazed': 2, 'astonished': 3,
                'unexpected': 2, 'wow': 2, 'unbelievable': 2, "can't believe": 2
            },
            'neutral': {}
        }

        stress_keywords = {
            'stressed': 3, 'overwhelmed': 3, 'pressure': 2, 'deadline': 2,
            'too much': 2, "can't cope": 3, 'burnt out': 3, 'overworked': 3,
            'swamped': 2, 'drowning': 2, 'assignment': 1, 'exam': 1
        }
        tired_keywords = {
            'tired': 3, 'exhausted': 3, 'fatigue': 3, 'sleepy': 2,
            'drained': 3, 'no energy': 3, 'worn out': 3, 'lethargy': 3,
            'sluggish': 2, 'weary': 2, 'knackered': 3
        }
        energetic_keywords = {
            'energetic': 3, 'pumped': 3, 'motivated': 3, 'ready': 1,
            'active': 2, 'strong': 2, 'fired up': 3, "let's go": 3,
            'enthusiastic': 3, 'alive': 2, 'vibrant': 2, 'buzzing': 2
        }

        emotion_scores = {emotion: 0 for emotion in emotion_keywords}
        emotion_scores['stressed_compound'] = 0
        emotion_scores['tired_compound'] = 0
        emotion_scores['energetic_compound'] = 0

        negation_patterns = [
            r'\bnot\s+', r"\bdon't\s+", r'\bdont\s+', r'\bno\s+',
            r'\bnever\s+', r'\bwithout\s+', r'\bhardly\s+'
        ]

        for emotion, keywords in emotion_keywords.items():
            for keyword, weight in keywords.items():
                if keyword in lowered_text:
                    is_negated = any(
                        re.search(pat + re.escape(keyword), lowered_text)
                        for pat in negation_patterns
                    )
                    emotion_scores[emotion] += (-weight if is_negated else weight)

        for keyword, weight in stress_keywords.items():
            if keyword in lowered_text:
                emotion_scores['stressed_compound'] += weight
        for keyword, weight in tired_keywords.items():
            if keyword in lowered_text:
                emotion_scores['tired_compound'] += weight
        for keyword, weight in energetic_keywords.items():
            if keyword in lowered_text:
                emotion_scores['energetic_compound'] += weight

        if emotion_scores['stressed_compound'] >= 3:
            detected_emotion, mood_category = 'anger', 'stressed'
            top_score = emotion_scores['stressed_compound']
        elif emotion_scores['tired_compound'] >= 3:
            detected_emotion, mood_category = 'neutral', 'tired'
            top_score = emotion_scores['tired_compound']
        elif emotion_scores['energetic_compound'] >= 3:
            detected_emotion, mood_category = 'surprise', 'energetic'
            top_score = emotion_scores['energetic_compound']
        else:
            base = {e: s for e, s in emotion_scores.items()
                    if e in emotion_keywords and e != 'neutral'}
            if any(s > 0 for s in base.values()):
                detected_emotion = max(base, key=base.get)
                top_score = base[detected_emotion]
            else:
                detected_emotion, top_score = 'neutral', 1

            mood_category = self._map_emotion_to_mood(
                detected_emotion,
                {e: max(0, s) / max(1, sum(max(0, x) for x in emotion_scores.values()))
                 for e, s in emotion_scores.items() if e in emotion_keywords}
            )

        total_weight = sum(max(0, s) for s in emotion_scores.values()) + 1
        confidence = min(0.85, 0.45 + (top_score / total_weight) * 0.4)

        all_emotion_scores = {
            e: round(max(0, emotion_scores.get(e, 0)) / max(1, total_weight), 4)
            for e in ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        }

        return {
            'detected_emotion': detected_emotion,
            'mood_category': mood_category,
            'confidence': round(confidence, 3),
            'all_scores': all_emotion_scores,
            'description': self._get_mood_description(mood_category),
            'method': 'keyword_fallback'
        }

    # ── Emotion mapping ───────────────────────────────────────────────────────

    def _map_emotion_to_mood(self, emotion: str, scores: dict) -> str:
        if scores.get('sadness', 0) > 0.25 and scores.get('anger', 0) > 0.2:
            return 'stressed'
        if emotion == 'neutral' and scores.get('sadness', 0) > 0.15:
            return 'tired'
        if emotion == 'neutral' and scores.get('joy', 0) > 0.15:
            return 'happy'
        return {
            'anger': 'stressed', 'disgust': 'stressed',
            'fear': 'anxious',   'sadness': 'sad',
            'joy': 'happy',      'surprise': 'energetic',
            'neutral': 'neutral'
        }.get(emotion, 'neutral')

    def _get_mood_description(self, mood: str) -> str:
        return {
            'stressed':  'Quiet, green, and calming routes to help you decompress',
            'anxious':   'Very quiet, secluded paths with minimal stimulation',
            'tired':     'Short, flat, gentle walks to restore your energy',
            'sad':       'Nature-rich uplifting routes to lift your spirits',
            'happy':     'Scenic enjoyable routes to celebrate your mood',
            'energetic': 'Long, challenging routes to channel your energy',
            'neutral':   'Balanced, well-rounded walking routes'
        }.get(mood, 'Balanced, well-rounded walking routes')