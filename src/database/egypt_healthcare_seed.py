"""Seed data imported from Egypt_Healthcare_Database.json.

The values are kept in source control so deployments and fresh databases receive
the same verified directory without depending on the uploaded zip at runtime.
"""

FACILITY_TYPES = [
    ("مستشفى تعليمي", "Teaching Hospital"),
    ("مستشفى جامعي", "University Hospital"),
    ("مستشفى خاص", "Private Hospital"),
    ("مستشفى عام", "General Hospital"),
    ("معمل تحاليل", "Laboratory"),
    ("صيدلية", "Pharmacy"),
]

OWNERSHIP_TYPES = [
    ("حكومي", "Government"),
    ("خاص", "Private"),
    ("جامعي", "University"),
]

GOVERNORATES = [
    ("القاهرة", "Cairo"),
    ("الإسكندرية", "Alexandria"),
    ("البحيرة", "Beheira"),
]

FACILITIES = [
    {
        "name_ar": "مستشفى أحمد ماهر التعليمي",
        "name_en": "Ahmed Maher Teaching Hospital",
        "type": "Teaching Hospital", "ownership": "Government",
        "gov": "Cairo", "city": "Cairo", "district": "El Sayeda Zeinab",
        "address": "341 Port Said St, El Sayeda Zeinab, Cairo",
        "maps_url": "https://goo.gl/maps/AhmedMaher", "lat": 30.0444, "lng": 31.2357,
        "phone": "02-23911670", "is_24h": True, "emergency": True, "icu": True,
        "source": "MOHP Official",
    },
    {
        "name_ar": "مستشفى الجلاء التعليمي للولادة",
        "name_en": "El Galaa Maternity Teaching Hospital",
        "type": "Teaching Hospital", "ownership": "Government",
        "gov": "Cairo", "city": "Cairo", "district": "Downtown",
        "address": "41 26th of July St, Downtown, Cairo",
        "maps_url": "https://goo.gl/maps/ElGalaa", "lat": 30.0545, "lng": 31.2376,
        "phone": "02-25756474", "is_24h": True, "emergency": True, "icu": True,
        "source": "MOHP Official",
    },
    {
        "name_ar": "مستشفى الساحل التعليمي",
        "name_en": "Al Sahel Teaching Hospital",
        "type": "Teaching Hospital", "ownership": "Government",
        "gov": "Cairo", "city": "Cairo", "district": "Shubra",
        "address": "2 Youssef Karam, El Sahel, Cairo",
        "maps_url": "https://goo.gl/maps/AlSahel", "lat": 30.0833, "lng": 31.25,
        "phone": "01020186351", "is_24h": True, "emergency": True, "icu": True,
        "source": "MOHP Official",
    },
    {
        "name_ar": "مستشفى قصر العيني",
        "name_en": "Kasr Al-Ainy Hospital",
        "type": "University Hospital", "ownership": "University",
        "gov": "Cairo", "city": "Cairo", "district": "El Manial",
        "address": "Al-Saray Street, El Manial, Cairo",
        "maps_url": "https://goo.gl/maps/KasrAlAiny", "lat": 30.0303, "lng": 31.2294,
        "phone": "02-23647545", "is_24h": True, "emergency": True, "icu": True,
        "source": "Cairo University",
    },
    {
        "name_ar": "مستشفى كليوباترا",
        "name_en": "Cleopatra Hospital",
        "type": "Private Hospital", "ownership": "Private",
        "gov": "Cairo", "city": "Cairo", "district": "Heliopolis",
        "address": "39 Cleopatra St, Heliopolis, Cairo",
        "maps_url": "https://goo.gl/maps/Cleopatra", "lat": 30.0911, "lng": 31.3289,
        "phone": "02-24143931", "is_24h": True, "emergency": True, "icu": True,
        "source": "Cleopatra Group",
    },
    {
        "name_ar": "مستشفى الجمهورية العام",
        "name_en": "Al Gomhouria General Hospital",
        "type": "General Hospital", "ownership": "Government",
        "gov": "Alexandria", "city": "Alexandria", "district": "Ragheb",
        "address": "Mahmoudia Canal Street, Alexandria",
        "maps_url": "https://goo.gl/maps/AlGomhouria", "lat": 31.185, "lng": 29.895,
        "phone": "03-3608027", "is_24h": True, "emergency": True, "icu": True,
        "source": "Alexandria Health Directorate",
    },
    {
        "name_ar": "مستشفى الشاطبي الجامعي للأطفال",
        "name_en": "Shatby University Hospital for Children",
        "type": "University Hospital", "ownership": "University",
        "gov": "Alexandria", "city": "Alexandria", "district": "Al Azaritah",
        "address": "El-Gaish Rd, Al Azaritah, Alexandria",
        "maps_url": "https://goo.gl/maps/Shatby", "lat": 31.21, "lng": 29.91,
        "phone": "03-4873500", "is_24h": True, "emergency": True, "icu": True,
        "source": "Alexandria University",
    },
    {
        "name_ar": "مستشفى دمنهور التعليمي",
        "name_en": "Damanhour Teaching Hospital",
        "type": "Teaching Hospital", "ownership": "Government",
        "gov": "Beheira", "city": "Damanhour", "district": "Center",
        "address": "Gomhoria Street, Damanhour, Beheira",
        "maps_url": "https://goo.gl/maps/Damanhour", "lat": 31.0333, "lng": 30.4667,
        "phone": "045-3318222", "is_24h": True, "emergency": True, "icu": True,
        "source": "MOHP Official",
    },
    {
        "name_ar": "معامل البرج - فرع القاهرة",
        "name_en": "Al Borg Laboratories - Cairo",
        "type": "Laboratory", "ownership": "Private",
        "gov": "Cairo", "city": "Cairo", "district": "Mohandessin",
        "address": "Mohandessin, Cairo",
        "maps_url": "https://goo.gl/maps/AlBorgCairo", "lat": 30.05, "lng": 31.2,
        "phone": "19911", "is_24h": False, "emergency": False, "icu": False,
        "source": "Al Borg Labs",
    },
    {
        "name_ar": "صيدلية العزبي - فرع القاهرة",
        "name_en": "El Ezaby Pharmacy - Cairo",
        "type": "Pharmacy", "ownership": "Private",
        "gov": "Cairo", "city": "Cairo", "district": "New Cairo",
        "address": "New Cairo, Cairo",
        "maps_url": "https://goo.gl/maps/ElEzabyCairo", "lat": 30.0, "lng": 31.4,
        "phone": "19600", "is_24h": True, "emergency": False, "icu": False,
        "source": "El Ezaby",
    },
]