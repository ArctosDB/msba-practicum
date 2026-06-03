#!/usr/bin/env python3
"""
Arctos Dashboard Update Tool (supports ZIP and GZ formats)

Supported formats:
- .zip (ZIP-compressed CSV)
- .gz  (GZIP-compressed CSV)
- .tar.gz (TAR+GZIP-compressed CSV)

Usage:
    python arctos_update_FINAL.py

    The script will automatically:
    1. Search for a ZIP or GZ file in data/input/
    2. Detect the format
    3. Convert to Hyper format
    4. Save to data/output/
    5. Generate a portal summary CSV that replaces Updated_Portal.xlsx:
       - portal_summary_YYYY_MM_DD.csv

    The portal_summary CSV feeds BOTH Summary tab charts:
      - "Porta-Distributionl" worksheet → NUMBER OF RECORDS bar chart
        Rows: F4 (Guid Prefix) / F11 (Records)   Cols: SUM(F7 = Rcnt)
      - "Pie chart" worksheet → % DISTRIBUTION pie chart
        Measure: F8 (Rcnt Percentage)

    Column mapping to Updated_Portal.xlsx (F1–F11):
      F1  Collection Id       sequential integer
      F2  Collection          collection_cde          (Arctos CSV / HTML: collection)
      F3  Institution         full institution name   (mapped via INSTITUTION_FULL_NAMES; fallback to acronym)
      F4  Guid Prefix         guid_prefix             (Arctos CSV / HTML: guid_prefix)
      F5  Guid Prefix First   guid_prefix token[0]   (part before ":")
      F6  Guid Prefix Split1  guid_prefix token[1]   (part after ":")
      F7  Rcnt                COUNT per guid_prefix   (bar chart measure)
      F8  Rcnt Percentage     Rcnt / total * 100      (pie chart measure, integer)
      F9  Portal Name         full institution name   (mapped via INSTITUTION_FULL_NAMES; fallback to acronym)
      F10 Type                collection_cde          (best available proxy)
      F11 Records             same as Rcnt            (bar chart row label)
"""

import sys
import os
import zipfile
import gzip
import tarfile
import math
import pandas as pd
import io
from pathlib import Path
from datetime import datetime
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, Inserter, TableName

# ============================================================================
# Configuration
# ============================================================================

# 34 columns to extract
UNIFIED_COLUMNS = [
    'cat_num', 'cataloged_item_type', 'collecting_event_id',
    'collecting_method', 'collecting_source', 'collection_cde',
    'collectors', 'country', 'county', 'dec_lat', 'dec_long',
    'family', 'genbanknum', 'genus', 'guid_prefix',
    'identification_id', 'institution_acronym', 'kingdom',
    'locality_id', 'media', 'phylclass', 'phylorder', 'phylum',
    'scientific_name', 'species', 'state_prov', 'subfamily',
    'suborder', 'subspecies', 'subtribe', 'superfamily',
    'superorder', 'tribe', 'year'
]

# Chunk size for streaming reads
CHUNK_SIZE = 100000

