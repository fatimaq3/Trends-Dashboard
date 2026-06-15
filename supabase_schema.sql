CREATE TABLE IF NOT EXISTS trends_interest (
    id          BIGSERIAL PRIMARY KEY,
    keyword     TEXT NOT NULL,
    category    TEXT NOT NULL,
    date        DATE NOT NULL,
    interest    INTEGER NOT NULL CHECK (interest BETWEEN 0 AND 100),
    geo         TEXT DEFAULT 'SA',
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trends_trending (
    id          BIGSERIAL PRIMARY KEY,
    keyword     TEXT NOT NULL,
    rank        INTEGER NOT NULL,
    geo         TEXT DEFAULT 'SA',
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trends_related (
    id            BIGSERIAL PRIMARY KEY,
    main_keyword  TEXT NOT NULL,
    related_query TEXT NOT NULL,
    value         INTEGER,
    query_type    TEXT,
    category      TEXT,
    fetched_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE trends_interest  ENABLE ROW LEVEL SECURITY;
ALTER TABLE trends_trending  ENABLE ROW LEVEL SECURITY;
ALTER TABLE trends_related   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read interest"  ON trends_interest  FOR SELECT USING (true);
CREATE POLICY "Public read trending"  ON trends_trending  FOR SELECT USING (true);
CREATE POLICY "Public read related"   ON trends_related   FOR SELECT USING (true);
