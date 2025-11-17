-- AI Freelance Search App - Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'premium')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);

-- User skills table
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level VARCHAR(50) CHECK (proficiency_level IN ('beginner', 'intermediate', 'expert')),
    years_experience DECIMAL(3,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);

-- User preferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_categories TEXT[],
    min_hourly_rate DECIMAL(10,2),
    max_hourly_rate DECIMAL(10,2),
    min_fixed_price DECIMAL(10,2),
    preferred_job_types TEXT[],
    preferred_locations TEXT[],
    email_alerts_enabled BOOLEAN DEFAULT TRUE,
    alert_frequency VARCHAR(50) DEFAULT 'daily' CHECK (alert_frequency IN ('realtime', 'hourly', 'daily', 'weekly')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Freelance platforms table
CREATE TABLE freelance_platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    base_url TEXT NOT NULL,
    logo_url TEXT,
    has_api BOOLEAN DEFAULT FALSE,
    scraper_enabled BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platforms_name ON freelance_platforms(name);

-- Insert default platforms
INSERT INTO freelance_platforms (name, base_url, has_api, scraper_enabled) VALUES
('Upwork', 'https://www.upwork.com', TRUE, TRUE),
('Freelancer', 'https://www.freelancer.com', FALSE, TRUE),
('Fiverr', 'https://www.fiverr.com', FALSE, TRUE),
('Guru', 'https://www.guru.com', FALSE, TRUE);

-- Clients table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_client_id VARCHAR(255),
    name VARCHAR(255),
    company_name VARCHAR(255),
    profile_url TEXT,
    location VARCHAR(255),
    timezone VARCHAR(100),
    member_since DATE,
    total_jobs_posted INTEGER DEFAULT 0,
    total_hires INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    payment_verified BOOLEAN DEFAULT FALSE,
    average_rating DECIMAL(3,2),
    response_time_hours INTEGER,
    project_completion_rate DECIMAL(5,2),
    trust_score INTEGER,
    last_active TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, external_client_id)
);

CREATE INDEX idx_clients_platform_id ON clients(platform_id);
CREATE INDEX idx_clients_trust_score ON clients(trust_score);
CREATE INDEX idx_clients_external_client_id ON clients(external_client_id);

-- Client reviews table
CREATE TABLE client_reviews (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    reviewer_name VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    project_title VARCHAR(255),
    project_value DECIMAL(10,2),
    review_date DATE,
    sentiment_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_client_reviews_client_id ON client_reviews(client_id);

-- Client red flags table
CREATE TABLE client_red_flags (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL,
    description TEXT,
    severity VARCHAR(50) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_client_red_flags_client_id ON client_red_flags(client_id);
CREATE INDEX idx_client_red_flags_severity ON client_red_flags(severity);

-- Jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_job_id VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(255),
    subcategory VARCHAR(255),
    skills_required TEXT[],
    job_type VARCHAR(50) CHECK (job_type IN ('hourly', 'fixed', 'both')),
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    hourly_rate DECIMAL(10,2),
    fixed_price DECIMAL(10,2),
    duration VARCHAR(100),
    experience_level VARCHAR(50) CHECK (experience_level IN ('entry', 'intermediate', 'expert')),
    client_id INTEGER REFERENCES clients(id),
    posted_date TIMESTAMP,
    applications_count INTEGER DEFAULT 0,
    job_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, external_job_id)
);

CREATE INDEX idx_jobs_platform_id ON jobs(platform_id);
CREATE INDEX idx_jobs_client_id ON jobs(client_id);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);

-- Job applications table
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'rejected', 'hired')),
    proposal_text TEXT,
    bid_amount DECIMAL(10,2),
    notes TEXT,
    UNIQUE(user_id, job_id)
);

CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_job_id ON job_applications(job_id);

-- Company research table
CREATE TABLE company_research (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE UNIQUE,
    company_name VARCHAR(255),
    linkedin_url TEXT,
    linkedin_found BOOLEAN DEFAULT FALSE,
    linkedin_employee_count INTEGER,
    website_url TEXT,
    website_found BOOLEAN DEFAULT FALSE,
    social_media_presence JSONB,
    recent_news JSONB,
    digital_footprint_score INTEGER CHECK (digital_footprint_score >= 0 AND digital_footprint_score <= 100),
    research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scam reports table
CREATE TABLE scam_reports (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    reporter_user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    report_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    evidence_urls TEXT[],
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'dismissed')),
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scam_reports_client_id ON scam_reports(client_id);
CREATE INDEX idx_scam_reports_status ON scam_reports(status);

-- Saved searches table
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    search_criteria JSONB NOT NULL,
    alert_enabled BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);

-- User analytics table
CREATE TABLE user_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    searches_performed INTEGER DEFAULT 0,
    jobs_viewed INTEGER DEFAULT 0,
    jobs_applied INTEGER DEFAULT 0,
    vetting_reports_generated INTEGER DEFAULT 0,
    average_trust_score_viewed DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_user_analytics_date ON user_analytics(date);

-- Platform analytics table
CREATE TABLE platform_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    jobs_scraped INTEGER DEFAULT 0,
    new_clients_added INTEGER DEFAULT 0,
    average_job_budget DECIMAL(10,2),
    average_trust_score DECIMAL(5,2),
    top_categories JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform_id)
);

CREATE INDEX idx_platform_analytics_date ON platform_analytics(date);
CREATE INDEX idx_platform_analytics_platform_id ON platform_analytics(platform_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scam_reports_updated_at BEFORE UPDATE ON scam_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_searches_updated_at BEFORE UPDATE ON saved_searches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
