"""
generate_idol_audio.py
Generates kid-friendly TTS audio for idol-explorer hotspots in en/hi/bn,
converts MP3 -> WAV, and zips the result as idol-audio-pack.zip.

Usage:
  python generate_idol_audio.py

Requirements:
  pip install gtts pydub
  ffmpeg must be installed and available on PATH
"""

import os
import time
import zipfile
from gtts import gTTS
from pydub import AudioSegment

# --- Hotspots (kid-friendly narration) ---
hotspots = [
    {
        "id": "lion",
        "story_en": "Maa Durga rides the mighty lion. It shows her courage and power to protect us.",
        "story_hi": "माँ दुर्गा सिंह पर सवार होती हैं। यह उनके साहस और शक्ति को दिखाता है, जिससे वे हमारी रक्षा करती हैं।",
        "story_bn": "মা দুর্গা সিংহে আরোহণ করেন। এটি তার সাহস ও শক্তি প্রকাশ করে, যা দিয়ে তিনি আমাদের রক্ষা করেন।",
    },
    {
        "id": "mouse",
        "story_en": "Ganesha’s vehicle is a little mouse. Small but very clever and quick!",
        "story_hi": "गणेश का वाहन एक छोटा चतुर मूषक है। छोटा होकर भी बहुत चालाक और तेज है!",
        "story_bn": "গণেশের বাহন একটি ছোট ইঁদুর। ছোট হলেও খুব চালাক এবং দ্রুত।",
    },
    {
        "id": "peacock",
        "story_en": "Kartikeya rides a colorful peacock. It shines with beauty and pride.",
        "story_hi": "कार्तिकेय एक रंग-बिरंगे मोर पर सवार रहते हैं। यह सुंदरता और गर्व से चमकता है।",
        "story_bn": "কার্তিকেয় রঙিন ময়ূরে চড়েন। এটি সৌন্দর্য ও গৌরবে ঝলমল করে।",
    },
    {
        "id": "owl",
        "story_en": "The wise owl is with Goddess Lakshmi. It reminds us to stay alert and thoughtful.",
        "story_hi": "बुद्धिमान उल्लू देवी लक्ष्मी के साथ है। यह हमें सतर्क और विचारशील रहने की याद दिलाता है।",
        "story_bn": "জ্ঞানী উলু দেবী লক্ষ্মীর সাথে। এটি আমাদের সতর্ক ও চিন্তাশীল থাকতে শেখায়।",
    },
    {
        "id": "swan",
        "story_en": "The swan is Saraswati’s vehicle. It stands for purity and the joy of learning.",
        "story_hi": "हंस सरस्वती का वाहन है। यह पवित्रता और सीखने की खुशी का प्रतीक है।",
        "story_bn": "হংস সরস্বতীর বাহন। এটি বিশুদ্ধতা এবং শেখার আনন্দের প্রতীক।",
    },
    {
        "id": "buffalo",
        "story_en": "The buffalo is linked to Mahishasura, the demon Maa Durga bravely defeated.",
        "story_hi": "भैंसा महिषासुर से जुड़ा है, जिसे माँ दुर्गा ने बहादुरी से हराया था।",
        "story_bn": "ভৈরব (মহিষ) মহিষাসুরের সাথে সম্পর্কিত, যাকে মা দুর্গা সাহসের সাথে পরাজিত করেছিলেন।",
    },
    {
        "id": "trishul",
        "story_en": "The Trishul is a powerful trident. It helps Maa Durga destroy evil and spread light.",
        "story_hi": "त्रिशूल एक शक्तिशाली त्रिशूल है। यह माँ दुर्गा को बुराई हराने और उजाला फैलाने में मदद करता है।",
        "story_bn": "ত্রিশূল একটি শক্তিশালী ত্রিশূল। এটি মা দুর্গাকে অপশক্তি নিবারণের মধ্যে সাহায্য করে।",
    },
    {
        "id": "sword",
        "story_en": "The sword is sharp like truth. It cuts away lies and helps truth shine through.",
        "story_hi": "तलवार सत्य की तरह तेज है। यह झूठ को काटकर सत्य को उजागर करती है।",
        "story_bn": "তলোয়ার সত্যের মতো ধারালো। এটি মিথ্যাকে কেটে সত্যকে প্রকাশ করে।",
    },
    {
        "id": "lotus",
        "story_en": "The lotus grows pure and beautiful. It reminds us about spiritual growth and goodness.",
        "story_hi": "कमल पवित्र और सुंदर उगता है। यह आध्यात्मिक वृद्धि और अच्छेपन की याद दिलाता है।",
        "story_bn": "পদ্ম পবিত্র ও সুন্দরভাবে বৃদ্ধি পায়। এটি আমাদের আধ্যাত্মিক বিকাশ ও শুভতার কথা মনে করায়।",
    },
    {
        "id": "kartikeya_vel",
        "story_en": "The Vel is Kartikeya’s bright spear. It stands for bravery and winning with honor.",
        "story_hi": "वेल कार्तिकेय का भाला है। यह वीरता और सम्मान के साथ जीत का प्रतीक है।",
        "story_bn": "ভেল কার্তিকেয়ার উজ্জ্বল কোঁচ। এটি সাহস ও মানসম্মত জয়ের প্রতীক।",
    },
    {
        "id": "ganesha",
        "story_en": "Ganesha removes obstacles and brings cheerful new beginnings for everyone.",
        "story_hi": "गणेश बाधाएं दूर करते हैं और सभी के लिए खुशहाल नई शुरुआत लाते हैं।",
        "story_bn": "গণেশ বাঁধা দূর করেন এবং সবার জন্য সুখময় নতুন সূচনা নিয়ে আসেন।",
    },
    {
        "id": "lakshmi",
        "story_en": "Lakshmi is the goddess of wealth and kindness. She brings good fortune and smiles.",
        "story_hi": "लक्ष्मी धन और दया की देवी हैं। वे शुभता और मुस्कान लाती हैं।",
        "story_bn": "লক্ষ্মী ধন ও করুণা-প্রদানকারী দেবী। তিনি সৌভাগ্য এবং হাসি আনেন।",
    },
    {
        "id": "durga",
        "story_en": "Maa Durga is a strong mother who defeats evil and protects the world with love.",
        "story_hi": "माँ दुर्गा एक शक्तिशाली माँ हैं जो बुराई को हराकर प्रेम से दुनिया की रक्षा करती हैं।",
        "story_bn": "মা দুর্গা একজন শক্তিশালী মা, তিনি প্রেম দিয়ে পাপ পরাস্ত করে পৃথিবীকে রক্ষা করেন।",
    },
    {
        "id": "saraswati",
        "story_en": "Saraswati is the goddess of knowledge, music, and arts. She helps us love learning.",
        "story_hi": "सरस्वती ज्ञान, संगीत और कला की देवी हैं। वह हमें सीखने से प्रेम करवाती हैं।",
        "story_bn": "সরস্বতী জ্ঞান, সঙ্গীত ও কলার দেবী। তিনি আমাদের শেখার প্রতি অনুরাগ বাড়ান।",
    },
    {
        "id": "kartikeya",
        "story_en": "Kartikeya is a brave warrior god and the commander of the gods.",
        "story_hi": "कार्तिकेय एक बहादुर योद्धा देवता और देवताओं के सेनापति हैं।",
        "story_bn": "কার্তিকেয় এক সাহসী যোদ্ধা দেবতা ও দেবতাদের অধিনায়ক।",
    },
]

