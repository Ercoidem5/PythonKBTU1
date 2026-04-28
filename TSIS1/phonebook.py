import psycopg2
import json
from connect import get_connection


def print_rows(rows):
    if not rows:
        print("No results.")
        return

    for row in rows:
        print(row)


# ---------------- SEARCH ----------------
def search_contacts():
    query = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    print_rows(rows)

    cur.close()
    conn.close()


# ---------------- FILTER GROUP ----------------
def filter_group():
    group = input("Group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.first_name, c.last_name, g.name
        FROM phonebook c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name=%s
    """, (group,))

    print_rows(cur.fetchall())

    cur.close()
    conn.close()


# ---------------- SORT ----------------
def sort_contacts():
    print("1-name")
    print("2-birthday")
    print("3-date added")

    choice = input("Choose: ")

    field = "first_name"

    if choice == "2":
        field = "birthday"
    elif choice == "3":
        field = "created_at"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM phonebook ORDER BY {field}")
    print_rows(cur.fetchall())

    cur.close()
    conn.close()


# ---------------- PAGINATION ----------------
def pagination():
    page = 1
    size = 5

    conn = get_connection()
    cur = conn.cursor()

    while True:
        cur.execute("SELECT * FROM get_contacts_paginated(%s,%s)", (size, page))
        rows = cur.fetchall()

        print(f"\nPage {page}")
        print_rows(rows)

        cmd = input("n-next / p-prev / q-quit: ")

        if cmd == "n":
            page += 1
        elif cmd == "p" and page > 1:
            page -= 1
        elif cmd == "q":
            break

    cur.close()
    conn.close()


# ---------------- EXPORT JSON ----------------
def export_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.first_name,p.last_name,p.email,p.birthday,g.name
        FROM phonebook p
        LEFT JOIN groups g ON p.group_id=g.id
    """)

    rows = cur.fetchall()

    data = []

    for row in rows:
        data.append({
            "first_name": row[0],
            "last_name": row[1],
            "email": row[2],
            "birthday": str(row[3]),
            "group": row[4]
        })

    with open("contacts.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Exported.")


# ---------------- IMPORT JSON ----------------
def import_json():
    with open("contacts.json", "r") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()

    for item in data:
        cur.execute(
            "SELECT id FROM phonebook WHERE first_name=%s",
            (item["first_name"],)
        )

        exists = cur.fetchone()

        if exists:
            act = input(f'{item["first_name"]} exists. skip/overwrite: ')

            if act == "skip":
                continue

            if act == "overwrite":
                cur.execute("""
                    UPDATE phonebook
                    SET last_name=%s,email=%s,birthday=%s
                    WHERE first_name=%s
                """, (
                    item["last_name"],
                    item["email"],
                    item["birthday"],
                    item["first_name"]
                ))
        else:
            cur.execute("""
                INSERT INTO phonebook(first_name,last_name,email,birthday)
                VALUES(%s,%s,%s,%s)
            """, (
                item["first_name"],
                item["last_name"],
                item["email"],
                item["birthday"]
            ))

    conn.commit()
    cur.close()
    conn.close()

    print("Imported.")


# ---------------- MENU ----------------
def main():
    while True:
        print("""
1 Search
2 Filter group
3 Sort
4 Pagination
5 Export JSON
6 Import JSON
0 Exit
""")

        ch = input("Choose: ")

        if ch == "1":
            search_contacts()
        elif ch == "2":
            filter_group()
        elif ch == "3":
            sort_contacts()
        elif ch == "4":
            pagination()
        elif ch == "5":
            export_json()
        elif ch == "6":
            import_json()
        elif ch == "0":
            break


if __name__ == "__main__":
    main()