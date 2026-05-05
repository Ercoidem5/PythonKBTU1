import csv
import json
import psycopg2
from connect import get_connection


# HELPERS

def print_rows(rows, headers=None):
    if not rows:
        print("  (no results)")
        return
    if headers:
        print("  " + " | ".join(f"{h:<20}" for h in headers))
        print("  " + "-" * (23 * len(headers)))
    for row in rows:
        print("  " + " | ".join(f"{str(v) if v is not None else '':<20}" for v in row))


def input_strip(prompt):
    return input(prompt).strip()


# SEARCH 

def search_contacts():
    query = input_strip("Search (name / email / phone): ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    print_rows(rows, ["id", "full_name", "email", "phone", "type", "group"])
    cur.close()
    conn.close()


# FILTER BY GROUP

def filter_group():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM groups ORDER BY name")
    groups = [r[0] for r in cur.fetchall()]
    if not groups:
        print("  No groups exist yet.")
        cur.close()
        conn.close()
        return

    print("  Available groups:", ", ".join(groups))
    group = input_strip("Group name: ")

    cur.execute("""
        SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
        ORDER BY c.first_name
    """, (group,))
    print_rows(cur.fetchall(), ["id", "first_name", "last_name", "email", "birthday", "group"])

    cur.close()
    conn.close()


# SEARCH BY EMAIL

def search_by_email():
    pattern = input_strip("Email pattern (e.g. gmail): ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.first_name, c.last_name, c.email, g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        WHERE c.email ILIKE %s
        ORDER BY c.first_name
    """, (f"%{pattern}%",))
    print_rows(cur.fetchall(), ["id", "first_name", "last_name", "email", "group"])
    cur.close()
    conn.close()


# SORT

def sort_contacts():
    print("  1 - name")
    print("  2 - birthday")
    print("  3 - date added")
    choice = input_strip("Choose: ")

    field_map = {"1": "first_name", "2": "birthday", "3": "created_at"}
    field = field_map.get(choice, "first_name")

    conn = get_connection()
    cur = conn.cursor()
    # Use safe whitelist — no user input in SQL identifier
    cur.execute(f"""
        SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, c.created_at, g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY {field} NULLS LAST
    """)
    print_rows(cur.fetchall(), ["id", "first_name", "last_name", "email", "birthday", "created_at", "group"])
    cur.close()
    conn.close()



# PAGINATION 

def pagination():
    page = 1
    size = 5

    conn = get_connection()
    cur = conn.cursor()

    while True:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (size, page))
        rows = cur.fetchall()

        print(f"\n  --- Page {page} ---")
        print_rows(rows, ["id", "first_name", "last_name", "email", "birthday", "group"])

        cmd = input_strip("n-next / p-prev / q-quit: ")
        if cmd == "n":
            if len(rows) < size:
                print("  Already on the last page.")
            else:
                page += 1
        elif cmd == "p":
            if page > 1:
                page -= 1
            else:
                print("  Already on the first page.")
        elif cmd == "q":
            break

    cur.close()
    conn.close()



# ADD CONTACT

def add_contact():
    first = input_strip("First name: ")
    last  = input_strip("Last name (blank to skip): ") or None
    email = input_strip("Email (blank to skip): ") or None
    bday  = input_strip("Birthday YYYY-MM-DD (blank to skip): ") or None
    phone = input_strip("Phone (blank to skip): ") or None
    ptype = None
    if phone:
        ptype = input_strip("Phone type (home/work/mobile) [mobile]: ") or "mobile"
    group = input_strip("Group name (blank to skip): ") or None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "CALL upsert_contact(%s, %s, %s, %s, %s, %s, %s)",
        (first, last, phone, ptype, email, bday, group)
    )
    conn.commit()
    print("  Contact saved.")
    cur.close()
    conn.close()


# ADD PHONE TO EXISTING CONTACT

def add_phone():
    name  = input_strip("Contact first name: ")
    phone = input_strip("Phone number: ")
    ptype = input_strip("Type (home/work/mobile) [mobile]: ") or "mobile"

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("  Phone added.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  Error: {e.pgerror or e}")
    finally:
        cur.close()
        conn.close()


# MOVE TO GROUP

def move_to_group():
    name  = input_strip("Contact first name: ")
    group = input_strip("Target group name: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL move_to_group(%s, %s)", (name, group))
    conn.commit()
    print("  Contact moved to group.")
    cur.close()
    conn.close()


# DELETE CONTACT

def delete_contact():
    print("  1 - by name")
    print("  2 - by phone")
    choice = input_strip("Choose: ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input_strip("First name: ")
        cur.execute("CALL delete_contact(%s, NULL)", (name,))
    elif choice == "2":
        phone = input_strip("Phone: ")
        cur.execute("CALL delete_contact(NULL, %s)", (phone,))
    else:
        print("  Invalid choice.")
        cur.close()
        conn.close()
        return

    conn.commit()
    print("  Contact deleted (if it existed).")
    cur.close()
    conn.close()


# EXPORT JSON

def export_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.first_name, c.last_name, c.email, c.birthday,
               g.name AS group_name,
               COALESCE(
                   json_agg(
                       json_build_object('phone', ph.phone, 'type', ph.type)
                   ) FILTER (WHERE ph.phone IS NOT NULL),
                   '[]'
               ) AS phones
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        ORDER BY c.first_name
    """)
    rows = cur.fetchall()

    data = []
    for row in rows:
        data.append({
            "first_name": row[0],
            "last_name":  row[1],
            "email":      row[2],
            "birthday":   str(row[3]) if row[3] else None,
            "group":      row[4],
            "phones":     row[5],
        })

    path = "contacts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"  Exported {len(data)} contacts to {path}.")
    cur.close()
    conn.close()


# IMPORT JSON

def import_json():
    path = input_strip("JSON file path [contacts.json]: ") or "contacts.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"  File not found: {path}")
        return

    conn = get_connection()
    cur = conn.cursor()
    inserted = updated = skipped = 0

    for item in data:
        first = item.get("first_name", "").strip()
        last  = item.get("last_name")
        if not first:
            continue

        cur.execute(
            "SELECT id FROM contacts WHERE first_name = %s AND (last_name = %s OR (last_name IS NULL AND %s IS NULL))",
            (first, last, last)
        )
        existing = cur.fetchone()

        if existing:
            act = input_strip(f'  "{first} {last or ""}" exists — skip/overwrite: ').lower()
            if act == "skip":
                skipped += 1
                continue
            if act == "overwrite":
                cid = existing[0]
                cur.execute("""
                    UPDATE contacts
                    SET last_name = %s, email = %s, birthday = %s
                    WHERE id = %s
                """, (last, item.get("email"), item.get("birthday"), cid))
                # re-insert phones
                for ph in item.get("phones", []):
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES(%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (cid, ph.get("phone"), ph.get("type", "mobile")))
                updated += 1
        else:
            # Resolve group
            gid = None
            grp = item.get("group")
            if grp:
                cur.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (grp,))
                cur.execute("SELECT id FROM groups WHERE name = %s", (grp,))
                gid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
                VALUES(%s, %s, %s, %s, %s)
                RETURNING id
            """, (first, last, item.get("email"), item.get("birthday"), gid))
            cid = cur.fetchone()[0]

            for ph in item.get("phones", []):
                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES(%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (cid, ph.get("phone"), ph.get("type", "mobile")))
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"  Done. Inserted: {inserted}, updated: {updated}, skipped: {skipped}.")


# IMPORT CSV 


def import_csv():
    path = input_strip("CSV file path [contacts.csv]: ") or "contacts.csv"
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"  File not found: {path}")
        return

    conn = get_connection()
    cur = conn.cursor()
    inserted = skipped = 0

    for row in rows:
        first = row.get("first_name", "").strip()
        if not first:
            continue
        last  = row.get("last_name", "").strip() or None
        email = row.get("email", "").strip() or None
        bday  = row.get("birthday", "").strip() or None
        grp   = row.get("group", "").strip() or None
        phone = row.get("phone", "").strip() or None
        ptype = row.get("phone_type", "mobile").strip() or "mobile"

        try:
            cur.execute(
                "CALL upsert_contact(%s, %s, %s, %s, %s, %s, %s)",
                (first, last, phone, ptype, email, bday, grp)
            )
            inserted += 1
        except psycopg2.Error as e:
            conn.rollback()
            print(f"  Row skipped ({first}): {e.pgerror or e}")
            skipped += 1
            # Re-open tx
            conn.autocommit = False

    conn.commit()
    cur.close()
    conn.close()
    print(f"  CSV import done. Inserted/updated: {inserted}, skipped: {skipped}.")


# BULK INSERT (names[] + phones[])

def bulk_insert():
    print("  Enter pairs of 'Full Name' and phone, one per line.")
    print("  Empty line to finish.")
    names, phones = [], []
    while True:
        name = input_strip("  Name (blank to finish): ")
        if not name:
            break
        phone = input_strip("  Phone: ")
        names.append(name)
        phones.append(phone)

    if not names:
        print("  Nothing to insert.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "CALL insert_many_contacts(%s, %s)",
        (names, phones)
    )
    conn.commit()
    # Report invalids if any
    cur.execute("SELECT * FROM tmp_invalid_contacts")
    bad = cur.fetchall()
    if bad:
        print("  Invalid rows:")
        for b in bad:
            print(f"    name={b[0]!r}  phone={b[1]!r}  reason={b[2]}")
    print("  Bulk insert complete.")
    cur.close()
    conn.close()


# MAIN MENU

MENU = """
PhoneBook
  
 1  Search (name/email/phone)
 2  Filter by group
 3  Search by email
 4  Sort contacts
 5  Paginated view
 6  Add / upsert contact
 7  Add phone to contact
 8  Move contact to group
 9  Delete contact
 10 Export to JSON
 11 Import from JSON
 12 Import from CSV
 13 Bulk insert (name+phone)     
 0  Exit                         
  
"""

def main():
    actions = {
        "1":  search_contacts,
        "2":  filter_group,
        "3":  search_by_email,
        "4":  sort_contacts,
        "5":  pagination,
        "6":  add_contact,
        "7":  add_phone,
        "8":  move_to_group,
        "9":  delete_contact,
        "10": export_json,
        "11": import_json,
        "12": import_csv,
        "13": bulk_insert,
    }

    while True:
        print(MENU)
        ch = input_strip("Choose: ")
        if ch == "0":
            print("  Bye!")
            break
        action = actions.get(ch)
        if action:
            try:
                action()
            except Exception as e:
                print(f"  Unexpected error: {e}")
        else:
            print("  Unknown option.")


if __name__ == "__main__":
    main()