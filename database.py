import sqlite3


def get_all_specialties():
    conn = sqlite3.connect('universities.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT specialty FROM universities ORDER BY specialty")
    specialties = [row[0] for row in cursor.fetchall()]
    conn.close()
    return specialties


def get_universities_by_specialty(specialty, limit=8):
    conn = sqlite3.connect('universities.db')
    cursor = conn.cursor()

    # Сначала московские вузы, потом остальные, сортировка по проходному баллу
    cursor.execute(
        """
        SELECT name, city, passing_score, link FROM universities 
        WHERE specialty = ? 
        ORDER BY 
            CASE WHEN city = 'Москва' THEN 1 ELSE 2 END,
            passing_score DESC
        LIMIT ?
        """,
        (specialty, limit)
    )
    universities = cursor.fetchall()
    conn.close()
    return universities


def get_specialty_count():
    conn = sqlite3.connect('universities.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT specialty) FROM universities")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_universities():
    conn = sqlite3.connect('universities.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM universities")
    count = cursor.fetchone()[0]
    conn.close()
    return count