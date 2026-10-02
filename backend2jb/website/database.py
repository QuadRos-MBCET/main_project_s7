import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safead.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('advertiser', 'admin', 'social_user'))
    )
    """)

    # 2. Advertisements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Advertisements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        advertiser_id INTEGER,
        caption TEXT,
        file_path TEXT NOT NULL,
        status TEXT DEFAULT 'under_review' CHECK(status IN ('approved', 'rejected', 'under_review')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(advertiser_id) REFERENCES Users(id)
    )
    """)

    # 3. MediaFiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MediaFiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        file_type TEXT CHECK(file_type IN ('video', 'image')),
        duration_sec REAL,
        width INTEGER,
        height INTEGER,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id)
    )
    """)

    # 4. OCRResults Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OCRResults (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        extracted_text TEXT,
        language TEXT,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id)
    )
    """)

    # 5. PolicyRules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PolicyRules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        age_restriction INTEGER DEFAULT 0
    )
    """)

    # 6. ModelPredictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ModelPredictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        modality TEXT CHECK(modality IN ('visual', 'ocr', 'speech', 'nlp')),
        prediction_label TEXT,
        score REAL,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id)
    )
    """)

    # 7. RiskScores Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RiskScores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        visual_score REAL DEFAULT 0,
        ocr_score REAL DEFAULT 0,
        speech_score REAL DEFAULT 0,
        final_score REAL DEFAULT 0,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id)
    )
    """)

    # 8. AgeProfiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AgeProfiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        method TEXT CHECK(method IN ('facial', 'behavioral')),
        prediction_class TEXT CHECK(prediction_class IN ('Child', 'Not a Child')),
        confidence REAL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
    """)

    # 9. HumanReviews Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS HumanReviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        reviewer_id INTEGER,
        action TEXT CHECK(action IN ('approve', 'reject', 'restrict')),
        notes TEXT,
        reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id),
        FOREIGN KEY(reviewer_id) REFERENCES Users(id)
    )
    """)

    # 9.5. ModerationResults Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ModerationResults (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        final_decision TEXT,
        explanation TEXT,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id)
    )
    """)


    # 10. AuditLogs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AuditLogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        trigger_user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        model_version TEXT,
        final_decision TEXT,
        log_details TEXT,
        FOREIGN KEY(ad_id) REFERENCES Advertisements(id),
        FOREIGN KEY(trigger_user_id) REFERENCES Users(id)
    )
    """)

    conn.commit()

    # Seed Default Users (Password Hash represents a simple seed for testing)
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("advertiser1", "hash_advertiser", "advertiser"),
            ("admin1", "hash_admin", "admin"),
            ("guest_user", "hash_guest", "social_user")
        ]
        cursor.executemany("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)", default_users)

    # Seed Default Policies
    cursor.execute("SELECT COUNT(*) FROM PolicyRules")
    if cursor.fetchone()[0] == 0:
        default_policies = [
            ("Adult/Sexual Content", "Restricts explicit or sexually suggestive imagery/text.", 18),
            ("Child Safety", "Blocks content containing child exploitation or harmful themes targeting children.", 0),
            ("Violence", "Flags blood, gore, violence, or dangerous weapons.", 18),
            ("Gambling", "Restricts betting platforms, lottery, and commercial gambling sites.", 18),
            ("Alcohol/Tobacco", "Regulates ads promoting alcohol products or vaping/tobacco items.", 18),
            ("Drugs", "Strictly bans illicit drugs, pharmaceutical sales infractions, and narcotics.", 18),
            ("Hate/Abusive Content", "Flags harassment, hate speech, bullying, and racial/ethnic abuse.", 13),
            ("Misleading Advertisement", "Flags deceptive claims, scam financial products, and fake giveaways.", 0),
            ("Other Age-Restricted Content", "Catch-all policy for generalized restricted products.", 18)
        ]
        cursor.executemany("INSERT INTO PolicyRules (name, description, age_restriction) VALUES (?, ?, ?)", default_policies)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully at:", DB_PATH)
