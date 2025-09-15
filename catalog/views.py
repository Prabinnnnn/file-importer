import os
import pandas as pd
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.db import transaction

from .forms import UploadFileForm
from .models import Product

ALLOWED_EXT = ('.csv', '.xls', '.xlsx')

REQUIRED_COLUMNS = {'sku','name','category','price','stock_qty','status'}

def handle_uploaded_file(f, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)

def import_products_from_dataframe(df, update_existing=True):
    """
    df: pandas.DataFrame with required columns (case-insensitive)
    update_existing: if True, update existing products with same sku; else skip duplicates
    Returns dict summary.
    """
    # Normalize columns to lower-case and strip
    df.columns = [c.strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

    created = 0
    updated = 0
    skipped = 0
    errors = []

    objs_to_create = []
    skus_seen = set()

    # We'll use transaction and upsert for safety
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                sku = str(row['sku']).strip()
                if not sku or sku in skus_seen:
                    skipped += 1
                    continue
                skus_seen.add(sku)

                name = str(row['name']).strip() if not pd.isna(row['name']) else ''
                category = str(row['category']).strip() if not pd.isna(row['category']) else ''
                # price: coerce to Decimal
                price_raw = row['price']
                price = Decimal(str(price_raw)) if not pd.isna(price_raw) else Decimal('0.00')
                stock_qty = int(row['stock_qty']) if not pd.isna(row['stock_qty']) else 0
                status_raw = str(row['status']).strip().lower() if not pd.isna(row['status']) else 'inactive'
                status = 'active' if 'active' in status_raw else 'inactive'

                # Upsert logic:
                if Product.objects.filter(sku=sku).exists():
                    if update_existing:
                        Product.objects.filter(sku=sku).update(
                            name=name, category=category, price=price, stock_qty=stock_qty, status=status
                        )
                        updated += 1
                    else:
                        skipped += 1
                else:
                    objs_to_create.append(Product(
                        sku=sku, name=name, category=category,
                        price=price, stock_qty=stock_qty, status=status
                    ))
                    created += 1

            except (InvalidOperation, ValueError, TypeError) as e:
                errors.append({"row": int(idx)+2, "error": str(e)})  # +2 to approximate excel row
                continue

        # bulk create
        if objs_to_create:
            Product.objects.bulk_create(objs_to_create)

    return {"created": created, "updated": updated, "skipped": skipped, "errors": errors}

def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data['file']
            fname = upload.name
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXT:
                messages.error(request, "Unsupported file type. Upload .csv, .xls, or .xlsx")
                return redirect('catalog:upload')

            # store temporarily
            dest_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, fname)
            handle_uploaded_file(upload, dest_path)

            # parse with pandas
            try:
                if ext == '.csv':
                    df = pd.read_csv(dest_path)
                else:
                    df = pd.read_excel(dest_path)  # openpyxl used for xlsx
            except Exception as e:
                messages.error(request, f"Failed to read file: {e}")
                return redirect('catalog:upload')

            try:
                summary = import_products_from_dataframe(df, update_existing=True)
                messages.success(request, f"Import completed — created: {summary['created']}, updated: {summary['updated']}, skipped: {summary['skipped']}")
                if summary['errors']:
                    messages.warning(request, f"Some rows had errors: {len(summary['errors'])} (see logs).")
                return redirect('admin:catalog_product_changelist')
            except ValueError as ve:
                messages.error(request, str(ve))
                return redirect('catalog:upload')
    else:
        form = UploadFileForm()

    return render(request, 'catalog/upload.html', {'form': form})
