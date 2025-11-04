
# data_pipeline.py
# Pipeline to download metadata from The Met Collection API, clean, preprocess, and visualize.
# Usage: python data_pipeline.py --query "vase" --n 100
import requests, csv, os, argparse, math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

MET_SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1/search"
MET_OBJECT = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"

def fetch_object_ids(q, hasImages=True):
    params = {"q": q, "hasImages": str(hasImages).lower()}
    r = requests.get(MET_SEARCH, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("objectIDs", []) or []

def fetch_object(obj_id):
    r = requests.get(MET_OBJECT.format(obj_id), timeout=30)
    r.raise_for_status()
    return r.json()

def collect(q, n=200, hasImages=True):
    ids = fetch_object_ids(q, hasImages=hasImages)
    ids = ids[:n]
    rows = []
    for i, oid in enumerate(ids):
        try:
            obj = fetch_object(oid)
            row = {
                "objectID": oid,
                "title": obj.get("title"),
                "artistDisplayName": obj.get("artistDisplayName"),
                "culture": obj.get("culture"),
                "period": obj.get("period") or obj.get("objectDate"),
                "medium": obj.get("medium"),
                "dimensions": obj.get("dimensions"),
                "classification": obj.get("classification"),
                "primaryImage": obj.get("primaryImage"),
                "isPublicDomain": obj.get("isPublicDomain"),
                "objectURL": obj.get("objectURL")
            }
            rows.append(row)
        except Exception as e:
            print(f"Failed {oid}: {e}")
    df = pd.DataFrame(rows)
    return df

def clean(df):
    # simple cleaning: normalize missing, extract century if possible
    df = df.copy()
    df['period_clean'] = df['period'].fillna('').str.strip().replace('', None)
    # attempt to extract earliest year from period or objectDate fields (very heuristic)
    def extract_year(s):
        if not s or not isinstance(s, str):
            return None
        import re
        m = re.search(r'(\d{3,4})', s)
        if m:
            y = int(m.group(1))
            return y
        return None
    df['year'] = df['period_clean'].apply(extract_year)
    return df

def visualize(df, outdir='out'):
    os.makedirs(outdir, exist_ok=True)
    sns.set(style='whitegrid')
    # classification counts (bar)
    plt.figure(figsize=(10,6))
    top_classes = df['classification'].fillna('Unknown').value_counts().nlargest(10)
    sns.barplot(x=top_classes.values, y=top_classes.index)
    plt.title('Top Classifications in Sample')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'bar_top_classifications.png'))
    plt.close()

    # material (medium) word-length histogram (proxy)
    plt.figure(figsize=(10,5))
    df['medium_len'] = df['medium'].fillna('').str.len()
    sns.histplot(df['medium_len'], bins=20)
    plt.title('Distribution of medium text length (proxy for detail)')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'hist_medium_len.png'))
    plt.close()

    # year histogram (where available)
    plt.figure(figsize=(10,5))
    years = df['year'].dropna().astype(int)
    if len(years)>0:
        sns.histplot(years, bins=15)
        plt.title('Distribution of Extracted Years (heuristic)')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'hist_years.png'))
        plt.close()

    # heatmap: two-way pivot between classification and whether public domain
    pivot = pd.crosstab(df['classification'].fillna('Unknown'), df['isPublicDomain'])
    plt.figure(figsize=(10,8))
    sns.heatmap(pivot, annot=True, fmt='d', cmap='YlGnBu')
    plt.title('Heatmap: Classification vs Public Domain flag')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'heatmap_class_publicdomain.png'))
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='vase')
    parser.add_argument('--n', type=int, default=200)
    parser.add_argument('--out', default='met_sample.csv')
    args = parser.parse_args()
    df = collect(args.query, args.n)
    df = clean(df)
    df.to_csv(args.out, index=False)
    visualize(df, outdir='visualizations')
    print('Done. Saved', args.out)
