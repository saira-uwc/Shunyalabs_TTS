"""Shared configuration for all TTS test scripts."""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SHUNYALABS_API_KEY", "")
MODEL = "zero-indic"

# Default test text (multilingual samples)
TEST_TEXTS = {
    "en": "Hello, welcome to the Shunyalabs text to speech testing suite.",
    "hi": "नमस्ते, शुन्यलैब्स टेक्स्ट टू स्पीच टेस्टिंग सूट में आपका स्वागत है।",
    "bn": "হ্যালো, শূন্যল্যাবস টেক্সট টু স্পিচ টেস্টিং স্যুটে আপনাকে স্বাগতম।",
    "ta": "வணக்கம், ஷுன்யலாப்ஸ் உரையிலிருந்து பேச்சு சோதனை தொகுப்பிற்கு வரவேற்கிறோம்.",
    "te": "హలో, శూన్యల్యాబ్స్ టెక్స్ట్ టు స్పీచ్ టెస్టింగ్ సూట్‌కు స్వాగతం.",
    "gu": "હેલો, શૂન્યલેબ્સ ટેક્સ્ટ ટુ સ્પીચ ટેસ્ટિંગ સ્યુટમાં આપનું સ્વાગત છે.",
    "kn": "ಹಲೋ, ಶೂನ್ಯಲ್ಯಾಬ್ಸ್ ಟೆಕ್ಸ್ಟ್ ಟು ಸ್ಪೀಚ್ ಟೆಸ್ಟಿಂಗ್ ಸೂಟ್‌ಗೆ ಸ್ವಾಗತ.",
    "ml": "ഹലോ, ശൂന്യലാബ്സ് ടെക്സ്റ്റ് ടു സ്പീച്ച് ടെസ്റ്റിംഗ് സ്യൂട്ടിലേക്ക് സ്വാഗതം.",
    "mr": "हॅलो, शून्यलॅब्स टेक्स्ट टू स्पीच टेस्टिंग सूटमध्ये आपले स्वागत आहे.",
    "pa": "ਹੈਲੋ, ਸ਼ੁਨਿਆਲੈਬਸ ਟੈਕਸਟ ਟੂ ਸਪੀਚ ਟੈਸਟਿੰਗ ਸੂਟ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ।",
    "or": "ହେଲୋ, ଶୂନ୍ୟଲ୍ୟାବ୍ସ ଟେକ୍ସଟ ଟୁ ସ୍ପିଚ ଟେଷ୍ଟିଂ ସୁଟକୁ ସ୍ୱାଗତ।",
    "ur": "ہیلو، شونیالیبز ٹیکسٹ ٹو اسپیچ ٹیسٹنگ سوٹ میں خوش آمدید۔",
    "as": "নমস্কাৰ, শূন্যলেবছ টেক্সট টু স্পীচ টেষ্টিং চুইটলৈ আপোনাক স্বাগতম।",
    "ne": "नमस्ते, शून्यल्याब्स टेक्स्ट टु स्पिच टेस्टिङ सुटमा तपाईंलाई स्वागत छ।",
    "sa": "नमस्ते, शून्यलैब्स पाठात् वाक् परीक्षण सुइट् मध्ये स्वागतम्।",
}

# All 46 speakers mapped to their language
VOICES = {
    "Assamese":  {"male": "Bimal",    "female": "Anjana"},
    "Bengali":   {"male": "Arjun",    "female": "Priyanka"},
    "Bodo":      {"male": "Daimalu",  "female": "Hasina"},
    "Dogri":     {"male": "Vishal",   "female": "Neelam"},
    "English":   {"male": "Varun",    "female": "Nisha"},
    "Gujarati":  {"male": "Rakesh",   "female": "Pooja"},
    "Hindi":     {"male": "Rajesh",   "female": "Sunita"},
    "Kannada":   {"male": "Kiran",    "female": "Shreya"},
    "Kashmiri":  {"male": "Farooq",   "female": "Habba"},
    "Konkani":   {"male": "Mohan",    "female": "Sarita"},
    "Maithili":  {"male": "Suresh",   "female": "Meera"},
    "Malayalam":  {"male": "Krishnan", "female": "Deepa"},
    "Manipuri":  {"male": "Tomba",    "female": "Ibemhal"},
    "Marathi":   {"male": "Siddharth","female": "Ananya"},
    "Nepali":    {"male": "Bikash",   "female": "Sapana"},
    "Odia":      {"male": "Bijay",    "female": "Sujata"},
    "Punjabi":   {"male": "Gurpreet", "female": "Simran"},
    "Sanskrit":  {"male": "Vedant",   "female": "Gayatri"},
    "Santali":   {"male": "Chandu",   "female": "Roshni"},
    "Sindhi":    {"male": "Amjad",    "female": "Kavita"},
    "Tamil":     {"male": "Murugan",  "female": "Thangam"},
    "Telugu":    {"male": "Vishnu",   "female": "Lakshmi"},
    "Urdu":      {"male": "Salman",   "female": "Fatima"},
}

# All expression styles
EXPRESSIONS = [
    "Happy", "Sad", "Angry", "Fearful", "Surprised",
    "Disgust", "News", "Conversational", "Narrative",
    "Enthusiastic", "Neutral",
]

# All output formats
FORMATS = ["pcm", "wav", "mp3", "ogg_opus", "flac", "mulaw", "alaw"]

# Speed test values
SPEEDS = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]
