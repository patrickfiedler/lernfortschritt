#!/usr/bin/env python3
"""
Generate weekly class reports for all active classes.
Runs every Sunday night (00:00 Monday) to create reports for the past week.
"""

import os
import sys
from datetime import datetime, timedelta
import models
import utils

# Ensure reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'instance', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_weekly_reports():
    """Generate PDF reports for all active classes for the past week."""
    # Calculate date range (last 7 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    print(f"Generating weekly reports for {start_date} to {end_date}")

    # Get all classes
    with models.db_session() as conn:
        klassen = conn.execute("SELECT id, name FROM klasse ORDER BY name").fetchall()

    if not klassen:
        print("No classes found.")
        return 0

    reports_generated = 0

    for klasse in klassen:
        klasse_id = klasse['id']
        klasse_name = klasse['name']

        print(f"  Processing class: {klasse_name} (ID: {klasse_id})")

        try:
            # Get report data
            report_data = models.get_report_data_for_class(
                klasse_id,
                date_from=str(start_date),
                date_to=str(end_date)
            )

            if not report_data:
                print(f"    ⚠️  No data available for class {klasse_name}")
                continue

            # Check if class has students
            if not report_data['students']:
                print(f"    ℹ️  Class {klasse_name} has no students, skipping")
                continue

            # Generate PDF
            pdf_buffer = utils.generate_class_report_pdf(
                report_data,
                date_from=str(start_date),
                date_to=str(end_date)
            )

            # Create filename: klassenbericht_ClassName_YYYY-MM-DD.pdf
            safe_name = klasse_name.replace(' ', '_').replace('/', '-')
            filename = f"klassenbericht_{safe_name}_{end_date.strftime('%Y-%m-%d')}.pdf"
            filepath = os.path.join(REPORTS_DIR, filename)

            # Save PDF
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())

            # Save record in database
            models.save_report_record(
                report_type='class_simple',
                klasse_id=klasse_id,
                filename=filename,
                date_from=str(start_date),
                date_to=str(end_date)
            )

            pdf_size = len(pdf_buffer.getvalue())
            print(f"    ✅ Generated: {filename} ({pdf_size} bytes)")
            reports_generated += 1

        except Exception as e:
            print(f"    ❌ Error generating report for {klasse_name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n✅ Successfully generated {reports_generated} weekly reports")
    return reports_generated


if __name__ == '__main__':
    try:
        count = generate_weekly_reports()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
