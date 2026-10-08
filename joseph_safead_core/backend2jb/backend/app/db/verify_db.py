import os
import sqlite3
import json
import sys
sys.path.append(os.getcwd())

def verify_safead_database(db_path: str = "safead.db"):
    print("=" * 65)
    print("      SAFEAD AI (SAFE-VISION) DATABASE AUDIT REPORT          ")
    print("=" * 65)
    
    if not os.path.exists(db_path):
        print(f"[FAIL] Database file '{db_path}' does not exist on disk!")
        return
        
    print(f"[OK] Database File Found: {os.path.abspath(db_path)}")
    print(f"[OK] Database Disk Size : {os.path.getsize(db_path) / 1024:.2f} KB")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"[OK] Total Relational Tables: {len(tables)} -> {tables}")
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM '{table}';")
        count = cursor.fetchone()[0]
        
        print("-" * 65)
        print(f"TABLE: [{table.upper()}] (Total Records: {count})")
        print(f"{'ID':<4} {'Column Name':<25} {'Data Type':<15} {'Nullable':<10} {'PK':<5}")
        print("-" * 65)
        for col in columns:
            cid, cname, ctype, notnull, dflt, pk = col
            nullable = "No" if notnull else "Yes"
            is_pk = "Yes" if pk else "No"
            print(f"{cid:<4} {cname:<25} {ctype:<15} {nullable:<10} {is_pk:<5}")
            
    conn.close()
    
    # -------------------------------------------------------------
    # FAISS Vector Exemplar Database Verification
    # -------------------------------------------------------------
    print("=" * 65)
    print("     FAISS VECTOR EMBEDDING EXEMPLAR DATABASE AUDIT           ")
    print("=" * 65)
    try:
        from ai.retrieval.faiss_retriever import retrieve_similar_exemplar, EXEMPLARS, HAS_FAISS, faiss_index
        print("[OK] FAISS Vector Retriever Module Loaded Successfully.")
        print(f"[OK] Total Exemplar Vectors Indexed: {len(EXEMPLARS)}")
        print(f"[OK] FAISS Index Active Status   : {'Enabled (faiss IndexFlatL2)' if HAS_FAISS else 'Lightweight Vector Search'}")
        print("\n[Exemplar Vector Database Case Records]:")
        for i, meta in enumerate(EXEMPLARS):
            print(f"  [{i+1}] Title: '{meta['title']}' | Policy: {meta['policy']} | Decision: {meta['decision']}")
            
        test_query = retrieve_similar_exemplar("casino jackpot bet win cash")
        print(f"\n[OK] Sample FAISS Nearest Neighbor Retrieval Test Query ('casino jackpot bet win cash'):")
        print(f"     Matched Exemplar: '{test_query['title']}' | Distance: {test_query['distance']} | Decision: {test_query['decision']}")
    except Exception as e:
        print(f"[FAIL] Could not verify FAISS Vector Database: {e}")
        
    print("=" * 65)

if __name__ == "__main__":
    verify_safead_database()
