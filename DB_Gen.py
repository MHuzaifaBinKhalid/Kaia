import os
import pandas as pd
import sqlite3

# -----------------------------
# Paths
# -----------------------------
df_folder = "DataFrame"
db_folder = "DataBase"
os.makedirs(db_folder, exist_ok=True)
csv_path = os.path.join(df_folder, "meta_with_media.csv")
db_path = os.path.join(db_folder, "posts_star.db")

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv(csv_path)

# -----------------------------
# Dimension Tables
# -----------------------------
# dim_post
dim_post = df[['post_id', 'caption', 'type', 'timestamp']].drop_duplicates()

# dim_media
media_rows = []
for _, row in df.iterrows():
    if pd.notnull(row['img_path']):
        for img in eval(row['img_path']):
            media_rows.append([row['post_id'], 'Image', img])
    if pd.notnull(row['video_path']):
        for vid in eval(row['video_path']):
            media_rows.append([row['post_id'], 'Video', vid])

dim_media = pd.DataFrame(media_rows, columns=['post_id', 'media_type', 'file_path'])
dim_media['media_id'] = range(1, len(dim_media)+1)

# -----------------------------
# Fact Table
# -----------------------------
fact_post_metrics = df[['post_id', 'likes', 'comments']].copy()

# -----------------------------
# Save to SQLite
# -----------------------------
conn = sqlite3.connect(db_path)
for table in ['dim_post', 'dim_media', 'fact_post_metrics']:
    conn.execute(f"DROP TABLE IF EXISTS {table};")  # Clean slate

dim_post.to_sql('dim_post', conn, if_exists='replace', index=False)
dim_media.to_sql('dim_media', conn, if_exists='replace', index=False)
fact_post_metrics.to_sql('fact_post_metrics', conn, if_exists='replace', index=False)

# Indexes for fast querying
conn.execute("CREATE INDEX idx_post_id_post ON dim_post(post_id);")
conn.execute("CREATE INDEX idx_post_id_media ON dim_media(post_id);")
conn.execute("CREATE INDEX idx_post_id_fact ON fact_post_metrics(post_id);")

conn.commit()
conn.close()
print("✅ Star Schema Data Warehouse created: posts_star.db")
