CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE (
    id         INT,
    first_name VARCHAR,
    last_name  VARCHAR,
    phone      VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT
            p.id,
            p.first_name,
            p.last_name,
            p.phone
        FROM phonebook p
        WHERE
            p.first_name ILIKE '%' || pattern || '%'
            OR p.last_name  ILIKE '%' || pattern || '%'
            OR p.phone      ILIKE '%' || pattern || '%'
        ORDER BY p.first_name;
END;
$$;


CREATE OR REPLACE FUNCTION get_contacts_paginated(
    page_size INT,
    page_num  INT
)
RETURNS TABLE (
    id         INT,
    first_name VARCHAR,
    last_name  VARCHAR,
    phone      VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_offset INT;
BEGIN
    -- Validate inputs
    IF page_size <= 0 THEN
        RAISE EXCEPTION 'page_size must be a positive integer, got %', page_size;
    END IF;
    IF page_num <= 0 THEN
        RAISE EXCEPTION 'page_num must be a positive integer, got %', page_num;
    END IF;

    v_offset := (page_num - 1) * page_size;

    RETURN QUERY
        SELECT
            p.id,
            p.first_name,
            p.last_name,
            p.phone
        FROM phonebook p
        ORDER BY p.id
        LIMIT  page_size
        OFFSET v_offset;
END;
$$;