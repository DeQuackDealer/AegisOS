// Aegis OS Rust SDK
use reqwest::{Client as HttpClient, header};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub mod models;
pub use models::*;

#[derive(Clone)]
pub struct Client {
    base_url: String,
    api_key: String,
    user_id: String,
    http_client: HttpClient,
}

impl Client {
    pub fn new(base_url: String, api_key: String, user_id: String) -> Self {
        Client {
            base_url,
            api_key,
            user_id,
            http_client: HttpClient::new(),
        }
    }

    async fn do_request<T: Serialize>(
        &self,
        method: &str,
        endpoint: &str,
        body: Option<T>,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let url = format!("{}{}", self.base_url, endpoint);
        
        let mut headers = header::HeaderMap::new();
        headers.insert("Content-Type", "application/json".parse()?);
        headers.insert("X-API-Key", self.api_key.parse()?);
        headers.insert("X-User-ID", self.user_id.parse()?);

        let response = match method {
            "POST" => {
                let body_json = serde_json::to_string(&body)?;
                self.http_client
                    .post(&url)
                    .headers(headers)
                    .body(body_json)
                    .send()
                    .await?
            }
            _ => self.http_client
                .get(&url)
                .headers(headers)
                .send()
                .await?,
        };

        Ok(response.text().await?)
    }

    pub async fn validate_license(&self, key: &str) -> Result<String, Box<dyn std::error::Error>> {
        #[derive(Serialize)]
        struct Request {
            key: String,
        }
        
        let body = Request {
            key: key.to_string(),
        };
        
        self.do_request("POST", "/api/v1/license/validate", Some(body))
            .await
    }

    pub async fn get_tiers(&self) -> Result<String, Box<dyn std::error::Error>> {
        self.do_request::<String>("GET", "/api/v1/tiers", None).await
    }

    pub async fn get_system_status(&self) -> Result<String, Box<dyn std::error::Error>> {
        self.do_request::<String>("GET", "/api/v1/system/status", None).await
    }

    pub async fn get_security_check(&self) -> Result<String, Box<dyn std::error::Error>> {
        self.do_request::<String>("GET", "/api/v1/security/check", None).await
    }
}
