"""
Breach Data — Realistic Breach Definitions
============================================
Static dataset of 15 real-world data breaches used for:
  1. Populating the offline breach SQLite database (``scripts/generate_breach_db.py``)
  2. Generating mock HIBP responses when the live API is unavailable

**Maintenance:** add new breach entries here when extending the dataset.
Only this module should define the canonical breach list — do NOT duplicate elsewhere.
"""

from typing import List, Dict

REALISTIC_BREACHES: List[Dict] = [
    {
        "name": "Adobe",
        "title": "Adobe Breach",
        "domain": "adobe.com",
        "date": "2013-10-04",
        "added_date": "2013-12-04T00:00:00Z",
        "accounts": 152_445_165,
        "description": (
            "In October 2013, 153 million Adobe accounts were breached with each "
            "containing an internal ID, username, email, encrypted password and a "
            "password hint in plain text."
        ),
        "data_classes": ["Email addresses", "Password hints", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "LinkedIn",
        "title": "LinkedIn Breach",
        "domain": "linkedin.com",
        "date": "2012-05-05",
        "added_date": "2016-05-21T00:00:00Z",
        "accounts": 164_611_595,
        "description": (
            "In May 2012, LinkedIn suffered a data breach which exposed the email "
            "addresses and passwords of 164 million subscribers."
        ),
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Yahoo",
        "title": "Yahoo Breach",
        "domain": "yahoo.com",
        "date": "2013-08-01",
        "added_date": "2016-12-14T00:00:00Z",
        "accounts": 3_000_000_000,
        "description": (
            "In August 2013, Yahoo sustained a massive breach affecting 3 billion "
            "accounts. The stolen data included names, email addresses, dates of "
            "birth and security questions."
        ),
        "data_classes": [
            "Dates of birth", "Email addresses", "Names",
            "Passwords", "Security questions and answers",
        ],
        "is_verified": True,
        "severity": "CRITICAL",
    },
    {
        "name": "Dropbox",
        "title": "Dropbox Breach",
        "domain": "dropbox.com",
        "date": "2012-07-01",
        "added_date": "2016-08-31T00:00:00Z",
        "accounts": 68_648_009,
        "description": (
            "In mid-2012, Dropbox suffered a data breach which exposed the email "
            "addresses and passwords of 68 million subscribers."
        ),
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "MySpace",
        "title": "MySpace Breach",
        "domain": "myspace.com",
        "date": "2008-06-01",
        "added_date": "2016-05-31T00:00:00Z",
        "accounts": 359_420_698,
        "description": (
            "In approximately 2008, MySpace suffered a data breach that exposed "
            "almost 360 million accounts."
        ),
        "data_classes": ["Email addresses", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Tumblr",
        "title": "Tumblr Breach",
        "domain": "tumblr.com",
        "date": "2013-02-01",
        "added_date": "2016-05-31T00:00:00Z",
        "accounts": 65_469_298,
        "description": "In February 2013, Tumblr suffered a data breach which exposed 65 million accounts.",
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "MEDIUM",
    },
    {
        "name": "Marriott",
        "title": "Marriott International Breach",
        "domain": "marriott.com",
        "date": "2018-09-10",
        "added_date": "2018-11-30T00:00:00Z",
        "accounts": 500_000_000,
        "description": (
            "In November 2018, Marriott disclosed that approximately 500 million "
            "guests had their information exposed."
        ),
        "data_classes": [
            "Email addresses", "Names", "Phone numbers",
            "Physical addresses", "Travel information",
        ],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Equifax",
        "title": "Equifax Breach",
        "domain": "equifax.com",
        "date": "2017-07-29",
        "added_date": "2017-09-07T00:00:00Z",
        "accounts": 147_000_000,
        "description": (
            "In mid-2017, Equifax suffered a major breach affecting 147 million "
            "people with social security numbers, birthdates, and addresses exposed."
        ),
        "data_classes": [
            "Dates of birth", "Names",
            "Physical addresses", "Social security numbers",
        ],
        "is_verified": True,
        "severity": "CRITICAL",
    },
    {
        "name": "Target",
        "title": "Target Breach",
        "domain": "target.com",
        "date": "2013-12-19",
        "added_date": "2014-01-18T00:00:00Z",
        "accounts": 110_000_000,
        "description": (
            "In late 2013, Target was breached resulting in 110 million customers "
            "having their information stolen."
        ),
        "data_classes": ["Credit cards", "Email addresses", "Names", "Phone numbers"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Uber",
        "title": "Uber Breach",
        "domain": "uber.com",
        "date": "2016-11-01",
        "added_date": "2017-11-21T00:00:00Z",
        "accounts": 57_000_000,
        "description": (
            "In late 2016, Uber suffered a data breach affecting 57 million "
            "accounts including names, email addresses and mobile phone numbers."
        ),
        "data_classes": ["Email addresses", "Names", "Phone numbers"],
        "is_verified": True,
        "severity": "MEDIUM",
    },
    {
        "name": "MyFitnessPal",
        "title": "MyFitnessPal Breach",
        "domain": "myfitnesspal.com",
        "date": "2018-02-01",
        "added_date": "2018-03-29T00:00:00Z",
        "accounts": 143_606_147,
        "description": "In February 2018, MyFitnessPal suffered a data breach affecting 143 million accounts.",
        "data_classes": ["Email addresses", "IP addresses", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Canva",
        "title": "Canva Breach",
        "domain": "canva.com",
        "date": "2019-05-24",
        "added_date": "2019-05-24T00:00:00Z",
        "accounts": 137_000_000,
        "description": "In May 2019, Canva suffered a data breach impacting 137 million subscribers.",
        "data_classes": [
            "Email addresses", "Geographic locations", "Names",
            "Passwords", "Usernames",
        ],
        "is_verified": True,
        "severity": "MEDIUM",
    },
    {
        "name": "Facebook",
        "title": "Facebook Breach",
        "domain": "facebook.com",
        "date": "2019-04-03",
        "added_date": "2021-04-03T00:00:00Z",
        "accounts": 533_313_128,
        "description": (
            "In April 2019, a large dataset of Facebook users was made public "
            "containing phone numbers, names, and Facebook IDs of 533 million users."
        ),
        "data_classes": ["Email addresses", "Names", "Phone numbers", "Social media profiles"],
        "is_verified": True,
        "severity": "HIGH",
    },
    {
        "name": "Twitter",
        "title": "Twitter Breach",
        "domain": "twitter.com",
        "date": "2022-12-01",
        "added_date": "2023-01-04T00:00:00Z",
        "accounts": 235_000_000,
        "description": (
            "In late 2022, data from 235 million Twitter accounts was leaked "
            "containing email addresses and usernames."
        ),
        "data_classes": ["Email addresses", "Names", "Usernames"],
        "is_verified": True,
        "severity": "MEDIUM",
    },
    {
        "name": "Zynga",
        "title": "Zynga Breach",
        "domain": "zynga.com",
        "date": "2019-09-01",
        "added_date": "2019-12-19T00:00:00Z",
        "accounts": 218_360_995,
        "description": "In September 2019, Zynga (Words With Friends) had 218 million accounts exposed.",
        "data_classes": ["Email addresses", "Passwords", "Phone numbers", "Usernames"],
        "is_verified": True,
        "severity": "MEDIUM",
    },
]
