CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE (
    id         INT,
    first_name VARCHAR(255),
    last_name  VARCHAR(255),
    phone      VARCHAR(255)
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
    first_name VARCHAR(255),
    last_name  VARCHAR(255),
    phone      VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_offset INT;
BEGIN

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