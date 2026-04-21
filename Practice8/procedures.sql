    CREATE OR REPLACE PROCEDURE upsert_contact(
        p_first_name VARCHAR(255),
        p_last_name  VARCHAR(255) DEFAULT NULL,
        p_phone      VARCHAR(255) DEFAULT NULL
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
        v_name      VARCHAR(255);
        v_phone     VARCHAR(255);
        v_first     VARCHAR(255);
        v_last      VARCHAR(255);
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

            v_first := SPLIT_PART(v_name, ' ', 1);
            v_last  := NULLIF(TRIM(SUBSTRING(v_name FROM POSITION(' ' IN v_name))), '');

            INSERT INTO phonebook (first_name, last_name, phone)
            VALUES (v_first, v_last, v_phone)
            ON CONFLICT (phone)
            DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name  = EXCLUDED.last_name;

        END LOOP;
    END;
    $$;


    CREATE OR REPLACE PROCEDURE delete_contact(
        p_username VARCHAR(255) DEFAULT NULL,
        p_phone    VARCHAR(255) DEFAULT NULL
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        rows_deleted INT;
    BEGIN


        DELETE FROM phonebook
        WHERE
            (p_username IS NOT NULL AND first_name = p_username)
            OR
            (p_phone    IS NOT NULL AND phone      = p_phone);

        GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    END;
    $$;