# ============================================================================
# Institution acronym → full name mapping
# Sourced from the Update_portals.hyper embedded in the Tableau workbook.
# F3 (Institution) and F9 (Portal_Name) use full names, matching the
# original Updated_Portal.xlsx behavior and the Tableau Institution filter.
# Falls back to the raw acronym for any code not listed here.
# ============================================================================
INSTITUTION_FULL_NAMES = {
    # --- A ---
    'ACBC':   'Arkansas Center for Biodiversity Collections',
    'ACUNHC': 'Abilene Christian University Natural History Collection',
    'ALMNH':  'Alabama Museum of Natural History',
    'ANSP':   'Academy of Natural Sciences of Philadelphia (Drexel University)',
    'APSU':   'Austin Peay State University',
    'Arctos': 'Arctos Consortium',
    'ASNHC':  'Angelo State Natural History Collections',
    'ASUMZ':  'Arkansas State University Museum of Zoology',
    # --- B ---
    'BELL':   'Bell Museum, University of Minnesota',
    'BIOAPT': 'Biomonitoring in Aquatic Protected Areas and Territories (BIOAPT)',
    'BSUNH':  'Bridgewater State University Natural History',
    'BYU':    'Brigham Young University Museum of Life Science',
    # --- C ---
    'CDSC':   'California Desert Studies Center',
    'CHAS':   'Chicago Academy of Sciences',
    'COA':    'College of the Atlantic',
    'CRCM':   'Cosumnes River College Museum',
    'CSULB':  'California State University, Long Beach',
    # --- D ---
    'DGR':    'Don Gardner Reptiles Collection (MSB)',
    'DMNS':   'Denver Museum of Nature & Science (DMNS)',
    # --- F ---
    'FHSM':   'Sternberg Museum of Natural History (FHSM)',
    # --- H ---
    'HMCM':   'Huron Mountain Club Mammal Collection',
    'HSU':    'Cal Poly Humboldt Vertebrate Museum',
    'HSUVM':  'Cal Poly Humboldt Vertebrate Museum',
    'HWML':   'Harold W. Manter Laboratory of Parasitology (HWML)',
    # --- J ---
    'JFBM':   'J. F. Bell Museum',
    'JSNM':   'Jurica-Suchy Nature Museum (Benedictine University)',
    # --- K ---
    'KNWR':   'Kenai National Wildlife Refuge (KNWR)',
    'KSB':    'Kansas Biological Survey (KSB)',
    'KWP':    'Kenelm W. Philip Lepidoptera Collection (KWP)',
    # --- L ---
    'LINGU':  'Lingnan University Natural History Collections',
    'LU':     'Lingnan University',
    # --- M ---
    'MIDNR':  'Michigan Department of Natural Resources',
    'MLZ':    'Moore Laboratory of Zoology (MLZ)',
    'MMNH':   'Minnesota Museum of Natural History',
    'MMNS':   'Mississippi Museum of Natural Science',
    'MSB':    'Museum of Southwestern Biology (University of New Mexico)',
    'MVZ':    'Museum of Vertebrate Zoology (UC Berkeley)',
    # --- N ---
    'NBSB':   'National Biomonitoring Specimen Bank',
    'NCWRC':  'North Carolina Wildlife Resources Commission',
    'NHSM':   'Natural History Society of Maryland',
    'NMMNHS': 'New Mexico Museum of Natural History and Science',
    'NMU':    'Northern Michigan University',
    # --- O ---
    'OGL':    'Ocean Genome Legacy',
    'OWU':    'Ohio Wesleyan University',
    # --- P ---
    'PSM':    'Puget Sound Museum of Natural History',
    # --- S ---
    'STAC':   'Saint Anselm College',
    # --- T ---
    'TCDGM':  'Trinity College Dublin Geology Museum',
    'TMCC':   'Truckee Meadows Community College',
    # --- U ---
    'UA':     'University of Arizona',
    'UAA':    'University of Alaska Anchorage',
    'UAF':    'University of Alaska Fairbanks',
    'UAM':    'University of Alaska Museum of the North',
    'UAMb':   'University of Alaska Museum (Botany)',
    'UCM':    'University of Colorado Museum of Natural History',
    'UCSC':   'University of California Santa Cruz (UCSC)',
    'UMNH':   'Natural History Museum of Utah (UMNH)',
    'UMZM':   'University of Michigan Museum of Zoology',
    'UNCG':   'University of North Carolina at Greensboro',
    'UNK':    'University of Nebraska at Kearney',
    'UNM':    'University of New Mexico',
    'UNR':    'University of Nevada, Reno',
    'USNPC':  'United States National Parasite Collection (USNPC)',
    'UTEP':   'University of Texas at El Paso',
    'UWBM':   'Burke Museum of Natural History and Culture (UWBM)',
    'UWYMV':  'University of Wyoming Museum of Vertebrates (UWYMV)',
    'UWZM':   'University of Wisconsin Zoological Museum',
    # --- W ---
    'WNMU':   'Western New Mexico University',
    # --- Z ---
    'ZSFQ':   'Universidad San Francisco de Quito',
}

# Directories
DATA_DIR = Path(__file__).parent / "data"
DASHBOARD_DIR = Path(__file__).parent / "dashboard"
LOGS_DIR = Path(__file__).parent / "logs"


# ============================================================================
# Portal summary helper (feeds both bar chart and pie chart)
# ============================================================================

def _clean_str(x):
    """Normalise NaN / None / 'nan' to empty string."""
    if x is None:
        return ''
    if isinstance(x, float) and math.isnan(x):
        return ''
    s = str(x).strip()
    return '' if s.lower() in ('nan', 'none', 'null') else s


# Taxonomy fields that can contain semicolon-duplicated values e.g. "Animalia; Animalia; Animalia"
DEDUP_SEMICOLON_COLS = {'kingdom', 'phylum', 'phylclass', 'phylorder', 'family', 'genus', 'species'}

def _dedup_semicolon(x):
    """Remove duplicate entries in semicolon-separated taxonomy strings.
    e.g. 'Animalia; Animalia; Animalia' → 'Animalia'
    """
    if not x or not isinstance(x, str):
        return x
    parts = [p.strip() for p in x.split(';')]
    seen = []
    for p in parts:
        if p and p not in seen:
            seen.append(p)
    return '; '.join(seen) if seen else x


