# Django Product Importer  

A Django-based system that allows uploading an Excel/CSV product file, parsing the data, storing it in a database, and viewing/managing it via the Django Admin interface.
---

## Features  
- Upload **CSV/XLS/XLSX** product files  
- Automatic parsing & validation using **pandas**  
- Store products in the database with 6 key fields:  
  - `sku` (unique code)  
  - `name`  
  - `category`  
  - `price`  
  - `stock_qty`  
  - `status`  
- Manage data via **Django Admin**    
- Clean admin UI with filters, search, and bulk actions  

---