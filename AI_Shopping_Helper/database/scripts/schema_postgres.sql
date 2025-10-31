-- PostgreSQL schema for AI Shopping Helper
-- Run via psql or the provided init_postgres_schema.py

CREATE TABLE IF NOT EXISTS public.products (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    price           NUMERIC(12,2) DEFAULT 0,
    rating          REAL DEFAULT 0,
    platform        TEXT,
    url             TEXT,
    specs           JSONB,
    quality_score   REAL DEFAULT 0,
    final_score     REAL DEFAULT 0,
    image_url       TEXT,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_final_score ON public.products(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_products_price ON public.products(price);

CREATE TABLE IF NOT EXISTS public.categories (
    name          TEXT PRIMARY KEY,
    display_name  TEXT,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS public.user_feedback (
    id           BIGSERIAL PRIMARY KEY,
  product_id   BIGINT REFERENCES public.products(id) ON DELETE CASCADE,
    user_rating  INT,
    is_helpful   BOOLEAN,
    comments     TEXT,
    user_ip      TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing CLIP hybrid search results
CREATE TABLE IF NOT EXISTS public.clip_search_results (
    id              BIGSERIAL PRIMARY KEY,
    image_name      TEXT NOT NULL,
    raw_json_result JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clip_search_created ON public.clip_search_results(created_at DESC);

-- Triggers to keep updated_at fresh
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'products_set_updated_at'
  ) THEN
    CREATE TRIGGER products_set_updated_at
      BEFORE UPDATE ON public.products
      FOR EACH ROW
      EXECUTE FUNCTION public.set_updated_at();
  END IF;
END$$;