def save_portal_summary(portal_accumulator, output_dir, timestamp):
    """
    Generates portal_summary_YYYY_MM_DD.csv — a full replacement for
    Updated_Portal.xlsx that feeds both Summary tab charts.

    Chart 1 — "Porta-Distributionl" (NUMBER OF RECORDS bar chart):
        Tableau datasource: Update_portals  (was Updated_Portal.xlsx)
        Rows shelf : F4 (Guid Prefix) / F11 (Records)
        Cols shelf : SUM(F7 = Rcnt)
        Source fields from Arctos CSV / HTML:
          guid_prefix        → F4  (HTML: guid_prefix)
          COUNT(rows)        → F7  Rcnt  (bar width measure)
          COUNT(rows)        → F11 Records  (row label)

    Chart 2 — "Pie chart" (PERCENTAGE DISTRIBUTION):
        Tableau datasource: Update_portals  (was Updated_Portal.xlsx)
        Measure: F8 (Rcnt Percentage = Rcnt / total * 100, integer)
        Source fields from Arctos CSV / HTML:
          guid_prefix        → F4  (HTML: guid_prefix)
          collection_cde     → F2  (HTML: collection)
          institution_acronym→ F3  (HTML: institution_acronym)
          Rcnt / total * 100 → F8  Rcnt Percentage

    Full column layout (mirrors Updated_Portal.xlsx F1–F11):
      F1  Collection Id      : sequential integer (1-based, sorted by Rcnt desc)
      F2  Collection         : collection_cde
      F3  Institution        : full institution name (INSTITUTION_FULL_NAMES mapping; fallback to acronym)
      F4  Guid Prefix        : guid_prefix
      F5  Guid Prefix First  : token before ":" in guid_prefix
      F6  Guid Prefix Split1 : token after  ":" in guid_prefix
      F7  Rcnt               : record count per guid_prefix
      F8  Rcnt Percentage    : round(Rcnt / total * 100)  [integer, matches F8 BigInt schema]
      F9  Portal Name        : full institution name (INSTITUTION_FULL_NAMES mapping; fallback to acronym)
      F10 Type               : collection_cde       (best available proxy for collection type)
      F11 Records            : same as Rcnt         (used as row label in bar chart)

    Output file: data/output/portal_summary_YYYY_MM_DD.csv
    """
    total_records = sum(portal_accumulator.values())

    rows = []
    for (guid_prefix, collection_cde, institution_acronym), rcnt in portal_accumulator.items():
        pct_int = round(rcnt / total_records * 100) if total_records > 0 else 0

        # Resolve full institution name for F3 / F9 — matches the Tableau Institution filter
        institution_full = INSTITUTION_FULL_NAMES.get(institution_acronym, institution_acronym)

        # Split guid_prefix on ":" for F5 / F6
        parts = guid_prefix.split(':', 1) if guid_prefix else ['', '']
        gp_first = parts[0]
        gp_split1 = parts[1] if len(parts) > 1 else ''

        rows.append({
            'Collection':          collection_cde,     # F2
            'Institution':         institution_full,   # F3 — full name (fallback: acronym)
            'Guid_Prefix':         guid_prefix,        # F4
            'Guid_Prefix_First':   gp_first,           # F5
            'Guid_Prefix_Split1':  gp_split1,          # F6
            'Rcnt':                rcnt,               # F7
            'Rcnt_Percentage':     pct_int,            # F8
            'Portal_Name':         institution_full,   # F9 — full name (fallback: acronym)
            'Type':                collection_cde,     # F10
            'Records':             rcnt,               # F11
        })

    portal_df = (pd.DataFrame(rows)
                 .sort_values('Rcnt', ascending=False)
                 .reset_index(drop=True))

    # Add F1 (Collection Id) as sequential integer after sorting
    portal_df.insert(0, 'Collection_Id', range(1, len(portal_df) + 1))

    output_path = output_dir / f"portal_summary_{timestamp}.csv"
    portal_df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"   ✅ Portal Summary CSV: {output_path.name}")
    print(f"      {len(portal_df)} Guid Prefixes  |  {total_records:,} total records")
    print(f"      → feeds NUMBER OF RECORDS bar chart  (F4 / F7 / F11)")
    print(f"      → feeds % DISTRIBUTION pie chart     (F4 / F8)")
    return output_path


# ============================================================================
# Core conversion functions
# ============================================================================

