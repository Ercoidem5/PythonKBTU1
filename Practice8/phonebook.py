import os
import psycopg2
from connect import get_connection


def print_rows(rows: list, headers=("ID", "First name", "Last name", "Phone")):
    if not rows:
        print(" no results")
        return
    widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
              for i, h in enumerate(headers)]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    sep = "  " + "  ".join("-" * w for w in widths)
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        print(fmt.format(*[str(c) if c is not None else "" for c in row]))


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id         SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name  VARCHAR(100),
                phone      VARCHAR(20)  NOT NULL UNIQUE
            );
        """)
    conn.commit()


def search_contacts():
    pattern = input("  Enter search pattern: ").strip()
    if not pattern:
        print("Pattern cannot be empty.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
        print_rows(rows)
    except psycopg2.Error as e:
        print(f"search_contacts: {e}")
    finally:
        conn.close()



def upsert_single():
    print("\n── Insert / Update contact ──")
    first = input("  First name : ").strip()
    last  = input("  Last name  : ").strip() or None
    phone = input("  Phone      : ").strip()

    if not first or not phone:
        print("First name and phone are required.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_contact(%s, %s, %s);", (first, last, phone))
        print(" Contact saved (inserted or updated).")
    except psycopg2.Error as e:
        print(f" upsert_single: {e}")
    finally:
        conn.close()


def insert_many():

    print("Bulk insert contacts ")
    print("Enter one contact per line:  First [Last],+phone")
    print("Press Enter on a blank line when done.\n")

    names, phones = [], []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        if "," not in line:
            print("Bad format - expected 'Name,+phone'")
            continue
        name_part, phone_part = line.split(",", 1)
        names.append(name_part.strip())
        phones.append(phone_part.strip())

    if not names:
        print("No data entered.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL insert_many_contacts(%s, %s);", (names, phones))

        with conn.cursor() as cur:
            cur.execute("SELECT name, phone, reason FROM tmp_invalid_contacts;")
            bad = cur.fetchall()

        if bad:
            print(f"{len(bad)} invalid row(s) were rejected:")
            print_rows(bad, headers=("Name", "Phone", "Reason"))
        else:
            print(" All contacts inserted successfully.")
    except psycopg2.Error as e:
        print(f" insert_many: {e}")
    finally:
        conn.close()




def paginated_query():
    try:
        size = int(input(" Page size (rows per page) [5]: ").strip() or "5")
        page = int(input(" Page number (1-based)      [1]: ").strip() or "1")
    except ValueError:
        print("Please enter valid integers.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (size, page))
            rows = cur.fetchall()
        print(f" Page {page}  (size={size})")
        print_rows(rows)
    except psycopg2.Error as e:
        print(f" paginated_query: {e}")
    finally:
        conn.close()



def delete_contact():
    print("Delete contact")
    print("1 - By first name")
    print("2 - By phone number")
    choice = input("  Choice: ").strip()

    username = phone = None
    if choice == "1":
        username = input("First name: ").strip() or None
    elif choice == "2":
        phone = input("Phone: ").strip() or None
    else:
        print("[WARN] Invalid choice.")
        return

    if not username and not phone:
        print("[WARN] Nothing to delete - no value provided.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_contact(%s, %s);", (username, phone))
        print(" Delete operation complete.")
    except psycopg2.Error as e:
        print(f" delete_contact: {e}")
    finally:
        conn.close()


MENU = """
1. Search contacts
2. Insert / update one contact
3. Bulk insert contacts (with validation)
4. Browse contact
5. Delete contact
0. Exit
"""


def main():
    conn = get_connection()
    try:
        with conn:
            ensure_table(conn)
    finally:
        conn.close()

    while True:
        print(MENU)
        choice = input("Select option: ").strip().lower()

        if   choice == "1": search_contacts()
        elif choice == "2": upsert_single()
        elif choice == "3": insert_many()
        elif choice == "4": paginated_query()
        elif choice == "5": delete_contact()
        elif choice == "0":
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
