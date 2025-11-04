
# Antique Object Age Predictor — Data Collection & Visualization Report

## Dataset
- Source: The Metropolitan Museum of Art Open Access API (https://collectionapi.metmuseum.org/)
- Sample: `sample_met_subset.csv` (10 records). Full dataset can be collected using `data_pipeline.py` which fetches metadata via the Met public API.

## What I collected in the sample
Saved `sample_met_subset.csv` with fields: objectID, title, artist, culture, period, medium, dimensions, classification, repositoryURL.
Preview of the sample (first 10 rows) is attached in the project folder.

## Cleaning & Preprocessing steps (implemented in `data_pipeline.py`)
1. Fetch object metadata via `/public/collection/v1/search` and `/objects/{objectID}`.
2. Keep fields: title, artistDisplayName, culture, period/objectDate, medium, dimensions, classification, primaryImage, isPublicDomain, objectURL.
3. Normalize missing values; create `period_clean` and heuristically extract a numeric `year` when possible (regex for first 3-4 digit number in period text).
4. Save cleaned CSV and generate visualizations (bar chart, histogram, heatmap, year histogram).

## Visualizations produced (files)
- `visualizations/bar_top_classifications.png` — Top 10 object classifications (bar chart)
- `visualizations/hist_medium_len.png` — Histogram of medium text length (proxy)
- `visualizations/hist_years.png` — Histogram of extracted years (heuristic)
- `visualizations/heatmap_class_publicdomain.png` — Heatmap comparing classification vs public-domain flag

## Observations (from sample & expected with larger data)
- The Met collection contains a long tail of classifications; ceramics, paintings, and textiles often appear frequently in queries for 'vase' or similar terms.
- Many objects have textual date ranges (e.g., '17th–18th century') rather than precise years; heuristic year extraction will capture earliest numeric year where present but misses many.
- Public domain flag correlates with older objects but also depends on provenance and rights — heatmap helps inspect which classifications are heavily in public domain.
- Medium text length varies — more complex media descriptions often indicate composite objects or more detailed provenance/technique notes.

## How to reproduce full pipeline
1. Install requirements:
```
pip install pandas requests matplotlib seaborn
```
2. Run the pipeline to fetch N objects (e.g. 500) and generate visualizations:
```
python data_pipeline.py --query "vase" --n 500 --out met_vases_500.csv
```
3. Open the `visualizations` folder for charts and inspect the CSV.

## Files included in submission
- CODE_FILE: `data_pipeline.py`
- DATASET: `sample_met_subset.csv` (10-record sample, real entries from The Met open data)
- REPORT: `REPORT.md` (this file)

## Notes & next steps
- For robust dating you will need curated labels (expert annotations) and possibly fine-tuned vision models + provenance records.
- The pipeline can be extended to download images (primaryImage) and compute visual features (color histograms, textures) for ML models.
- Consider enriching with other museum APIs (British Museum, Rijksmuseum, Getty) and merging by classification/culture for broader geographic coverage.
