import sqlite3
conn = sqlite3.connect('losazules.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS losazules(
    equipo_id TEXT,
    modelo TEXT,
    timestamp TEXT,
    tiempo_ciclo_min REAL,
    carga_ton REAL
)""")

todos_equipos = [
    ('CAM-001', 'Mercedes-Benz Arocs', '2026-07-01 08:00:00', 32.5, 175.0),
    ('CAM-002', 'CAT 793F', '2026-07-01 08:00:00', 32.5, 175.0),
    ('CAM-003', 'Komatsu 930E', '2026-07-01 08:15:00', 41.2, 168.3),
    ('CAM-004', 'Liebherr T284', '2026-07-01 08:30:00', 29.8, 182.1),
]

c.executemany("INSERT INTO losazules VALUES (?, ?, ?, ?, ?)", todos_equipos)
c.execute("SELECT * FROM losazules")
x = c.fetchall()
for i in x:
        print(i)

conn.commit()
conn.close()
print("OK")