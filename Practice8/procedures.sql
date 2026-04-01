CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name  VARCHAR DEFAULT NULL,
    p_phone      VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO phonebook (first_name, last_name, phone)
    VALUES (p_first_name, p_last_name, p_phone)
    ON CONFLICT (phone)
    DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name  = EXCLUDED.last_name;

    RAISE NOTICE 'upsert_contact: processed contact "% %" with phone %',
                 p_first_name, COALESCE(p_last_name, ''), p_phone;
END;
$$;



CREATE OR REPLACE PROCEDURE insert_many_contacts(
    names  VARCHAR[],
    phones VARCHAR[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i           INT;
    v_name      VARCHAR;
    v_phone     VARCHAR;
    v_first     VARCHAR;
    v_last      VARCHAR;
BEGIN
    IF array_length(names, 1) IS DISTINCT FROM array_length(phones, 1) THEN
        RAISE EXCEPTION 'names and phones arrays must have the same length';
    END IF;

    DROP TABLE IF EXISTS tmp_invalid_contacts;
    CREATE TEMP TABLE tmp_invalid_contacts (
        name   VARCHAR,
        phone  VARCHAR,
        reason VARCHAR
    );

    FOR i IN 1 .. array_length(names, 1) LOOP
        v_name  := TRIM(names[i]);
        v_phone := TRIM(phones[i]);

        v_first := SPLIT_PART(v_name, ' ', 1);
        v_last  := NULLIF(TRIM(SUBSTRING(v_name FROM POSITION(' ' IN v_name))), '');

        IF v_name = '' THEN
            INSERT INTO tmp_invalid_contacts VALUES (v_name, v_phone, 'empty name');
            CONTINUE;
        END IF;

        IF v_phone = '' THEN
            INSERT INTO tmp_invalid_contacts VALUES (v_name, v_phone, 'empty phone');
            CONTINUE;
        END IF;



        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (v_first, v_last, v_phone)
        ON CONFLICT (phone)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name  = EXCLUDED.last_name;

    END LOOP;

    RAISE NOTICE 'insert_many_contacts: finished. Check tmp_invalid_contacts for rejected rows.';
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(
    p_username VARCHAR DEFAULT NULL,
    p_phone    VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    rows_deleted INT;
BEGIN
    IF p_username IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'delete_contact: at least one of p_username or p_phone must be provided';
    END IF;

    DELETE FROM phonebook
    WHERE
        (p_username IS NOT NULL AND first_name = p_username)
        OR
        (p_phone    IS NOT NULL AND phone      = p_phone);

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RAISE NOTICE 'delete_contact: % row(s) deleted', rows_deleted;
END;
$$;