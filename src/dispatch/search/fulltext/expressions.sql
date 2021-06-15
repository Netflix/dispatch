DROP TYPE IF EXISTS tsq_state CASCADE;

CREATE TYPE tsq_state AS (
    search_query text,
    parentheses_stack int,
    skip_for int,
    current_token text,
    current_index int,
    current_char text,
    previous_char text,
    tokens text[]
);

CREATE OR REPLACE FUNCTION tsq_append_current_token(state tsq_state)
RETURNS tsq_state AS $$
BEGIN
    IF state.current_token != '' THEN
        state.tokens := array_append(state.tokens, state.current_token);
        state.current_token := '';
    END IF;
    RETURN state;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_tokenize_character(state tsq_state)
RETURNS tsq_state AS $$
BEGIN
    IF state.current_char = '(' THEN
        state.tokens := array_append(state.tokens, '(');
        state.parentheses_stack := state.parentheses_stack + 1;
        state := tsq_append_current_token(state);
    ELSIF state.current_char = ')' THEN
        IF (state.parentheses_stack > 0 AND state.current_token != '') THEN
            state := tsq_append_current_token(state);
            state.tokens := array_append(state.tokens, ')');
            state.parentheses_stack := state.parentheses_stack - 1;
        END IF;
    ELSIF state.current_char = '"' THEN
        state.skip_for := position('"' IN substring(
            state.search_query FROM state.current_index + 1
        ));

        IF state.skip_for > 1 THEN
            state.tokens = array_append(
                state.tokens,
                substring(
                    state.search_query
                    FROM state.current_index FOR state.skip_for + 1
                )
            );
        ELSIF state.skip_for = 0 THEN
            state.current_token := state.current_token || state.current_char;
        END IF;
    ELSIF (
        state.current_char = '-' AND
        (state.current_index = 1 OR state.previous_char = ' ')
    ) THEN
        state.tokens := array_append(state.tokens, '-');
    ELSIF state.current_char = ' ' THEN
        state := tsq_append_current_token(state);
    ELSE
        state.current_token = state.current_token || state.current_char;
    END IF;
    RETURN state;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_tokenize(search_query text) RETURNS text[] AS $$
DECLARE
    state tsq_state;
BEGIN
    SELECT
        search_query::text AS search_query,
        0::int AS parentheses_stack,
        0 AS skip_for,
        ''::text AS current_token,
        0 AS current_index,
        ''::text AS current_char,
        ''::text AS previous_char,
        '{}'::text[] AS tokens
    INTO state;

    state.search_query := lower(trim(
        regexp_replace(search_query, '""+', '""', 'g')
    ));

    FOR state.current_index IN (
        SELECT generate_series(1, length(state.search_query))
    ) LOOP
        state.current_char := substring(
            search_query FROM state.current_index FOR 1
        );

        IF state.skip_for > 0 THEN
            state.skip_for := state.skip_for - 1;
            CONTINUE;
        END IF;

        state := tsq_tokenize_character(state);
        state.previous_char := state.current_char;
    END LOOP;
    state := tsq_append_current_token(state);

    state.tokens := array_nremove(state.tokens, '(', -state.parentheses_stack);

    RETURN state.tokens;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- Processes an array of text search tokens and returns a tsquery
CREATE OR REPLACE FUNCTION tsq_process_tokens(config regconfig, tokens text[])
RETURNS tsquery AS $$
DECLARE
    result_query text;
    previous_value text;
    value text;
BEGIN
    result_query := '';

    FOREACH value IN ARRAY tokens LOOP
        IF value = '"' THEN
            CONTINUE;
        END IF;

        IF value = 'or' THEN
            value := ' | ';
        END IF;

        IF left(value, 1) = '"' AND right(value, 1) = '"' THEN
            value := phraseto_tsquery(config, value);
        ELSIF value NOT IN ('(', ' | ', ')', '-') THEN
            value := quote_literal(value) || ':*';
        END IF;

        IF previous_value = '-' THEN
            IF value = '(' THEN
                value := '!' || value;
            ELSIF value = ' | ' THEN
                CONTINUE;
            ELSE
                value := '!(' || value || ')';
            END IF;
        END IF;

        SELECT
            CASE
                WHEN result_query = '' THEN value
                WHEN previous_value = ' | ' AND value = ' | ' THEN result_query
                WHEN previous_value = ' | ' THEN result_query || ' | ' || value
                WHEN previous_value IN ('!(', '(') OR value = ')' THEN result_query || value
                WHEN value != ' | ' THEN result_query || ' & ' || value
                ELSE result_query
            END
        INTO result_query;

        IF result_query = ' | ' THEN
            result_query := '';
        END IF;

        previous_value := value;
    END LOOP;

    RETURN to_tsquery(config, result_query);
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_process_tokens(tokens text[])
RETURNS tsquery AS $$
    SELECT tsq_process_tokens(get_current_ts_config(), tokens);
$$ LANGUAGE SQL IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_parse(config regconfig, search_query text)
RETURNS tsquery AS $$
    SELECT tsq_process_tokens(config, tsq_tokenize(search_query));
$$ LANGUAGE SQL IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_parse(config text, search_query text)
RETURNS tsquery AS $$
    SELECT tsq_parse(config::regconfig, search_query);
$$ LANGUAGE SQL IMMUTABLE;


CREATE OR REPLACE FUNCTION tsq_parse(search_query text) RETURNS tsquery AS $$
    SELECT tsq_parse(get_current_ts_config(), search_query);
$$ LANGUAGE SQL IMMUTABLE;


-- remove first N elements equal to the given value from the array (array
-- must be one-dimensional)
--
-- If negative value is given as the third argument the removal of elements
-- starts from the last array element.
CREATE OR REPLACE FUNCTION array_nremove(anyarray, anyelement, int)
RETURNS ANYARRAY AS $$
    WITH replaced_positions AS (
        SELECT UNNEST(
            CASE
            WHEN $2 IS NULL THEN
                '{}'::int[]
            WHEN $3 > 0 THEN
                (array_positions($1, $2))[1:$3]
            WHEN $3 < 0 THEN
                (array_positions($1, $2))[
                    (cardinality(array_positions($1, $2)) + $3 + 1):
                ]
            ELSE
                '{}'::int[]
            END
        ) AS position
    )
    SELECT COALESCE((
        SELECT array_agg(value)
        FROM unnest($1) WITH ORDINALITY AS t(value, index)
        WHERE index NOT IN (SELECT position FROM replaced_positions)
    ), $1[1:0]);
$$ LANGUAGE SQL IMMUTABLE;
