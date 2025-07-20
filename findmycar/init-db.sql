-- Initialize FindMyCar database with proper indexes and constraints

-- Create database (will be created by docker-compose, but included for reference)
-- CREATE DATABASE findmycar;

-- Ensure we're using the right database
\c findmycar;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_vehicles_source ON vehicles(source);
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX IF NOT EXISTS idx_vehicles_year ON vehicles(year);
CREATE INDEX IF NOT EXISTS idx_vehicles_price ON vehicles(price);
CREATE INDEX IF NOT EXISTS idx_vehicles_location ON vehicles(location);
CREATE INDEX IF NOT EXISTS idx_vehicles_created_at ON vehicles(created_at);
CREATE INDEX IF NOT EXISTS idx_vehicles_deal_rating ON vehicles(deal_rating);
CREATE INDEX IF NOT EXISTS idx_vehicles_carmax_store ON vehicles(carmax_store);
CREATE INDEX IF NOT EXISTS idx_vehicles_bat_auction_id ON vehicles(bat_auction_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_auction_status ON vehicles(auction_status);
CREATE INDEX IF NOT EXISTS idx_vehicles_current_bid ON vehicles(current_bid);
CREATE INDEX IF NOT EXISTS idx_vehicles_time_left ON vehicles(time_left);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_year ON vehicles(make, model, year);
CREATE INDEX IF NOT EXISTS idx_vehicles_source_created ON vehicles(source, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vehicles_price_range ON vehicles(price) WHERE price IS NOT NULL;

-- Full text search index for title (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_vehicles_title_search ON vehicles USING gin(to_tsvector('english', title));

-- User sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_vehicles_updated_at ON vehicles;
CREATE TRIGGER update_vehicles_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create some useful views for analytics
CREATE OR REPLACE VIEW vehicle_summary AS
SELECT 
    source,
    make,
    COUNT(*) as total_listings,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(mileage) as avg_mileage,
    COUNT(CASE WHEN deal_rating = 'Great Deal' THEN 1 END) as great_deals,
    COUNT(CASE WHEN deal_rating = 'Good Deal' THEN 1 END) as good_deals
FROM vehicles 
WHERE price IS NOT NULL
GROUP BY source, make
ORDER BY source, make;

CREATE OR REPLACE VIEW daily_ingestion_stats AS
SELECT 
    DATE(created_at) as date,
    source,
    COUNT(*) as vehicles_added,
    AVG(price) as avg_price,
    COUNT(CASE WHEN deal_rating IN ('Great Deal', 'Good Deal') THEN 1 END) as good_deals
FROM vehicles 
GROUP BY DATE(created_at), source
ORDER BY date DESC, source;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO findmycar;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO findmycar;