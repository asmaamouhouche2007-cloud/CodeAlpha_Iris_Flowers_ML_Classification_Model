CREATE TABLE IF NOT EXISTS inferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SepalLengthCm REAL,
    SepalWidthCm REAL,
    PetalLengthCm REAL,
    PetalWidthCm REAL,
    predicted_species TEXT,
    user_feedback TEXT
    )