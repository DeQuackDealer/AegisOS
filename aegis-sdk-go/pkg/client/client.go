// Package client provides the Aegis OS API client
package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// Client is the Aegis OS API client
type Client struct {
	BaseURL string
	APIKey  string
	UserID  string
	client  *http.Client
}

// NewClient creates a new Aegis OS API client
func NewClient(baseURL, apiKey, userID string) *Client {
	return &Client{
		BaseURL: baseURL,
		APIKey:  apiKey,
		UserID:  userID,
		client:  &http.Client{},
	}
}

// doRequest performs an HTTP request
func (c *Client) doRequest(method, endpoint string, body interface{}) ([]byte, error) {
	url := fmt.Sprintf("%s%s", c.BaseURL, endpoint)
	
	var reqBody io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		reqBody = bytes.NewBuffer(jsonBody)
	}
	
	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", c.APIKey)
	req.Header.Set("X-User-ID", c.UserID)
	
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	return io.ReadAll(resp.Body)
}

// ValidateLicense validates a license key
func (c *Client) ValidateLicense(key string) (map[string]interface{}, error) {
	body := map[string]string{"key": key}
	resp, err := c.doRequest("POST", "/api/v1/license/validate", body)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, err
	}
	
	return result, nil
}

// GetTiers gets all available tiers
func (c *Client) GetTiers() (map[string]interface{}, error) {
	resp, err := c.doRequest("GET", "/api/v1/tiers", nil)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, err
	}
	
	return result, nil
}

// GetSystemStatus gets system status
func (c *Client) GetSystemStatus() (map[string]interface{}, error) {
	resp, err := c.doRequest("GET", "/api/v1/system/status", nil)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, err
	}
	
	return result, nil
}

// GetSecurityCheck gets security status
func (c *Client) GetSecurityCheck() (map[string]interface{}, error) {
	resp, err := c.doRequest("GET", "/api/v1/security/check", nil)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, err
	}
	
	return result, nil
}
