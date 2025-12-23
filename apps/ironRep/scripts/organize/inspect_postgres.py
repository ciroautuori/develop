#!/usr/bin/env python3
"""
PostgreSQL Inspector - Verifica database produzione
Connessione al database PostgreSQL di IronRep
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

def get_connection():
    """Connessione al database PostgreSQL"""
    try:
        # Connection details dal container backend
        conn = psycopg2.connect(
            host='postgres',
            port=5432,
            database='ironrep',
            user='ironrep',
            password='ironrep_password',
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return None

def inspect_tables():
    """Ispeziona tutte le tabelle del database"""

    print("🐘 PostgreSQL Inspector - IronRep Database Analysis")
    print("=" * 60)
    print(f"🕐 Inspection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Production: https://ironrep.it")

    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Lista tutte le tabelle
        cursor.execute("""
            SELECT table_name,
                   (SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        print(f"\n📊 Tables Found: {len(tables)}")
        print("-" * 40)

        for table in tables:
            table_name = table['table_name']
            column_count = table['column_count']

            # Count records
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            record_count = cursor.fetchone()['count']

            print(f"📋 {table_name}")
            print(f"   Columns: {column_count} | Records: {record_count:,}")

            # Show sample data for important tables
            if record_count > 0 and table_name in ['users', 'pain_assessments', 'workout_sessions', 'exercises']:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                samples = cursor.fetchall()

                print(f"   Sample Data:")
                for i, sample in enumerate(samples):
                    print(f"     {i+1}. {dict(sample)}")
                print()

        # Analisi dettagliata utenti
        print("\n👥 Users Analysis:")
        print("-" * 30)
        cursor.execute("""
            SELECT COUNT(*) as total_users,
                   COUNT(CASE WHEN is_onboarded = true THEN 1 END) as onboarded_users,
                   COUNT(CASE WHEN is_active = true THEN 1 END) as active_users
            FROM users;
        """)

        user_stats = cursor.fetchone()
        print(f"   Total Users: {user_stats['total_users']}")
        print(f"   Onboarded: {user_stats['onboarded_users']}")
        print(f"   Active: {user_stats['active_users']}")

        # Analisi sessioni recenti
        print("\n💪 Recent Activity:")
        print("-" * 25)
        cursor.execute("""
            SELECT COUNT(*) as recent_sessions,
                   MAX(date) as last_session
            FROM workout_sessions
            WHERE date >= NOW() - INTERVAL '7 days';
        """)

        activity = cursor.fetchone()
        print(f"   Sessions (7 days): {activity['recent_sessions']}")
        print(f"   Last Session: {activity['last_session']}")

        # Analisi check-in dolore
        print("\n🩺 Pain Check-ins:")
        print("-" * 22)
        cursor.execute("""
            SELECT COUNT(*) as total_checkins,
                   AVG(pain_level) as avg_pain,
                   MAX(date) as last_checkin
            FROM pain_assessments;
        """)

        pain_stats = cursor.fetchone()
        print(f"   Total Check-ins: {pain_stats['total_checkins']}")
        print(f"   Average Pain: {pain_stats['avg_pain']:.1f}/10")
        print(f"   Last Check-in: {pain_stats['last_checkin']}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error during inspection: {e}")
        conn.close()
        return False

def main():
    """Main inspection"""

    success = inspect_tables()

    if success:
        print("\n✅ PostgreSQL inspection completed!")
        print("\n🔧 pgadmin Setup Instructions:")
        print("   1. Install pgadmin: sudo pacman -S pgadmin4")
        print("   2. Launch pgadmin: pgadmin4")
        print("   3. Add new server:")
        print("      - Name: IronRep Production")
        print("      - Host: localhost")
        print("      - Port: 5432")
        print("      - Database: ironrep")
        print("      - Username: ironrep")
        print("      - Password: ironrep_password")
        print("      - SSL mode: disable")
        print("\n🌐 Alternative: pgadmin web interface")
        print("   Access: http://localhost:5050 (if running)")
    else:
        print("\n❌ PostgreSQL inspection failed!")
        print("   Check: docker ps | grep postgres")

if __name__ == "__main__":
    main()
