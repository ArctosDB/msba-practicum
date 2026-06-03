# Arctos Dashboard Update Tool

Update the Arctos Tableau dashboard with the latest data in a few simple steps.

---

## What This Tool Does

Each time you run it, the tool automatically:
- Converts the latest Arctos data export into Tableau's format
- Updates the portal summary (Summary tab charts)
- Updates the main dataset (Taxonomic Breakdown, Spatial Analysis, Guid Prefix Map)
- Updates the global statistics (Collections, Institutions, Specimens count)
- Patches everything directly into the `.twbx` file — no manual Tableau steps needed

---

## First-Time Setup

### Requirements
- Python 3.8 or higher — check by running:
  ```
  python3 --version
  ```
  If not installed, download from [python.org](https://www.python.org/downloads/)

### Steps

You start with just two files: `setup.py` and `arctos_update.py`. Place them anywhere on your computer (e.g. Desktop).

**1. Open Terminal**

On Mac: press `Cmd + Space`, type `Terminal`, press Enter.

**2. Navigate to where you saved the files**

```bash
cd ~/Desktop
```

Tip: you can drag the folder into Terminal instead of typing the path.

**3. Run the setup script**

```bash
python3 setup.py
```

This will:
- Check your Python version
- Install all required packages (`pandas`, `tableauhyperapi`)
- Create the `arctos_update/` project folder with subfolders `data/input/`, `data/output/`, and `logs/`
- Copy `arctos_update.py` into the new folder

You only need to do this once.

**4. Place the required files in the right locations**

After setup completes, copy the following files:

- Most recent Arctos Tableau `.twbx` → into `arctos_update/` (same folder as `arctos_update.py`)
- Latest Arctos data export `.csv.gz` → into `arctos_update/data/input/`
- Latest `cache_sysstats_global_YYYY-MM-DD.csv` → into `arctos_update/data/input/`

---

## Folder Structure

After setup, your folder should look like this:

```
arctos_update/
├── arctos_update.py                   ← main script
├── setup.py                           ← first-time setup
├── [most_recent].twbx                 ← Tableau workbook (must be here)
├── data/
│   ├── input/                         ← PUT YOUR INPUT FILES HERE
│   │   ├── [arctos_export].csv.gz
│   │   └── cache_sysstats_global_YYYY-MM-DD.csv
│   └── output/                        ← generated files (auto-created)
└── logs/                              ← run logs (auto-created)
```

---

## How to Update (Every Time)

### Step 1 — Add the input files

Place both of the following files into `data/input/`:

| File | Description |
|------|-------------|
| Latest Arctos data export `.csv.gz` | Compressed CSV export from Arctos |
| `cache_sysstats_global_YYYY-MM-DD.csv` | Latest global statistics CSV |

> If there are multiple `.gz` files in the folder, the script automatically uses the most recent one.

### Step 2 — Open Terminal and navigate to the folder

```bash
cd ~/Desktop/arctos_update
```

### Step 3 — Run the update script

```bash
python3 arctos_update.py
```

The script will print progress as it runs. It takes about **8–10 minutes** to complete. You will see output like:

```
Arctos Dashboard Update Tool (ZIP / GZ)
========================================
Checking...
  ✓ Input file: [arctos_export].csv.gz
  ✓ Format: .GZ
  ✓ Output: arctos_main_YYYY_MM_DD.hyper

Processing CSV in chunks of 100,000 rows...
  Chunk 1: 100,000 rows  (total: 100,000)
  Chunk 2: 100,000 rows  (total: 200,000)
  ...

✅ Portal Summary CSV: portal_summary_YYYY_MM_DD.csv
📦 Updating embedded CSV in: [workbook].twbx
📦 Updating embedded Hyper in: [workbook].twbx
📊 Updating cache stats from: cache_sysstats_global_YYYY-MM-DD.csv
```

### Step 4 — Open Tableau

1. **Fully close** Tableau if it is already open (Cmd + Q on Mac)
2. **Reopen** the `.twbx` file from the `arctos_update/` folder

All dashboard tabs will now show the latest data — no manual refresh needed.

---

## What Gets Updated

| Dashboard Tab | Updated? |
|---------------|----------|
| Summary (bar chart + pie chart) | ✅ Yes |
| Porta-Distributionl | ✅ Yes |
| Spatial Analysis | ✅ Yes |
| Taxonomic Breakdown | ✅ Yes |
| Guid Prefix Map | ✅ Yes |
| Global stats (collections, institutions, specimens, etc.) | ✅ Yes |

---

## Troubleshooting

**`python3: command not found`**
→ Python is not installed. Download it from [python.org](https://www.python.org/downloads/) and rerun setup.

**`No such file or directory` when running the script**
→ You are not in the right folder. Run `cd ~/Desktop/arctos_update` first, then try again.

**Script can't find the input file**
→ Make sure the Arctos data export `.csv.gz` is inside `data/input/`, not the root folder or anywhere else.

**`No .twbx file found` warning**
→ Move the most recent `.twbx` file into the `arctos_update/` folder (same level as `arctos_update.py`).

**Tableau still shows old data after running**
→ You must fully close and reopen Tableau — do not just click refresh. Press `Cmd + Q` to quit, then reopen the `.twbx` file.

**Script fails with an error**
→ Check the log file inside the `logs/` folder for details. The log is named `update_YYYY_MM_DD.log`.