def create_hyper_table_definition(table_name):
    """Creates the Tableau Hyper table definition."""
    columns = [
        TableDefinition.Column('cat_num', SqlType.text(), NULLABLE),
        TableDefinition.Column('cataloged_item_type', SqlType.text(), NULLABLE),
        TableDefinition.Column('collecting_event_id', SqlType.text(), NULLABLE),
        TableDefinition.Column('collecting_method', SqlType.text(), NULLABLE),
        TableDefinition.Column('collecting_source', SqlType.text(), NULLABLE),
        TableDefinition.Column('collection_cde', SqlType.text(), NULLABLE),
        TableDefinition.Column('collectors', SqlType.text(), NULLABLE),
        TableDefinition.Column('country', SqlType.text(), NULLABLE),
        TableDefinition.Column('county', SqlType.text(), NULLABLE),
        TableDefinition.Column('dec_lat', SqlType.double(), NULLABLE),
        TableDefinition.Column('dec_long', SqlType.double(), NULLABLE),
        TableDefinition.Column('family', SqlType.text(), NULLABLE),
        TableDefinition.Column('genbanknum', SqlType.text(), NULLABLE),
        TableDefinition.Column('genus', SqlType.text(), NULLABLE),
        TableDefinition.Column('guid_prefix', SqlType.text(), NULLABLE),
        TableDefinition.Column('identification_id', SqlType.big_int(), NULLABLE),
        TableDefinition.Column('institution_acronym', SqlType.text(), NULLABLE),
        TableDefinition.Column('kingdom', SqlType.text(), NULLABLE),
        TableDefinition.Column('locality_id', SqlType.big_int(), NULLABLE),
        TableDefinition.Column('media', SqlType.text(), NULLABLE),
        TableDefinition.Column('phylclass', SqlType.text(), NULLABLE),
        TableDefinition.Column('phylorder', SqlType.text(), NULLABLE),
        TableDefinition.Column('phylum', SqlType.text(), NULLABLE),
        TableDefinition.Column('scientific_name', SqlType.text(), NULLABLE),
        TableDefinition.Column('species', SqlType.text(), NULLABLE),
        TableDefinition.Column('state_prov', SqlType.text(), NULLABLE),
        TableDefinition.Column('subfamily', SqlType.text(), NULLABLE),
        TableDefinition.Column('suborder', SqlType.text(), NULLABLE),
        TableDefinition.Column('subspecies', SqlType.text(), NULLABLE),
        TableDefinition.Column('subtribe', SqlType.text(), NULLABLE),
        TableDefinition.Column('superfamily', SqlType.text(), NULLABLE),
        TableDefinition.Column('superorder', SqlType.text(), NULLABLE),
        TableDefinition.Column('tribe', SqlType.text(), NULLABLE),
        TableDefinition.Column('year', SqlType.int(), NULLABLE),
    ]

    return TableDefinition(table_name=table_name, columns=columns)


def get_csv_stream_from_gz(gz_path):
    """Returns a text stream from a .gz or .tar.gz file."""
    print(f"📄 Processing GZ file: {os.path.basename(gz_path)}")

    if gz_path.endswith('.tar.gz'):
        print("   Format: TAR.GZ")
        with tarfile.open(gz_path, 'r:gz') as tar:
            csv_members = [m for m in tar.getmembers() if m.name.endswith('.csv')]
            if not csv_members:
                raise ValueError("No CSV file found inside the TAR.GZ archive.")
            csv_member = csv_members[0]
            print(f"   Found CSV: {csv_member.name}")
            print(f"   Uncompressed size: {csv_member.size / (1024**3):.2f} GB")
            csv_file = tar.extractfile(csv_member)
            text_stream = io.TextIOWrapper(csv_file, encoding='utf-8')
            return text_stream, csv_member.size

    else:
        print("   Format: GZ")
        # Last 4 bytes of a GZ file hold uncompressed size (mod 2^32)
        with open(gz_path, 'rb') as f:
            f.seek(-4, 2)
            uncompressed_size = int.from_bytes(f.read(4), 'little')
        print(f"   Uncompressed size: ~{uncompressed_size / (1024**3):.2f} GB")
        gz_file = gzip.open(gz_path, 'rb')
        text_stream = io.TextIOWrapper(gz_file, encoding='utf-8')
        return text_stream, uncompressed_size


def get_csv_stream_from_zip(zip_path):
    """Returns a text stream from a .zip file."""
    print(f"📄 Processing ZIP file: {os.path.basename(zip_path)}")
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
    if not csv_files:
        raise ValueError("No CSV file found inside the ZIP archive.")
    csv_filename = csv_files[0]
    print(f"   Found CSV: {csv_filename}")
    csv_info = zip_ref.getinfo(csv_filename)
    uncompressed_size = csv_info.file_size
    print(f"   Uncompressed size: {uncompressed_size / (1024**3):.2f} GB")
    csv_file = zip_ref.open(csv_filename)
    text_stream = io.TextIOWrapper(csv_file, encoding='utf-8')
    return text_stream, uncompressed_size, zip_ref


