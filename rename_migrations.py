#!/usr/bin/env python
"""
Script to rename 'cars' app to 'products' in the Django migrations table.
This updates the django_migrations table to reflect the app rename.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshmarket.settings')
django.setup()

from django.db import connection

def rename_app_in_migrations():
    """Rename 'cars' to 'products' in django_migrations table"""
    with connection.cursor() as cursor:
        # Check if there are any 'cars' migrations
        cursor.execute("SELECT COUNT(*) FROM django_migrations WHERE app = 'cars'")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Found {count} migration(s) for 'cars' app")

            # Update the app name from 'cars' to 'products'
            cursor.execute("UPDATE django_migrations SET app = 'products' WHERE app = 'cars'")
            print(f"Successfully renamed {count} migration(s) from 'cars' to 'products'")
        else:
            print("No 'cars' migrations found in database")

        # Show current state
        cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'products' ORDER BY id")
        products_migrations = cursor.fetchall()

        if products_migrations:
            print("\nCurrent 'products' migrations in database:")
            for app, name in products_migrations:
                print(f"  - {app}.{name}")

if __name__ == '__main__':
    try:
        rename_app_in_migrations()
        print("\nMigration rename completed successfully!")
        print("You can now run: python manage.py migrate")
    except Exception as e:
        print(f"Error: {e}")
