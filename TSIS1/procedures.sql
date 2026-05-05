
-- Upsert a single contact 
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR(255),
    p_last_name  VARCHAR(255) DEFAULT NULL,
    p_phone      VARCHAR(255) DEFAULT NULL,
    p_type       VARCHAR(10)  DEFAULT 'mobile',
    p_email      VARCHAR(100) DEFAULT NULL,
    p_birthday   DATE         DEFAULT NULL,
    p_group_name VARCHAR(50)  DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
    v_group_id   INT;
BEGIN
    -- Resolve group
    IF p_group_name IS NOT NULL THEN
        INSERT INTO groups(name) VALUES(p_group_name)
        ON CONFLICT(name) DO NOTHING;
        SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    END IF;

    -- Upsert contact (match by first+last name as identity)
    INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
    VALUES(p_first_name, p_last_name, p_email, p_birthday, v_group_id)
    ON CONFLICT DO NOTHING
    RETURNING id INTO v_contact_id;

    -- If nothing was inserted, fetch existing id
    IF v_contact_id IS NULL THEN
        SELECT id INTO v_contact_id
        FROM contacts
        WHERE first_name = p_first_name
          AND (last_name = p_last_name OR (last_name IS NULL AND p_last_name IS NULL))
        LIMIT 1;

        -- Update fields
        UPDATE contacts
        SET email    = COALESCE(p_email,    email),
            birthday = COALESCE(p_birthday, birthday),
            group_id = COALESCE(v_group_id, group_id)
        WHERE id = v_contact_id;
    END IF;

    -- Insert phone if provided (skip duplicate)
    IF p_phone IS NOT NULL AND v_contact_id IS NOT NULL THEN
        INSERT INTO phones(contact_id, phone, type)
        VALUES(v_contact_id, p_phone, p_type)
        ON CONFLICT DO NOTHING;
    END IF;
END;
$$;


-- Bulk-insert 
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    names  VARCHAR[],
    phones VARCHAR[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i       INT;
    v_name  VARCHAR(255);
    v_phone VARCHAR(255);
    v_first VARCHAR(255);
    v_last  VARCHAR(255);
    v_cid   INT;
BEGIN
    DROP TABLE IF EXISTS tmp_invalid_contacts;
    CREATE TEMP TABLE tmp_invalid_contacts (
        name   VARCHAR,
        phone  VARCHAR,
        reason VARCHAR
    );

    FOR i IN 1 .. array_length(names, 1) LOOP
        v_name  := TRIM(names[i]);
        v_phone := TRIM(phones[i]);

        IF v_name = '' OR v_phone = '' THEN
            INSERT INTO tmp_invalid_contacts VALUES(v_name, v_phone, 'empty field');
            CONTINUE;
        END IF;

        v_first := SPLIT_PART(v_name, ' ', 1);
        v_last  := NULLIF(TRIM(SUBSTRING(v_name FROM POSITION(' ' IN v_name))), '');

        INSERT INTO contacts(first_name, last_name)
        VALUES(v_first, v_last)
        ON CONFLICT DO NOTHING
        RETURNING id INTO v_cid;

        IF v_cid IS NULL THEN
            SELECT id INTO v_cid FROM contacts
            WHERE first_name = v_first
              AND (last_name = v_last OR (last_name IS NULL AND v_last IS NULL))
            LIMIT 1;
        END IF;

        IF v_cid IS NOT NULL THEN
            INSERT INTO phones(contact_id, phone, type)
            VALUES(v_cid, v_phone, 'mobile')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END;
$$;


-- Delete contact by username or phone
CREATE OR REPLACE PROCEDURE delete_contact(
    p_username VARCHAR(255) DEFAULT NULL,
    p_phone    VARCHAR(255) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_phone IS NOT NULL THEN
        DELETE FROM contacts
        WHERE id IN (
            SELECT contact_id FROM phones WHERE phone = p_phone
        );
    END IF;

    IF p_username IS NOT NULL THEN
        DELETE FROM contacts
        WHERE first_name = p_username;
    END IF;
END;
$$;


-- Add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cid INT;
BEGIN
    SELECT id INTO v_cid
    FROM contacts
    WHERE first_name = p_contact_name
    LIMIT 1;

    IF v_cid IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES(v_cid, p_phone, p_type);
END;
$$;


-- Move contact to a group 
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_gid INT;
BEGIN
    INSERT INTO groups(name) VALUES(p_group_name)
    ON CONFLICT(name) DO NOTHING;

    SELECT id INTO v_gid FROM groups WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = v_gid
    WHERE first_name = p_contact_name;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id         INT,
    full_name  TEXT,
    email      VARCHAR(100),
    phone      VARCHAR(20),
    phone_type VARCHAR(10),
    grp        VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT DISTINCT ON (c.id, ph.phone)
               c.id,
               (c.first_name || ' ' || COALESCE(c.last_name, ''))::TEXT AS full_name,
               c.email,
               ph.phone,
               ph.type  AS phone_type,
               g.name   AS grp
        FROM contacts c
        LEFT JOIN phones ph ON ph.contact_id = c.id
        LEFT JOIN groups g  ON g.id = c.group_id
        WHERE c.first_name ILIKE '%' || p_query || '%'
           OR c.last_name  ILIKE '%' || p_query || '%'
           OR c.email      ILIKE '%' || p_query || '%'
           OR ph.phone     ILIKE '%' || p_query || '%'
        ORDER BY c.id, ph.phone;
END;
$$;


-- Paginated contact list
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    page_size INT,
    page_num  INT
)
RETURNS TABLE(
    id         INT,
    first_name VARCHAR(100),
    last_name  VARCHAR(100),
    email      VARCHAR(100),
    birthday   DATE,
    grp        VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT c.id,
               c.first_name,
               c.last_name,
               c.email,
               c.birthday,
               g.name AS grp
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.id
        LIMIT  page_size
        OFFSET (page_num - 1) * page_size;
END;
$$;