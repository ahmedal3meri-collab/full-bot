import re
import hashlib
import base64
import uuid
import secrets
import string
import math
from datetime import datetime, timedelta
import pytz


def safe_eval(expr: str) -> str:
    """Safe math expression evaluator."""
    expr = expr.strip().replace("^", "**").replace("×", "*").replace("÷", "/")
    allowed = set("0123456789+-*/()., **%")
    if not all(c in allowed for c in expr):
        return None
    try:
        result = eval(expr, {"__builtins__": {}}, {
            "abs": abs, "round": round, "int": int, "float": float,
            "sqrt": math.sqrt, "pow": pow, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "ceil": math.ceil,
            "floor": math.floor, "factorial": math.factorial,
        })
        if isinstance(result, float) and result == int(result):
            return str(int(result))
        return str(round(result, 10)).rstrip("0").rstrip(".")
    except Exception:
        return None


def hash_text(text: str) -> dict:
    encoded = text.encode()
    return {
        "MD5": hashlib.md5(encoded).hexdigest(),
        "SHA1": hashlib.sha1(encoded).hexdigest(),
        "SHA256": hashlib.sha256(encoded).hexdigest(),
        "SHA512": hashlib.sha512(encoded).hexdigest(),
    }


def b64_encode(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def b64_decode(text: str) -> str:
    try:
        return base64.b64decode(text.encode()).decode()
    except Exception:
        return None


def gen_password(length: int = 16) -> str:
    length = max(8, min(64, length))
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        pwd = "".join(secrets.choice(chars) for _ in range(length))
        if (any(c.isupper() for c in pwd) and any(c.islower() for c in pwd)
                and any(c.isdigit() for c in pwd) and any(c in "!@#$%^&*()-_=+" for c in pwd)):
            return pwd


def gen_uuid() -> str:
    return str(uuid.uuid4())


def parse_time(text: str) -> timedelta | None:
    """Parse time strings like 10m, 1h, 2d, 30s."""
    patterns = [
        (r"(\d+)\s*s(?:ec(?:ond)?s?)?", "seconds"),
        (r"(\d+)\s*m(?:in(?:ute)?s?)?", "minutes"),
        (r"(\d+)\s*h(?:our?s?)?", "hours"),
        (r"(\d+)\s*d(?:ay?s?)?", "days"),
    ]
    for pattern, unit in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return timedelta(**{unit: int(m.group(1))})
    return None


def get_city_time(city: str) -> str | None:
    city_tz = {
        "الرياض": "Asia/Riyadh", "riyadh": "Asia/Riyadh",
        "جدة": "Asia/Riyadh", "jeddah": "Asia/Riyadh",
        "دبي": "Asia/Dubai", "dubai": "Asia/Dubai",
        "القاهرة": "Africa/Cairo", "cairo": "Africa/Cairo",
        "بغداد": "Asia/Baghdad", "baghdad": "Asia/Baghdad",
        "بيروت": "Asia/Beirut", "beirut": "Asia/Beirut",
        "عمان": "Asia/Amman", "amman": "Asia/Amman",
        "الكويت": "Asia/Kuwait", "kuwait": "Asia/Kuwait",
        "الدوحة": "Asia/Qatar", "doha": "Asia/Qatar",
        "أبوظبي": "Asia/Dubai", "abu dhabi": "Asia/Dubai",
        "مسقط": "Asia/Muscat", "muscat": "Asia/Muscat",
        "لندن": "Europe/London", "london": "Europe/London",
        "باريس": "Europe/Paris", "paris": "Europe/Paris",
        "برلين": "Europe/Berlin", "berlin": "Europe/Berlin",
        "نيويورك": "America/New_York", "new york": "America/New_York",
        "لوس انجلوس": "America/Los_Angeles", "los angeles": "America/Los_Angeles",
        "طوكيو": "Asia/Tokyo", "tokyo": "Asia/Tokyo",
        "بكين": "Asia/Shanghai", "beijing": "Asia/Shanghai",
        "موسكو": "Europe/Moscow", "moscow": "Europe/Moscow",
        "إسطنبول": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
        "الرباط": "Africa/Casablanca", "rabat": "Africa/Casablanca",
        "تونس": "Africa/Tunis", "tunis": "Africa/Tunis",
        "الجزائر": "Africa/Algiers", "algiers": "Africa/Algiers",
    }
    tz_name = city_tz.get(city.lower())
    if not tz_name:
        return None
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


JOKES_AR = [
    "لماذا يكره العلماء الذرة؟ لأنها دائماً تقاطع!",
    "ماذا قال صفر لثمانية؟ حزامك جميل!",
    "لماذا لا يثق الحاسوب بالإنترنت؟ لأنه كان دائماً يواجه 'فيروسات'!",
    "ما الفرق بين البرمجي والبيتزا؟ البيتزا تُغذّي عائلة من أربعة!",
    "قال الرقم 1 للرقم 10: أنت ليس بدوني!",
    "لماذا ذهب المبرمج إلى المحكمة؟ لأنه حاول تجاوز حدود المصفوفة!",
    "ماذا يقول المغني للحاسوب؟ هل أنت جاهز للـ BYTE؟",
    "لماذا فشل المبرمج في الزواج؟ لأنه لم يعرف كيف يُنهي العلاقة بطريقة صحيحة!",
    "ما أكثر ما يخاف منه المبرمج؟ الـ null pointer!",
    "قال الكود للمبرمج: أنا أعمل على جهازي فقط!",
]

JOKES_EN = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my wife she should embrace her mistakes. She gave me a hug!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "What do you call a fake noodle? An impasta!",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What did the ocean say to the beach? Nothing, it just waved!",
    "I used to hate facial hair, but then it grew on me!",
]