# --- output dirs ---
OUT_DIR = "assets/audio"
os.makedirs(OUT_DIR, exist_ok=True)


# Progress helper
def safe_tts_save(text, lang, outpath):
    # gTTS may fail sometimes; wrap in try/except and retry once
    for attempt in range(2):
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(outpath)
            return True
        except Exception as e:
            print(f"[WARN] gTTS failed for {outpath} (attempt {attempt+1}): {e}")
            time.sleep(1)
    return False


# Generate mp3 then convert to wav and clean up mp3
generated = []
for h in hotspots:
    hid = h["id"]
    for lang_code, text_key in (
        ("en", "story_en"),
        ("hi", "story_hi"),
        ("bn", "story_bn"),
    ):
        text = h[text_key]
        mp3_path = os.path.join(OUT_DIR, f"{hid}_{lang_code}.mp3")
        wav_path = os.path.join(OUT_DIR, f"{hid}_{lang_code}.wav")
        print(f"Generating: {hid} [{lang_code}] ...")
        ok = safe_tts_save(text, lang_code, mp3_path)
        if not ok:
            print(f"[ERROR] Could not generate TTS for {hid}_{lang_code}. Skipping.")
            continue
        # Convert mp3 to wav using pydub (ffmpeg required)
        try:
            audio = AudioSegment.from_file(mp3_path, format="mp3")
            audio.export(wav_path, format="wav")
            print(f"Saved WAV: {wav_path}")
            # remove mp3 to save space (optional)
            os.remove(mp3_path)
            generated.append(wav_path)
        except Exception as e:
            print(f"[ERROR] Conversion failed for {mp3_path}: {e}")

# Create zip package
zip_name = "idol-audio-pack.zip"
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
    for wav in generated:
        # put them under assets/audio/ in the zip
        arcname = os.path.join("assets", "audio", os.path.basename(wav))
        zf.write(wav, arcname)
print(f"\nDone. Created zip: {zip_name}")
print("Drop the contents of the zip into your project's assets/audio/ folder.")