def convert_compressed_to_hyper(compressed_path, hyper_path):
    """
    Converts a compressed CSV to Hyper format using streaming reads.
    Simultaneously accumulates the portal summary in a single pass.
    Supports .zip, .gz, .tar.gz.

    Returns:
        portal_accumulator : dict
            key   = (guid_prefix, collection_cde, institution_acronym)
            value = record count
            Feeds both the NUMBER OF RECORDS bar chart (F4/F7/F11)
            and the % DISTRIBUTION pie chart (F4/F8) via save_portal_summary().
    """
    print(f"\n🔄 Starting data conversion...")
    print(f"   Input:  {os.path.basename(compressed_path)}")
    print(f"   Output: {os.path.basename(hyper_path)}")
    print(f"   ✨ Streaming mode — no full decompression required!\n")

    if os.path.exists(hyper_path):
        os.remove(hyper_path)

    file_extension = Path(compressed_path).suffix.lower()

    if file_extension == '.zip':
        text_stream, uncompressed_size, archive = get_csv_stream_from_zip(compressed_path)
        should_close_archive = True
    elif file_extension == '.gz' or compressed_path.endswith('.tar.gz'):
        text_stream, uncompressed_size = get_csv_stream_from_gz(compressed_path)
        archive = None
        should_close_archive = False
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    uncompressed_size_gb = uncompressed_size / (1024**3)
    print(f"   💾 Saving ~{uncompressed_size_gb:.0f} GB of disk space!\n")

    # ── Portal accumulator ──────────────────────────────────────────────────
    # key: (guid_prefix, collection_cde, institution_acronym)  value: count
    # Populated chunk-by-chunk; feeds bar chart (F4/F7/F11) + pie chart (F4/F8)
    portal_accumulator = {}
    # ────────────────────────────────────────────────────────────────────────

    try:
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint,
                            database=hyper_path,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as connection:

                from tableauhyperapi import SchemaName
                schema_name = SchemaName("Extract")
                connection.catalog.create_schema_if_not_exists(schema_name)

                table_name = TableName("Extract", "Extract")
                table_def = create_hyper_table_definition(table_name)

                print(f"📊 Creating Hyper table: {table_name}")
                print(f"   Columns: {len(UNIFIED_COLUMNS)}\n")
                connection.catalog.create_table(table_def)

                print(f"⏳ Processing CSV in chunks of {CHUNK_SIZE:,} rows...")

                total_rows = 0
                chunk_num = 0

                csv_iterator = pd.read_csv(
                    text_stream,
                    usecols=UNIFIED_COLUMNS,
                    chunksize=CHUNK_SIZE,
                    low_memory=False,
                    dtype=str,       # Read all as string first — safest approach
                    on_bad_lines='warn'
                )

                INT_COLUMNS   = ['year', 'identification_id', 'locality_id']
                FLOAT_COLUMNS = ['dec_lat', 'dec_long']
                TEXT_COLUMNS  = [col for col in UNIFIED_COLUMNS
                                 if col not in INT_COLUMNS + FLOAT_COLUMNS]

                for chunk_df in csv_iterator:
                    chunk_num += 1
                    chunk_rows = len(chunk_df)
                    total_rows += chunk_rows

                    # Fix: enforce column order to match table_def
                    chunk_df = chunk_df.reindex(columns=UNIFIED_COLUMNS)

                    # ── Portal accumulation (raw strings, before numeric conversion) ──
                    #
                    # Feeds NUMBER OF RECORDS bar chart ("Porta-Distributionl" worksheet):
                    #   Rows: F4 (Guid Prefix) / F11 (Records)
                    #   Cols: SUM(F7 = Rcnt)
                    #   Arctos CSV → HTML field mapping:
                    #     guid_prefix        → guid_prefix   (HTML: guid_prefix)
                    #     collection_cde     → collection    (HTML: collection)
                    #     institution_acronym→ institution   (HTML: institution_acronym)
                    #
                    # Feeds % DISTRIBUTION pie chart ("Pie chart" worksheet):
                    #   Measure: F8 = Rcnt / total * 100
                    #
                    portal_cols = chunk_df[
                        ['guid_prefix', 'collection_cde', 'institution_acronym']
                    ].copy()

                    for col in portal_cols.columns:
                        portal_cols[col] = portal_cols[col].apply(_clean_str)

                    portal_group = portal_cols.groupby(
                        ['guid_prefix', 'collection_cde', 'institution_acronym'],
                        dropna=False
                    ).size()

                    for key, cnt in portal_group.items():
                        portal_accumulator[key] = (
                            portal_accumulator.get(key, 0) + int(cnt)
                        )
                    # ──────────────────────────────────────────────────────────────

                    # Convert numeric columns
                    for col in INT_COLUMNS:
                        if col in chunk_df.columns:
                            chunk_df[col] = pd.to_numeric(chunk_df[col], errors='coerce')

                    for col in FLOAT_COLUMNS:
                        if col in chunk_df.columns:
                            chunk_df[col] = pd.to_numeric(chunk_df[col], errors='coerce')

                    # Fix: guard NaN before str cast to avoid 'nan' string values
                    for col in TEXT_COLUMNS:
                        if col in chunk_df.columns:
                            mask = chunk_df[col].isna()
                            chunk_df[col] = chunk_df[col].astype(str)
                            chunk_df.loc[mask, col] = None

                    # Deduplicate semicolon-separated taxonomy fields
                    for col in DEDUP_SEMICOLON_COLS:
                        if col in chunk_df.columns:
                            chunk_df[col] = chunk_df[col].apply(_dedup_semicolon)

                    # Build row list in UNIFIED_COLUMNS order for Hyper insertion
                    rows_to_insert = []
                    for idx, row in chunk_df.iterrows():
                        clean_row = []
                        for col_name in UNIFIED_COLUMNS:
                            value = row[col_name]
                            if hasattr(value, 'item'):
                                value = value.item()
                            if value is None or (isinstance(value, float) and math.isnan(value)):
                                value = None
                            elif col_name in INT_COLUMNS:
                                value = int(value)
                            elif col_name in TEXT_COLUMNS and not isinstance(value, str):
                                value = str(value)
                            clean_row.append(value)
                        rows_to_insert.append(clean_row)

                    with Inserter(connection, table_def) as inserter:
                        inserter.add_rows(rows_to_insert)
                        inserter.execute()

                    print(f"   Chunk {chunk_num}: {chunk_rows:,} rows  (total: {total_rows:,})")

            print(f"\n✅ Conversion complete!")
            print(f"   Total rows: {total_rows:,}")

            if os.path.exists(hyper_path):
                hyper_size_gb = os.path.getsize(hyper_path) / (1024**3)
                print(f"   Hyper size: {hyper_size_gb:.2f} GB")
                print(f"   Compression ratio: {(1 - hyper_size_gb / uncompressed_size_gb) * 100:.1f}%")
            else:
                print(f"   ⚠️  Hyper file not found at expected path — skipping size report")

    finally:
        text_stream.close()
        if should_close_archive and archive:
            archive.close()

    return portal_accumulator


