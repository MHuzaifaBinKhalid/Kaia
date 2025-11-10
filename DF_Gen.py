import os
import json
import pandas as pd

# -----------------------
# Folders
# -----------------------
meta_folder = os.path.join("dataset", "metadata")
img_folder = os.path.join("dataset", "images")
video_folder = os.path.join("dataset", "videos")
df_folder = ""

os.makedirs(df_folder, exist_ok=True)

# -----------------------
# Load JSON metadata
# -----------------------
data = []
meta_files = [f for f in os.listdir(meta_folder) if f.endswith(".json")]
for file in meta_files:
    with open(os.path.join(meta_folder, file), 'r', encoding='utf-8') as f:
        post_data = json.load(f)
        data.append(post_data)

print(f"✅ Loaded {len(data)} posts from {len(meta_files)} metadata files.")

# -----------------------
# Convert to DataFrame & clean
# -----------------------
df = pd.DataFrame(data)
df['caption'] = df['caption'].fillna('')
df['likes'] = df['likes'].fillna(0).astype(int)
df['comments'] = df['comments'].fillna(0).astype(int)
df['type'] = df['type'].fillna('Unknown')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df.drop_duplicates(subset='post_id', inplace=True)

print(f"✅ DataFrame created with {len(df)} unique posts.")

# -----------------------
# Map images & videos
# -----------------------
img_files = [f for f in os.listdir(img_folder) if f.endswith(".jpg")]
video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

def map_files(post_id, files, folder):
    post_id = post_id.strip()
    matched = [os.path.join(folder, f) for f in files if f.startswith(post_id)]
    return matched if matched else None

df['img_path'] = df['post_id'].apply(lambda x: map_files(x, img_files, img_folder))
df['video_path'] = df['post_id'].apply(lambda x: map_files(x, video_files, video_folder))

print(f"✅ Mapped images & videos for posts.")
print(f"   Posts with images: {df['img_path'].notnull().sum()}")
print(f"   Posts with videos: {df['video_path'].notnull().sum()}")

# -----------------------
# Save to CSV
# -----------------------
csv_path = os.path.join(df_folder, "meta_with_media.csv")
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"✅ DataFrame saved to {csv_path}")
