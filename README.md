# E-commerce ETL/DWH Pipeline

This project demonstrates a simple ETL pipeline for e-commerce order data.

Current pipeline:
- Read raw orders from CSV
- Validate and clean order records
- Cast fields to proper data types
- Normalize order statuses
- Remove duplicate orders
- Split data into clean and rejected records
- Save results to JSON files

Tech stack:
- Python
- CSV
- JSON
- pathlib
