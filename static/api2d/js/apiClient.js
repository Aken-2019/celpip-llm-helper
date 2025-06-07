/**
 * API Client Utility
 * 
 * A reusable utility for making API calls with authentication and error handling.
 * 
 * Features:
 * - Support for GET, POST, PUT, DELETE methods
 - Automatic CSRF token handling for Django
 - JSON request/response handling
 - Error handling with customizable error messages
 - Authentication via API key or token
 */

class ApiClient {
    /**
     * Create a new ApiClient instance
     * @param {Object} options - Configuration options
     * @param {string} options.baseUrl - Base URL for all API requests
     * @param {Object} options.headers - Default headers to include with every request
     * @param {Function} options.onError - Global error handler function
     * @param {boolean} options.useCsrf - Whether to include CSRF token in requests (default: true)
     */
    constructor({
        baseUrl = '',
        headers = {},
        onError = null,
        useCsrf = true
    } = {}) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            ...headers
        };
        this.onError = onError;
        this.useCsrf = useCsrf;
        
        // Get CSRF token from cookies if available
        if (this.useCsrf) {
            this.csrfToken = this._getCsrfToken();
        }
    }

    /**
     * Get CSRF token from cookies
     * @private
     * @returns {string|null} CSRF token or null if not found
     */
    _getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || null;
    }

    async _request(method, endpoint, {
        data = null,
        params = null,
        headers = {},
        includeAuth = true
    } = {}) {
        // Build URL with query parameters
        let url = `${this.baseUrl}${endpoint}`;
        if (params) {
            const queryString = new URLSearchParams(params).toString();
            url += `?${queryString}`;
        }

        // Prepare headers
        const requestHeaders = { ...this.headers, ...headers };
        
        // Add CSRF token if enabled and available
        if (this.useCsrf && this.csrfToken) {
            requestHeaders['X-CSRFToken'] = this.csrfToken;
        }

        // Prepare request config
        const config = {
            method,
            headers: requestHeaders,
            credentials: 'same-origin' // Include cookies for CSRF
        };

        // Add request body for methods that support it
        if (data && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
            // If data is FormData, use it directly
            if (data instanceof FormData) {
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        try {
            const response = await fetch(url, config);
            
            // Handle non-2xx responses
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Try to parse JSON response, fall back to text if not JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            if (this.onError) {
                this.onError(error, { method, endpoint });
            }
            throw error;
        }
    }

    // Convenience methods for common HTTP methods

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - URL parameters
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    get(endpoint, params = {}, options = {}) {
        return this._request('GET', endpoint, { ...options, params });
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    post(endpoint, data = {}, options = {}) {
        return this._request('POST', endpoint, { ...options, data });
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    put(endpoint, data = {}, options = {}) {
        return this._request('PUT', endpoint, { ...options, data });
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    delete(endpoint, options = {}) {
        return this._request('DELETE', endpoint, options);
    }

    /**
     * Make a PATCH request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    patch(endpoint, data = {}, options = {}) {
        return this._request('PATCH', endpoint, { ...options, data });
    }

    /**
     * Fetch credits for a given API key from the billing endpoint
     * @param {string} apiKey - The API key to fetch credits for
     * @returns {Promise<Object>} Response data containing credit information
     */
    async fetchCredits(apiKey) {
        try {
            const response = await this.get('/dashboard/billing/credit_grants', {}, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                }
            });
            return response;
        } catch (error) {
            console.error('Error fetching credits:', error);
            throw error;
        }
    }

    
    /**
     * Transcribe audio file using OpenAI's API
     * @param {File} file - The audio file to transcribe
     * @param {string} apiKey - API key for authentication
     * @param {string} [model="gpt-4o-mini-transcribe"] - The model to use for transcription
     * @param {string} [language="en"] - The language of the audio
     * @param {Object} [options={}] - Additional configuration options
     * @returns {Promise<Object>} Response data containing the transcription
     */
    async transcribeAudio(file, apiKey, model="gpt-4o-mini-transcribe", language="en", options = {}) {
        const defaultOptions = {
            model: model,
            language: language,
        };
        
        // Create FormData and append file content
        const formData = new FormData();
        formData.append("file", file); 
        formData.append("model", model);

        const headers = {
            'Authorization': `Bearer ${apiKey}`,
            // 'Content-Type': 'multipart/form-data'
        };

        try {
            // Use vanilla fetch for transcription request instead of _request method
            // This is necessary because FormData requires special handling:
            // 1. The browser must automatically set the Content-Type header with boundary
            // 2. The browser handles multipart/form-data formatting internally
            // 3. We don't want to override these automatic headers
            // The _request method was trying to set Content-Type manually which interfered with FormData's automatic handling
            const response = await fetch(`${this.baseUrl}/v1/audio/transcriptions`, {
                method: 'POST',
                body: formData,
                headers: headers,
            });
            
            // Parse response
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to transcribe audio');
            }
            return data;
        } catch (error) {
            if (this.onError) {
                this.onError(error, {
                    method: 'POST',
                    endpoint: '/v1/audio/transcriptions',
                    context: 'Transcribing audio file'
                });
            }
            throw error;
        }
    }

    /**
     * Call OpenAI's Chat Completions API
     * @param {string} apiKey - OpenAI API key
     * @param {string} model - Model to use (e.g., 'gpt-3.5-turbo')
     * @param {Array<Object>} messages - Array of message objects with 'role' and 'content' properties
     * @param {Object} [options={}] - Additional options for the API call
     * @returns {Promise<Object>} Response from the API
     */
    async chatCompletion(apiKey, model, messages, options = {}) {
        const {
            ...otherOptions
        } = options;

        try {
            // Prepare headers with authorization
            const headers = {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                ...this.headers
            };

            // Make the request using the instance's _request method
            return await this._request('POST', '/v1/chat/completions', {
                data: {
                    model,
                    messages,
                    ...otherOptions
                },
                headers,
                includeAuth: false  // We're handling auth in the headers
            });
        } catch (error) {
            console.error('Error in chat completion:', error);
            if (this.onError) {
                this.onError(error, {
                    method: 'POST',
                    endpoint: '/v1/chat/completions',
                    context: 'Chat completion request'
                });
            }
            throw error;
        }
    }
}

// Attach to window for global access
window.ApiClient = ApiClient;