# ============================================================================
# Utility functions
# ============================================================================

def find_compressed_file():
    """Locates a compressed input file (ZIP or GZ) in data/input/."""
    input_dir = DATA_DIR / "input"

    zip_files     = list(input_dir.glob("*.zip"))
    gz_files      = list(input_dir.glob("*.gz"))
    tar_gz_files  = list(input_dir.glob("*.tar.gz"))
    all_files     = zip_files + gz_files + tar_gz_files

    if not all_files:
        print(f"❌ No compressed file found in {input_dir}")
        print(f"   Supported formats: .zip, .gz, .tar.gz")
        print(f"   Please copy a compressed file to: {input_dir}")
        sys.exit(1)

    if len(all_files) > 1:
        print(f"⚠️  Multiple compressed files found:")
        for i, f in enumerate(all_files, 1):
            print(f"   {i}. {f.name}")
        print(f"\n   Using the most recent: {all_files[-1].name}")

    return str(all_files[-1])


def generate_output_path():
    """Generates the timestamped output path for the Hyper file."""
    output_dir = DATA_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d")
    return output_dir / f"arctos_main_{timestamp}.hyper"


def update_twbx_portal_csv(portal_csv_path):
    """
    Replaces the embedded portal summary CSV inside the .twbx file.

    The .twbx is a zip archive. The TWB XML hardcodes references to
    'Data/output/portal_summary_2026_05_05.csv' throughout — changing the
    filename breaks every field reference.  Instead we overwrite the embedded
    CSV in-place so Tableau sees fresh data with zero remapping required.

    Steps:
      1. Find the .twbx in the same folder as this script.
      2. Read the new CSV content.
      3. Rewrite the zip, replacing the old embedded CSV entry.
      4. The user just opens (or refreshes) the .twbx — no datasource replace needed.
    """
    import zipfile
    import shutil

    script_dir = Path(__file__).parent
    twbx_files = list(script_dir.glob("*.twbx"))
    if not twbx_files:
        print("   ⚠️  No .twbx file found next to this script — skipping embed update.")
        return None

    twbx_path = twbx_files[0]
    if len(twbx_files) > 1:
        # prefer the most recently modified
        twbx_path = max(twbx_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📦 Updating embedded CSV in: {twbx_path.name}")

    # The embedded entry name is hardcoded in the .twbx
    EMBEDDED_CSV = "Data/output/portal_summary_2026_05_05.csv"

    new_csv_bytes = portal_csv_path.read_bytes()

    # Rewrite the zip in-place using a temp file
    tmp_path = twbx_path.with_suffix(".twbx.tmp")
    try:
        with zipfile.ZipFile(twbx_path, 'r') as zin, \
             zipfile.ZipFile(tmp_path,  'w', compression=zipfile.ZIP_DEFLATED) as zout:

            replaced = False
            for item in zin.infolist():
                if item.filename == EMBEDDED_CSV:
                    zout.writestr(item, new_csv_bytes)
                    replaced = True
                    print(f"   ✅ Replaced: {EMBEDDED_CSV}")
                else:
                    zout.writestr(item, zin.read(item.filename))

            if not replaced:
                print(f"   ⚠️  Entry '{EMBEDDED_CSV}' not found in .twbx — adding it.")
                zout.writestr(EMBEDDED_CSV, new_csv_bytes)

        shutil.move(str(tmp_path), str(twbx_path))
        print(f"   ✅ .twbx updated: {twbx_path.name}")
        print(f"      Just open (or Ctrl+R refresh) the .twbx — no datasource remapping needed.")
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"   ❌ Failed to update .twbx: {e}")
        raise

    return twbx_path