QUOTES_AR = [
    "النجاح ليس نهاية الطريق، والفشل ليس نهاية الحياة، الشجاعة هي التي تُحدد. — ونستون تشرشل",
    "المستقبل ينتمي لأولئك الذين يؤمنون بجمال أحلامهم. — إليانور روزفلت",
    "كن التغيير الذي تريد أن تراه في العالم. — غاندي",
    "إذا لم تتمكن من فعل الأشياء العظيمة، فافعل الأشياء الصغيرة بطريقة رائعة. — نابليون هيل",
    "لا يهم كم مرة سقطت، بل كم مرة نهضت. — مجهول",
    "الوقت ذهب فلا تضيّعه. — مجهول",
    "الفشل هو فرصة للبدء مجدداً بشكل أذكى. — هنري فورد",
    "الحياة قصيرة، ابتسم بينما لا تزال لديك أسنان! — مجهول",
    "عندما تريد شيئاً ما، يتآمر الكون لمساعدتك في الحصول عليه. — باولو كويلو",
    "الشخص الناجح هو من يبني أساساً متيناً بالطوب الذي رماه عليه الآخرون. — ديفيد برينكلي",
]

QUOTES_EN = [
    "Success is not final, failure is not fatal: It is the courage to continue that counts. — Churchill",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "Be the change you wish to see in the world. — Gandhi",
    "You miss 100% of the shots you don't take. — Wayne Gretzky",
    "In the middle of every difficulty lies opportunity. — Einstein",
    "It always seems impossible until it's done. — Nelson Mandela",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Life is what happens when you're busy making other plans. — John Lennon",
    "Spread love everywhere you go. — Mother Teresa",
    "When you reach the end of your rope, tie a knot in it and hang on. — Franklin D. Roosevelt",
]

