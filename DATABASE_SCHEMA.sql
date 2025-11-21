-- Aegis OS Database Schema - PostgreSQL
-- Complete production-ready schema with all tables

-- ============= USERS =============
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ============= 2FA =============
CREATE TABLE two_fa_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secret_key VARCHAR(255),
    is_enabled BOOLEAN DEFAULT FALSE,
    backup_codes TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- ============= LICENSES =============
CREATE TABLE licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATE NOT NULL,
    hardware_id VARCHAR(255),
    INDEX idx_user_licenses (user_id),
    INDEX idx_license_status (status)
);

-- ============= TEAMS =============
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id),
    plan VARCHAR(50) DEFAULT 'basic_team',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id)
);

-- ============= PAYMENTS =============
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    license_id UUID REFERENCES licenses(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(255),
    stripe_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_user_payments (user_id)
);

-- ============= INVOICES =============
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    payment_id UUID REFERENCES payments(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft',
    due_date DATE,
    paid_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============= WEBHOOKS =============
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    url VARCHAR(255) NOT NULL,
    events TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    failure_count INT DEFAULT 0,
    last_triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============= AUDIT LOG =============
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_action_log (action),
    INDEX idx_user_log (user_id)
);

-- ============= SUPPORT TICKETS =============
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(50) DEFAULT 'normal',
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============= BACKUPS =============
CREATE TABLE backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule VARCHAR(50),
    retention_days INT DEFAULT 30,
    last_backup_at TIMESTAMP,
    next_backup_at TIMESTAMP,
    backup_size_gb DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============= ANALYTICS =============
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100),
    user_id UUID REFERENCES users(id),
    license_id UUID REFERENCES licenses(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_created_date (created_at)
);

-- ============= API KEYS =============
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- ============= NOTIFICATIONS =============
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(100),
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_notifications (user_id)
);

-- ============= INDEXES FOR PERFORMANCE =============
CREATE INDEX idx_users_created ON users(created_at);
CREATE INDEX idx_licenses_expires ON licenses(expires_at);
CREATE INDEX idx_payments_created ON payments(created_at);
CREATE INDEX idx_audit_timestamp ON audit_log(created_at);

-- ============= VIEWS FOR ANALYTICS =============
CREATE VIEW user_statistics AS
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN email_verified THEN 1 END) as verified_users,
    COUNT(CASE WHEN is_active THEN 1 END) as active_users,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as new_users_30d
FROM users;

CREATE VIEW license_statistics AS
SELECT 
    tier,
    COUNT(*) as count,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
    COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired,
    SUM(CASE WHEN tier = 'basic' THEN 49 WHEN tier = 'gamer' THEN 99 WHEN tier = 'ai-dev' THEN 149 WHEN tier = 'server' THEN 199 ELSE 0 END) as potential_revenue
FROM licenses
GROUP BY tier;

CREATE VIEW payment_statistics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_payments,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_payments,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) as daily_revenue
FROM payments
GROUP BY DATE(created_at)
ORDER BY date DESC;
