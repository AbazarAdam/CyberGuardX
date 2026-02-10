"""
Comprehensive Breach Dataset Generator for CyberGuardX
Generates 100,000+ realistic breach records for offline operation
"""
import csv
import hashlib
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sqlite3

# COMPREHENSIVE Real-world breach data with full details
REALISTIC_BREACHES = [
    {
        "name": "Adobe",
        "title": "Adobe Breach",
        "domain": "adobe.com",
        "date": "2013-10-04",
        "added_date": "2013-12-04T00:00:00Z",
        "accounts": 152445165,
        "description": "In October 2013, 153 million Adobe accounts were breached with each containing an internal ID, username, email, encrypted password and a password hint in plain text.",
        "data_classes": ["Email addresses", "Password hints", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "LinkedIn",
        "title": "LinkedIn Breach",
        "domain": "linkedin.com",
        "date": "2012-05-05",
        "added_date": "2016-05-21T00:00:00Z",
        "accounts": 164611595,
        "description": "In May 2012, LinkedIn suffered a data breach which exposed the email addresses and passwords of 164 million subscribers.",
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Yahoo",
        "title": "Yahoo Breach",
        "domain": "yahoo.com",
        "date": "2013-08-01",
        "added_date": "2016-12-14T00:00:00Z",
        "accounts": 3000000000,
        "description": "In August 2013, Yahoo sustained a massive breach affecting 3 billion accounts. The stolen data included names, email addresses, dates of birth and security questions.",
        "data_classes": ["Dates of birth", "Email addresses", "Names", "Passwords", "Security questions and answers"],
        "is_verified": True,
        "severity": "CRITICAL"
    },
    {
        "name": "Dropbox",
        "title": "Dropbox Breach",
        "domain": "dropbox.com",
        "date": "2012-07-01",
        "added_date": "2016-08-31T00:00:00Z",
        "accounts": 68648009,
        "description": "In mid-2012, Dropbox suffered a data breach which exposed the email addresses and passwords of 68 million subscribers.",
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "MySpace",
        "title": "MySpace Breach",
        "domain": "myspace.com",
        "date": "2008-06-01",
        "added_date": "2016-05-31T00:00:00Z",
        "accounts": 359420698,
        "description": "In approximately 2008, MySpace suffered a data breach that exposed almost 360 million accounts.",
        "data_classes": ["Email addresses", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Tumblr",
        "title": "Tumblr Breach",
        "domain": "tumblr.com",
        "date": "2013-02-01",
        "added_date": "2016-05-31T00:00:00Z",
        "accounts": 65469298,
        "description": "In February 2013, Tumblr suffered a data breach which exposed 65 million accounts.",
        "data_classes": ["Email addresses", "Passwords"],
        "is_verified": True,
        "severity": "MEDIUM"
    },
    {
        "name": "Marriott",
        "title": "Marriott International Breach",
        "domain": "marriott.com",
        "date": "2018-09-10",
        "added_date": "2018-11-30T00:00:00Z",
        "accounts": 500000000,
        "description": "In November 2018, Marriott disclosed that approximately 500 million guests had their information exposed.",
        "data_classes": ["Email addresses", "Names", "Phone numbers", "Physical addresses", "Travel information"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Equifax",
        "title": "Equifax Breach",
        "domain": "equifax.com",
        "date": "2017-07-29",
        "added_date": "2017-09-07T00:00:00Z",
        "accounts": 147000000,
        "description": "In mid-2017, Equifax suffered a major breach affecting 147 million people with social security numbers, birthdates, and addresses exposed.",
        "data_classes": ["Dates of birth", "Names", "Physical addresses", "Social security numbers"],
        "is_verified": True,
        "severity": "CRITICAL"
    },
    {
        "name": "Target",
        "title": "Target Breach",
        "domain": "target.com",
        "date": "2013-12-19",
        "added_date": "2014-01-18T00:00:00Z",
        "accounts": 110000000,
        "description": "In late 2013, Target was breached resulting in 110 million customers having their information stolen.",
        "data_classes": ["Credit cards", "Email addresses", "Names", "Phone numbers"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Uber",
        "title": "Uber Breach",
        "domain": "uber.com",
        "date": "2016-11-01",
        "added_date": "2017-11-21T00:00:00Z",
        "accounts": 57000000,
        "description": "In late 2016, Uber suffered a data breach affecting 57 million accounts including names, email addresses and mobile phone numbers.",
        "data_classes": ["Email addresses", "Names", "Phone numbers"],
        "is_verified": True,
        "severity": "MEDIUM"
    },
    {
        "name": "MyFitnessPal",
        "title": "MyFitnessPal Breach",
        "domain": "myfitnesspal.com",
        "date": "2018-02-01",
        "added_date": "2018-03-29T00:00:00Z",
        "accounts": 143606147,
        "description": "In February 2018, MyFitnessPal suffered a data breach affecting 143 million accounts.",
        "data_classes": ["Email addresses", "IP addresses", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Canva",
        "title": "Canva Breach",
        "domain": "canva.com",
        "date": "2019-05-24",
        "added_date": "2019-05-24T00:00:00Z",
        "accounts": 137000000,
        "description": "In May 2019, Canva suffered a data breach impacting 137 million subscribers.",
        "data_classes": ["Email addresses", "Geographic locations", "Names", "Passwords", "Usernames"],
        "is_verified": True,
        "severity": "MEDIUM"
    },
    {
        "name": "Facebook",
        "title": "Facebook Breach",
        "domain": "facebook.com",
        "date": "2019-04-03",
        "added_date": "2021-04-03T00:00:00Z",
        "accounts": 533313128,
        "description": "In April 2019, a large dataset of Facebook users was made public containing phone numbers, names, and Facebook IDs of 533 million users.",
        "data_classes": ["Email addresses", "Names", "Phone numbers", "Social media profiles"],
        "is_verified": True,
        "severity": "HIGH"
    },
    {
        "name": "Twitter",
        "title": "Twitter Breach",
        "domain": "twitter.com",
        "date": "2022-12-01",
        "added_date": "2023-01-04T00:00:00Z",
        "accounts": 235000000,
        "description": "In late 2022, data from 235 million Twitter accounts was leaked containing email addresses and usernames.",
        "data_classes": ["Email addresses", "Names", "Usernames"],
        "is_verified": True,
        "severity": "MEDIUM"
    },
    {
        "name": "Zynga",
        "title": "Zynga Breach",
        "domain": "zynga.com",
        "date": "2019-09-01",
        "added_date": "2019-12-19T00:00:00Z",
        "accounts": 218360995,
        "description": "In September 2019, Zynga (Words With Friends) had 218 million accounts exposed.",
        "data_classes": ["Email addresses", "Passwords", "Phone numbers", "Usernames"],
        "is_verified": True,
        "severity": "MEDIUM"
    }
]

# EXPANDED name lists for more realistic generation (500+ unique names)
FIRST_NAMES = [
    "james", "mary", "john", "patricia", "robert", "jennifer", "michael", "linda",
    "william", "barbara", "david", "elizabeth", "richard", "susan", "joseph", "jessica",
    "thomas", "sarah", "christopher", "karen", "charles", "nancy", "daniel", "lisa",
    "matthew", "betty", "anthony", "margaret", "mark", "sandra", "donald", "ashley",
    "steven", "kimberly", "paul", "emily", "andrew", "donna", "joshua", "michelle",
    "kenneth", "carol", "kevin", "amanda", "brian", "dorothy", "george", "melissa",
    "timothy", "deborah", "ronald", "stephanie", "edward", "rebecca", "jason", "sharon",
    "jeffrey", "laura", "ryan", "cynthia", "jacob", "kathleen", "gary", "amy",
    "nicholas", "shirley", "eric", "angela", "jonathan", "helen", "stephen", "anna",
    "larry", "brenda", "justin", "pamela", "scott", "nicole", "brandon", "emma",
    "benjamin", "samantha", "samuel", "katherine", "raymond", "christine", "gregory", "debra",
    "alexander", "rachel", "patrick", "catherine", "frank", "carolyn", "jack", "janet",
    "dennis", "ruth", "jerry", "maria", "tyler", "heather", "aaron", "diane",
    "jose", "virginia", "adam", "julie", "henry", "joyce", "nathan", "victoria",
    "douglas", "olivia", "zachary", "kelly", "peter", "christina", "kyle", "lauren",
    "walter", "joan", "ethan", "evelyn", "jeremy", "judith", "harold", "megan",
    "keith", "cheryl", "christian", "andrea", "roger", "hannah", "noah", "martha",
    "gerald", "jacqueline", "carl", "frances", "terry", "gloria", "sean", "ann",
    "austin", "teresa", "arthur", "kathryn", "lawrence", "sara", "jesse", "janice",
    "dylan", "jean", "bryan", "alice", "joe", "madison", "jordan", "doris",
    "billy", "abigail", "bruce", "julia", "albert", "judy", "willie", "grace",
    "gabriel", "denise", "logan", "amber", "alan", "marilyn", "juan", "beverly"
]

LAST_NAMES = [
    "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis",
    "rodriguez", "martinez", "hernandez", "lopez", "gonzalez", "wilson", "anderson", "thomas",
    "taylor", "moore", "jackson", "martin", "lee", "perez", "thompson", "white",
    "harris", "sanchez", "clark", "ramirez", "lewis", "robinson", "walker", "young",
    "allen", "king", "wright", "scott", "torres", "nguyen", "hill", "flores",
    "green", "adams", "nelson", "baker", "hall", "rivera", "campbell", "mitchell",
    "carter", "roberts", "gomez", "phillips", "evans", "turner", "diaz", "parker",
    "cruz", "edwards", "collins", "reyes", "stewart", "morris", "morales", "murphy",
    "cook", "rogers", "gutierrez", "ortiz", "morgan", "cooper", "peterson", "bailey",
    "reed", "kelly", "howard", "ramos", "kim", "cox", "ward", "richardson",
    "watson", "brooks", "chavez", "wood", "james", "bennett", "gray", "mendoza",
    "ruiz", "hughes", "price", "alvarez", "castillo", "sanders", "patel", "myers",
    "long", "ross", "foster", "jimenez", "powell", "jenkins", "perry", "russell",
    "sullivan", "bell", "coleman", "butler", "henderson", "barnes", "gonzales", "fisher",
    "vasquez", "simmons", "romero", "jordan", "patterson", "alexander", "hamilton", "graham",
    "reynolds", "griffin", "wallace", "moreno", "west", "cole", "hayes", "bryant",
    "herrera", "gibson", "ellis", "tran", "medina", "aguilar", "stevens", "murray",
    "ford", "castro", "marshall", "owens", "harrison", "fernandez", "mcdonald", "woods",
    "washington", "kennedy", "wells", "vargas", "henry", "chen", "freeman", "webb"
]

COMMON_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "protonmail.com", "mail.com", "live.com", "msn.com",
    "ymail.com", "inbox.com", "gmx.com", "fastmail.com", "zoho.com",
    "me.com", "mac.com", "comcast.net", "verizon.net", "att.net",
    "bellsouth.net", "charter.net", "earthlink.net", "cox.net", "sbcglobal.net"
]


def generate_realistic_email() -> str:
    """Generate a realistic email address using various patterns."""
    pattern_type = random.choice([
        'firstname.lastname',
        'firstnamelastname', 
        'firstname_lastname',
        'firstlast',
        'firstname',
        'firstname123',
        'flastname',
        'firstname.l'
    ])
    
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    domain = random.choice(COMMON_DOMAINS)
    
    if pattern_type == 'firstname.lastname':
        email = f"{first}.{last}@{domain}"
    elif pattern_type == 'firstnamelastname':
        email = f"{first}{last}@{domain}"
    elif pattern_type == 'firstname_lastname':
        email = f"{first}_{last}@{domain}"
    elif pattern_type == 'firstlast':
        email = f"{first[0]}{last}@{domain}"
    elif pattern_type == 'firstname':
        num = random.randint(1, 9999) if random.random() > 0.5 else ""
        email = f"{first}{num}@{domain}"
    elif pattern_type == 'firstname123':
        num = random.randint(1, 999)
        email = f"{first}{num}@{domain}"
    elif pattern_type == 'flastname':
        email = f"{first[0]}.{last}@{domain}"
    else:  # firstname.l
        email = f"{first}.{last[0]}@{domain}"
    
    return email.lower()


def hash_email(email: str) -> str:
    """Hash email using SHA-1 for privacy."""
    normalized = email.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def select_realistic_breaches(num_breaches: int) -> List[Dict]:
    """Select realistic breach combinations."""
    if num_breaches == 0:
        return []
    
    # Common breach combinations (realistic patterns)
    common_combinations = [
        ["Adobe", "LinkedIn"],  # Early 2010s combo
        ["Yahoo", "Dropbox"],   # 2012-2013 combo
        ["LinkedIn", "MySpace", "Tumblr"],  # Social media combo
        ["Adobe", "LinkedIn", "Dropbox"],  # Tech user combo
        ["Yahoo", "MySpace", "Adobe", "LinkedIn"],  # Heavy internet user
        ["Facebook", "Twitter"],  # Modern social media
        ["MyFitnessPal", "Canva"],  # Lifestyle apps
    ]
    
    # Try to use realistic combination first
    if num_breaches <= 4 and random.random() > 0.3:
        suitable_combos = [c for c in common_combinations if len(c) == num_breaches]
        if suitable_combos:
            selected_names = random.choice(suitable_combos)
            return [b for b in REALISTIC_BREACHES if b["name"] in selected_names]
    
    # Otherwise random selection
    return random.sample(REALISTIC_BREACHES, min(num_breaches, len(REALISTIC_BREACHES)))


def generate_breach_record(email: str, num_breaches: int = None) -> Dict:
    """Generate a comprehensive breach record for an email."""
    if num_breaches is None:
        # Realistic distribution
        num_breaches = random.choices(
            [0, 1, 2, 3, 4, 5],
            weights=[20, 30, 25, 15, 7, 3]  # 20% clean, rest breached
        )[0]
    
    email_hash = hash_email(email)
    
    if num_breaches == 0:
        return {
            "email_hash": email_hash,
            "total_breaches": 0,
            "breaches": [],
            "first_breach_date": None,
            "last_breach_date": None,
            "total_accounts_affected": 0
        }
    
    # Select breaches
    selected_breaches = select_realistic_breaches(num_breaches)
    
    # Sort by date
    selected_breaches.sort(key=lambda x: x["date"])
    
    # Calculate totals
    total_accounts = sum(b["accounts"] for b in selected_breaches)
    first_date = selected_breaches[0]["date"] if selected_breaches else None
    last_date = selected_breaches[-1]["date"] if selected_breaches else None
    
    return {
        "email_hash": email_hash,
        "total_breaches": len(selected_breaches),
        "breaches": selected_breaches,
        "first_breach_date": first_date,
        "last_breach_date": last_date,
        "total_accounts_affected": total_accounts
    }


def create_sqlite_database(db_path: Path, force_recreate: bool = False):
    """Create SQLite database with optimized schema."""
    if db_path.exists() and force_recreate:
        db_path.unlink()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table with optimized schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS breached_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_hash TEXT UNIQUE NOT NULL,
            total_breaches INTEGER NOT NULL DEFAULT 0,
            first_breach_date TEXT,
            last_breach_date TEXT,
            total_accounts_affected INTEGER,
            breach_details TEXT,  -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for fast lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_email_hash 
        ON breached_emails(email_hash)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_total_breaches 
        ON breached_emails(total_breaches)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✓ SQLite database created: {db_path}")


def insert_breach_records(db_path: Path, records: List[Dict], batch_size: int = 1000):
    """Insert breach records into SQLite database in batches."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        for record in batch:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO breached_emails 
                    (email_hash, total_breaches, first_breach_date, last_breach_date, 
                     total_accounts_affected, breach_details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    record["email_hash"],
                    record["total_breaches"],
                    record["first_breach_date"],
                    record["last_breach_date"],
                    record["total_accounts_affected"],
                    json.dumps(record["breaches"])
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting record: {e}")
        
        conn.commit()
        
        if (i + batch_size) % 10000 == 0:
            print(f"  Inserted {inserted:,} records...")
    
    conn.close()
    print(f"✓ Total records inserted: {inserted:,}")


def generate_comprehensive_dataset(num_records: int = 100000, db_path: Path = None) -> int:
    """
    Generate comprehensive breach dataset with 100,000+ records.
    
    Args:
        num_records: Number of breach records to generate (default 100,000)
        db_path: Path to SQLite database file
        
    Returns:
        Number of records generated
    """
    print(f"\n{'='*70}")
    print(f"🔥 GENERATING COMPREHENSIVE BREACH DATASET")
    print(f"{'='*70}")
    print(f"Target records: {num_records:,}")
    print(f"This will take a few minutes...")
    
    if db_path is None:
        db_path = Path(__file__).resolve().parents[2] / "data" / "breaches.db"
    
    # Create database
    db_path.parent.mkdir(parents=True, exist_ok=True)
    create_sqlite_database(db_path, force_recreate=True)
    
    # Generate required test emails first
    test_emails = {
        "test@example.com": 3,
        "user@gmail.com": 2,
        "admin@yahoo.com": 4,
        "pwned@hotmail.com": 5,
        "safe@cyberguardx.com": 0
    }
    
    print(f"\n📧 Generating {len(test_emails)} required test emails...")
    test_records = []
    for email, num_breaches in test_emails.items():
        record = generate_breach_record(email, num_breaches)
        test_records.append(record)
        status = f"{num_breaches} breaches" if num_breaches > 0 else "CLEAN"
        print(f"  ✓ {email:30} → {status}")
    
    # Insert test emails
    insert_breach_records(db_path, test_records)
    
    # Generate remaining records
    print(f"\n📊 Generating {num_records - len(test_emails):,} random email patterns...")
    
    records = []
    emails_used = set(test_emails.keys())
    
    for i in range(num_records - len(test_emails)):
        # Generate unique email
        attempts = 0
        while attempts < 10:
            email = generate_realistic_email()
            if email not in emails_used:
                emails_used.add(email)
                break
            attempts += 1
        
        # Generate breach record
        record = generate_breach_record(email)
        records.append(record)
        
        # Insert in batches
        if len(records) >= 5000:
            insert_breach_records(db_path, records)
            records = []
        
        # Progress indicator
        if (i + 1) % 10000 == 0:
            print(f"  Generated {i + 1:,}/{num_records - len(test_emails):,} records...")
    
    # Insert remaining records
    if records:
        insert_breach_records(db_path, records)
    
    # Get statistics
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM breached_emails")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches = 0")
    clean = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM breached_emails WHERE total_breaches > 0")
    breached = cursor.fetchone()[0]
    
    conn.close()
    
    # Summary
    print(f"\n{'='*70}")
    print(f"✅ DATASET GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Database: {db_path}")
    print(f"Total records: {total:,}")
    print(f"Breached emails: {breached:,} ({breached/total*100:.1f}%)")
    print(f"Clean emails: {clean:,} ({clean/total*100:.1f}%)")
    print(f"Database size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\n🎯 Test emails ready:")
    for email in test_emails:
        print(f"  • {email}")
    print(f"{'='*70}\n")
    
    return total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive breach dataset')
    parser.add_argument('--size', type=int, default=100000,
                       help='Number of records to generate (default: 100,000)')
    parser.add_argument('--db', type=str, default=None,
                       help='Database path (default: backend/data/breaches.db)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db) if args.db else None
    generate_comprehensive_dataset(num_records=args.size, db_path=db_path)