def update_twbx_hyper(hyper_path):
    """
    Replaces the embedded arctos_main hyper file inside the .twbx.

    The .twbx hardcodes 'Data/output/arctos_main_2026_05_05.hyper' — we
    overwrite it in-place so all worksheets (Taxonomic Breakdown, Guid Prefix
    Map, Spatial Analysis, etc.) see fresh data without any remapping.
    """
    import zipfile
    import shutil

    script_dir = Path(__file__).parent
    twbx_files = list(script_dir.glob("*.twbx"))
    if not twbx_files:
        print("   ⚠️  No .twbx file found next to this script — skipping hyper update.")
        return None

    twbx_path = twbx_files[0]
    if len(twbx_files) > 1:
        twbx_path = max(twbx_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📦 Updating embedded Hyper in: {twbx_path.name}")

    EMBEDDED_HYPER = "Data/output/arctos_main_2026_05_05.hyper"

    new_hyper_bytes = Path(hyper_path).read_bytes()

    tmp_path = twbx_path.with_suffix(".twbx.tmp")
    try:
        with zipfile.ZipFile(twbx_path, 'r') as zin, \
             zipfile.ZipFile(tmp_path,  'w', compression=zipfile.ZIP_DEFLATED) as zout:

            replaced = False
            for item in zin.infolist():
                if item.filename == EMBEDDED_HYPER:
                    zout.writestr(item, new_hyper_bytes)
                    replaced = True
                    print(f"   ✅ Replaced: {EMBEDDED_HYPER}")
                else:
                    zout.writestr(item, zin.read(item.filename))

            if not replaced:
                print(f"   ⚠️  Entry '{EMBEDDED_HYPER}' not found in .twbx — adding it.")
                zout.writestr(EMBEDDED_HYPER, new_hyper_bytes)

        shutil.move(str(tmp_path), str(twbx_path))
        print(f"   ✅ .twbx updated with new Hyper data.")
        print(f"      Just open (or Ctrl+R refresh) the .twbx — Taxonomic Breakdown and all other sheets will show fresh data.")
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"   ❌ Failed to update .twbx hyper: {e}")
        raise

    return twbx_path


def update_twbx_cache_stats(twbx_path=None):
    """
    Finds cache_sysstats_global_*.csv in data/input/ and replaces the
    embedded copy inside the .twbx (Data/Practicum/cache_sysstats_global_2026-04-30.csv).
    """
    import zipfile
    import shutil

    # Find the input CSV
    input_dir = DATA_DIR / "input"
    candidates = sorted(input_dir.glob("cache_sysstats_global_*.csv"))
    if not candidates:
        print("   ⚠️  No cache_sysstats_global_*.csv found in data/input/ — skipping.")
        return None
    csv_path = candidates[-1]  # most recent by filename
    print(f"\n📊 Updating cache stats from: {csv_path.name}")

    # Find .twbx
    if twbx_path is None:
        script_dir = Path(__file__).parent
        twbx_files = list(script_dir.glob("*.twbx"))
        if not twbx_files:
            print("   ⚠️  No .twbx file found — skipping cache stats update.")
            return None
        twbx_path = max(twbx_files, key=lambda p: p.stat().st_mtime)

    EMBEDDED_CSV = "Data/Practicum/cache_sysstats_global_2026-04-30.csv"
    new_csv_bytes = csv_path.read_bytes()

    tmp_path = twbx_path.with_suffix(".twbx.tmp")
    try:
        with zipfile.ZipFile(twbx_path, 'r') as zin, \
             zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:

            replaced = False
            for item in zin.infolist():
                if item.filename == EMBEDDED_CSV:
                    zout.writestr(item, new_csv_bytes)
                    replaced = True
                    print(f"   ✅ Replaced: {EMBEDDED_CSV}")
                else:
                    zout.writestr(item, zin.read(item.filename))

            if not replaced:
                print(f"   ⚠️  Entry '{EMBEDDED_CSV}' not found in .twbx — adding it.")
                zout.writestr(EMBEDDED_CSV, new_csv_bytes)

        shutil.move(str(tmp_path), str(twbx_path))
        print(f"   ✅ Cache stats updated in .twbx.")
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"   ❌ Failed to update cache stats: {e}")
        raise

    return twbx_path




