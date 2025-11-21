// Data models
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct License {
    pub tier: String,
    pub price: u32,
    pub features: Vec<String>,
    pub expires: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct User {
    pub user_id: String,
    pub email: String,
    pub role: String,
    pub created: String,
    pub two_fa_enabled: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Webhook {
    pub webhook_id: String,
    pub url: String,
    pub events: Vec<String>,
    pub created: String,
    pub active: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemStatus {
    pub status: String,
    pub uptime_hours: u64,
    pub version: String,
    pub editions: Vec<String>,
}