FACTS_AR = [
    "الأخطبوط لديه ثلاثة قلوب!",
    "البرق يضرب الأرض حوالي مئة مرة في الثانية!",
    "الكلب يمكنه شم الرائحة بمقدار 40 ألف مرة أفضل من الإنسان!",
    "الفيل هو الحيوان الوحيد الذي لا يستطيع القفز!",
    "الأخطبوط لديه دماغ في كل ذراع من ذراعيه الثمانية!",
    "النجوم لا تنتمي لأي دولة وفقاً للقانون الدولي!",
    "الدماغ البشري يستهلك 20% من طاقة الجسم رغم أنه يشكل 2% من وزنه!",
    "الفراشة تتذوق الطعام بأقدامها!",
    "الأسماك لديها ذاكرة أكثر من ثلاث ثوانٍ!",
    "صوت الصاعقة يُسمى 'الرعد' لأن الهواء يتمدد بسرعة!",
]

FACTS_EN = [
    "An octopus has three hearts!",
    "Lightning strikes the Earth about 100 times per second!",
    "A dog's sense of smell is 40,000 times better than a human's!",
    "Elephants are the only animals that cannot jump!",
    "An octopus has a brain in each of its eight arms!",
    "Butterflies taste with their feet!",
    "The human brain uses 20% of the body's energy despite being only 2% of its weight!",
    "Fish have memories longer than three seconds!",
    "Honey never spoils — archaeologists found edible 3000-year-old honey in Egyptian tombs!",
    "The shortest war in history was between Britain and Zanzibar — it lasted 38 minutes!",
]

TRIVIA_QUESTIONS = [
    {
        "q_ar": "ما عاصمة المملكة العربية السعودية؟",
        "q_en": "What is the capital of Saudi Arabia?",
        "choices": ["الرياض / Riyadh", "جدة / Jeddah", "مكة / Mecca", "المدينة / Medina"],
        "answer": 0,
    },
    {
        "q_ar": "من اخترع الهاتف؟",
        "q_en": "Who invented the telephone?",
        "choices": ["غراهام بيل / Graham Bell", "إديسون / Edison", "تسلا / Tesla", "فاراداي / Faraday"],
        "answer": 0,
    },
    {
        "q_ar": "كم عدد أضلاع المثلث؟",
        "q_en": "How many sides does a triangle have?",
        "choices": ["3", "4", "5", "6"],
        "answer": 0,
    },
    {
        "q_ar": "ما أكبر كوكب في المجموعة الشمسية؟",
        "q_en": "What is the largest planet in the solar system?",
        "choices": ["المشتري / Jupiter", "زحل / Saturn", "الأرض / Earth", "أورانوس / Uranus"],
        "answer": 0,
    },
    {
        "q_ar": "ما أطول نهر في العالم؟",
        "q_en": "What is the longest river in the world?",
        "choices": ["النيل / Nile", "الأمازون / Amazon", "اليانغتسي / Yangtze", "المسيسيبي / Mississippi"],
        "answer": 0,
    },
    {
        "q_ar": "في أي سنة هبطت أول مركبة فضائية على القمر؟",
        "q_en": "In which year did the first spacecraft land on the moon?",
        "choices": ["1969", "1971", "1965", "1975"],
        "answer": 0,
    },
    {
        "q_ar": "ما أصغر دولة في العالم؟",
        "q_en": "What is the smallest country in the world?",
        "choices": ["الفاتيكان / Vatican", "موناكو / Monaco", "نورو / Nauru", "سان مارينو / San Marino"],
        "answer": 0,
    },
    {
        "q_ar": "كم عدد دقائق الساعة؟",
        "q_en": "How many minutes are in an hour?",
        "choices": ["60", "50", "100", "70"],
        "answer": 0,
    },
    {
        "q_ar": "ما لغة البرمجة التي خلقها Guido van Rossum؟",
        "q_en": "Which programming language was created by Guido van Rossum?",
        "choices": ["Python", "Java", "C++", "Ruby"],
        "answer": 0,
    },
    {
        "q_ar": "ما أعمق بحيرة في العالم؟",
        "q_en": "What is the deepest lake in the world?",
        "choices": ["بايكال / Baikal", "تيتيكاكا / Titicaca", "كاسبيان / Caspian", "فيكتوريا / Victoria"],
        "answer": 0,
    },
]
