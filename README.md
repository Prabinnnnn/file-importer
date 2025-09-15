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

##  Implementation Details

### 1. File Upload and Parsing
- Users (admins) upload **CSV, XLS, or XLSX** files via Django Admin.  
- **Pandas** is used to read and parse the file content.  
- For Excel files:  
  - `.xlsx` files are handled with **openpyxl**  
  - `.xls` files are handled with **xlrd**  
- This ensures that the project can handle multiple file formats robustly.

### 2. Database Model
- A **Product** model stores all product information in the database.  
- It has six fields:  
  - `sku` (unique identifier)  
  - `name`  
  - `category`  
  - `price`  
  - `stock_qty`  
  - `status` (Active/Inactive)  
- Each field corresponds to a column in the uploaded file.

### 3. Data Import and Export
- The project uses **django-import-export** instead of custom views.  
- Admins can click **Import** to upload files, and the library automatically:  
  - Validates the data  
  - Maps file rows to the `Product` model  
  - Prevents duplicate entries using `sku` as the unique field  
- Admins can also **Export** data back to CSV or Excel.

### 4. Admin Integration
- The `Product` model is registered in Django Admin using **ImportExportModelAdmin**.  
- This provides a clean interface with:  
  - Filters (e.g., by category or status)  
  - Search functionality (by SKU or name)  
  - Bulk actions for managing products  
  - Import and Export buttons for file operations

### 5. Storage of Uploaded Files
- Uploaded files are temporarily stored in the `media/` folder during development.  
- Actual product data is stored in the **database**, not in the uploaded file itself.  
- This keeps the workflow efficient and secure.

### 6. Workflow Summary
1. Admin logs in to Django Admin.  
2. Uploads CSV/Excel file using the **Import** button.  
3. The system parses and validates the file.  
4. Valid product data is stored/updated in the database.  
5. Admin can manage products (edit, delete, filter, search).  
6. Data can be exported back to CSV/Excel when needed.

---