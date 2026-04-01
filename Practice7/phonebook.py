import csv
import psycopg2
from connect import get_connection


def create_table():
    sql = """
        CREATE TABLE IF NOT EXISTS phonebook (
            id         SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name  VARCHAR(100),
            phone      VARCHAR(20)  NOT NULL UNIQUE
        );
    """
    conn = get_connection()
    try:
        with conn:                      
            with conn.cursor() as cur:
                cur.execute(sql)
        print(" Table 'phonebook' is ready.")
    except psycopg2.Error as e:
        print(f"create_table: {e}")
    finally:
        conn.close()



def insert_from_csv(filepath: str):

    sql = """
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING;
    """
    rows = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append((
                    row["first_name"].strip(),
                    row.get("last_name", "").strip(),
                    row["phone"].strip(),
                ))
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return

    if not rows:
        print("CSV file is empty or another problems.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)   
        print(f"Imported {len(rows)} row(s) from '{filepath}'.")
    except psycopg2.Error as e:
        print(f"insert_from_csv: {e}")
    finally:
        conn.close()


def insert_from_console():
    print("Add a new contact ")
    first_name = input(" First name : ").strip()
    last_name  = input(" Last name  : ").strip()
    phone      = input(" Phone      : ").strip()

    if not first_name or not phone:
        print("First name and phone are required.")
        return

    sql = """
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING
        RETURNING id;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (first_name, last_name, phone))
                result = cur.fetchone()
                if result:
                    print(f" Contact added with id={result[0]}.")
                else:
                    print("Phone number already exists - contact not added.")
    except psycopg2.Error as e:
        print(f" insert_from_console: {e}")
    finally:
        conn.close()


def update_contact():

    print("Update a contact")
    search_name = input("  Enter the current first name to find: ").strip()
    if not search_name:
        return

    found = search_contacts(first_name=search_name, silent=True)
    if not found:
        print(f"No contacts found with first name '{search_name}'.")
        return

    print("What would you like to update?")
    print("1 - First name")
    print("2 - Phone number")
    print("3 - Both")
    choice = input("  Choice: ").strip()

    new_first = new_phone = None
    if choice in ("1", "3"):
        new_first = input("  New first name : ").strip()
    if choice in ("2", "3"):
        new_phone = input("  New phone      : ").strip()

    if not new_first and not new_phone:
        print("Nothing to update.")
        return

    parts, params = [], []
    if new_first:
        parts.append("first_name = %s")
        params.append(new_first)
    if new_phone:
        parts.append("phone = %s")
        params.append(new_phone)
    params.append(search_name)

    sql = f"UPDATE phonebook SET {', '.join(parts)} WHERE first_name = %s"

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                print(f"[OK] {cur.rowcount} row(s) updated.")
    except psycopg2.Error as e:
        print(f"[ERROR] update_contact: {e}")
    finally:
        conn.close()


def search_contacts(first_name: str = None, phone_prefix: str = None, silent: bool = False):
    
    conditions, params = [], []

    if first_name:
        conditions.append("first_name ILIKE %s")
        params.append(f"%{first_name}%")
    if phone_prefix:
        conditions.append("phone LIKE %s")
        params.append(f"{phone_prefix}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT id, first_name, last_name, phone FROM phonebook {where} ORDER BY first_name;"

    conn = get_connection()
    rows = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    except psycopg2.Error as e:
        print(f" search_contacts: {e}")
    finally:
        conn.close()

    if not silent:
        if rows:
            print(f"\n{'ID':<5} {'First name':<15} {'Last name':<15} {'Phone':<20}")
            print("-" * 57)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<15} {(row[2] or ''):<15} {row[3]:<20}")
        else:
            print("No contacts found.")
    return rows


def query_menu():
    print("Search contacts")
    print("  1 – By first name")
    print("  2 – By phone prefix")
    print("  3 – Show all")
    choice = input("  Choice: ").strip()

    if choice == "1":
        name = input("  First name (partial OK): ").strip()
        search_contacts(first_name=name)
    elif choice == "2":
        prefix = input("  Phone prefix: ").strip()
        search_contacts(phone_prefix=prefix)
    elif choice == "3":
        search_contacts()
    else:
        print("Invalid choice.")


def delete_contact():
    print("Delete a contact:")
    print("  1 – By first name")
    print("  2 – By phone number")
    choice = input("  Choice: ").strip()

    if choice == "1":
        name = input("  First name: ").strip()
        if not name:
            return
        sql    = "DELETE FROM phonebook WHERE first_name = %s"
        params = (name,)
    elif choice == "2":
        phone = input("  Phone: ").strip()
        if not phone:
            return
        sql    = "DELETE FROM phonebook WHERE phone = %s"
        params = (phone,)
    else:
        print("[WARN] Invalid choice.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                print(f"[OK] {cur.rowcount} row(s) deleted.")
    except psycopg2.Error as e:
        print(f"[ERROR] delete_contact: {e}")
    finally:
        conn.close()


MENU = """
PhoneBook                    
1. Import contacts from CSV         
2. Add contact (console)            
3. Update contact                   
4. Search / list contacts           
5. Delete contact                   
0. Exit                             

"""

def main():
    create_table()

    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        if choice == "1":
            path = "contacts.csv"
            insert_from_csv(path)
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_menu()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("[WARN] Unknown option, please try again.")


if __name__ == "__main__":
    main()