def print_next_steps(hyper_path, portal_csv_path):
    """Prints instructions for refreshing the Tableau dashboard."""
    print("\n" + "=" * 80)
    print("📋 Next Steps:")
    print("=" * 80)
    print("\nBoth data sources are already embedded in the .twbx — NO manual steps needed!")
    print("Just open the .twbx (or Ctrl+R refresh if already open).")
    print()
    print("  ✅ Portal summary CSV  → Porta-Distributionl + Pie chart")
    print("  ✅ arctos_main Hyper   → Taxonomic Breakdown + Guid Prefix Map + all other sheets")
    print()
    print("[1] File → Save\n")
    print("=" * 80)


# ============================================================================
# Main
# ============================================================================

def main():
    """Entry point."""
    print("=" * 80)
    print("Arctos Dashboard Update Tool (ZIP / GZ)")
    print("=" * 80)
    print()

    print("📋 Checking...")

    compressed_file = find_compressed_file()
    file_size_gb    = os.path.getsize(compressed_file) / (1024**3)
    file_type       = Path(compressed_file).suffix.upper()
    print(f"   ✓ Input file: {os.path.basename(compressed_file)} ({file_size_gb:.1f} GB)")
    print(f"   ✓ Format: {file_type}")

    output_path = generate_output_path()
    print(f"   ✓ Output: {output_path.name}")
    print()

    start_time = datetime.now()

    try:
        # Convert to Hyper and accumulate portal summary in one pass
        portal_accumulator = convert_compressed_to_hyper(
            compressed_file, str(output_path)
        )

        hyper_duration = datetime.now() - start_time
        hyper_min = hyper_duration.seconds // 60
        hyper_sec = hyper_duration.seconds % 60
        print(f"\n⏱️  Hyper conversion time: {hyper_min} min {hyper_sec} sec")

        # ── Save portal summary CSV (replaces Updated_Portal.xlsx) ──────────
        print(f"\n📊 Generating portal summary (bar chart + pie chart data)...")
        output_dir = output_path.parent
        timestamp  = datetime.now().strftime("%Y_%m_%d")

        t = datetime.now()
        portal_csv_path = save_portal_summary(portal_accumulator, output_dir, timestamp)
        portal_duration = datetime.now() - t
        print(f"⏱️  Portal summary time: {portal_duration.seconds} sec")

        # ── Patch the .twbx so Tableau picks up new data without remapping ──
        t = datetime.now()
        update_twbx_portal_csv(portal_csv_path)
        print(f"⏱️  CSV embed time: {(datetime.now() - t).seconds} sec")

        t = datetime.now()
        update_twbx_hyper(output_path)
        print(f"⏱️  Hyper embed time: {(datetime.now() - t).seconds} sec")

        t = datetime.now()
        update_twbx_cache_stats()
        print(f"⏱️  Cache stats embed time: {(datetime.now() - t).seconds} sec")

        # ─────────────────────────────────────────────────────────────────────

        total_duration = datetime.now() - start_time
        total_min = total_duration.seconds // 60
        total_sec = total_duration.seconds % 60
        print(f"\n⏱️  Total time: {total_min} min {total_sec} sec")

        # Write log
        logs_dir = LOGS_DIR
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"update_{datetime.now().strftime('%Y_%m_%d')}.log"
        with open(log_file, 'w') as f:
            f.write(f"Updated at:             {datetime.now()}\n")
            f.write(f"Source file:            {os.path.basename(compressed_file)}\n")
            f.write(f"Format:                 {file_type}\n")
            f.write(f"Output (Hyper):         {output_path.name}\n")
            f.write(f"Output (Portal CSV):    {portal_csv_path.name}\n")
            f.write(f"Hyper conversion:       {hyper_min} min {hyper_sec} sec\n")
            f.write(f"Total duration:         {total_min} min {total_sec} sec\n")

        print(f"📝 Log: {log_file.name}")

        print_next_steps(output_path, portal_csv_path)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
