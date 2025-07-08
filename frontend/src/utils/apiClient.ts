/**
 * API Client Utility
 * 
 * A reusable utility for making API calls with authentication and error handling.
 * 
 * Features:
 * - Support for GET, POST, PUT, DELETE methods
 * - Automatic CSRF token handling for Django
 * - JSON request/response handling
 * - Error handling with customizable error messages
 * - Authentication via API key or token
 */

interface ApiClientOptions {
    baseUrl?: string;
    headers?: Record<string, string>;
    onError?: (error: Error) => void;
    useCsrf?: boolean;
}

interface RequestOptions {
    data?: any;
    params?: Record<string, any>;
    headers?: Record<string, string>;
    includeAuth?: boolean;
}

export class ApiClient {
    private baseUrl: string;
    private headers: Record<string, string>;
    private onError?: (error: Error, context?: { method: string; endpoint: string; context?: string }) => void;
    private useCsrf: boolean;
    private csrfToken?: string;
    /**
     * Create a new ApiClient instance
     * @param options - Configuration options
     */
    constructor({
        baseUrl = '',
        headers = {},
        onError,
        useCsrf = true
    }: ApiClientOptions = {}) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            ...headers
        };
        if (onError) this.onError = onError;
        this.useCsrf = useCsrf;
        
        // Get CSRF token from cookies if available
        if (this.useCsrf) {
            this.csrfToken = this._getCsrfToken();
        }
    }

    /**
     * Get CSRF token from cookies
     * @private
     * @returns CSRF token or null if not found
     */
    private _getCsrfToken(): string | undefined {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    private async _request(
        method: string, 
        endpoint: string, 
        {
            data = null,
            params = {},
            headers = {},
            includeAuth = true
        }: RequestOptions = {}
    ): Promise<any> {
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
        const config: RequestInit = {
            method,
            headers: requestHeaders,
            credentials: 'same-origin' as const // Include cookies for CSRF
        };

        // Add request body for methods that support it
        if (data && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
            // If data is FormData, use it directly
            if (data instanceof FormData) {
                config.body = data as BodyInit;
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
        } catch (error: unknown) {
            console.error('API request failed:', error);
            if (this.onError) {
                const errorMessage = error instanceof Error ? error : new Error('An unknown error occurred');
                this.onError(errorMessage, { method, endpoint });
            }
            if (error instanceof Error) {
                throw error;
            }
            throw new Error('An unknown error occurred');
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
    async get(endpoint: string, params: Record<string, any> = {}, options: Omit<RequestOptions, 'data'> = {}) {
        return this._request('GET', endpoint, { ...options, params });
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async post(endpoint: string, data: any = {}, options: Omit<RequestOptions, 'data' | 'params'> = {}) {
        return this._request('POST', endpoint, { ...options, data });
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async put(endpoint: string, data: any = {}, options: Omit<RequestOptions, 'data' | 'params'> = {}) {
        return this._request('PUT', endpoint, { ...options, data });
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async delete(endpoint: string, options: Omit<RequestOptions, 'data'> = {}) {
        return this._request('DELETE', endpoint, options);
    }

    /**
     * Make a PATCH request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async patch(endpoint: string, data: any = {}, options: Omit<RequestOptions, 'data' | 'params'> = {}) {
        return this._request('PATCH', endpoint, { ...options, data });
    }

    /**
     * Fetch credits for a given API key from the billing endpoint
     * @param {string} apiKey - The API key to fetch credits for
     * @returns {Promise<Object>} Response data containing credit information
     */
    async fetchCredits(apiKey: string): Promise<any> {
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
    async transcribeAudio(file: File, apiKey: string, model = "gpt-4o-mini-transcribe", language = "en", options: Record<string, any> = {}): Promise<any> {
        // Create FormData and append file content and options
        const formData = new FormData();
        formData.append("file", file); 
        formData.append("model", model);
        formData.append("language", language);

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
                throw new Error(data.message || 'Failed to transcribe audio');
            }
            return data;
        } catch (error) {
            if (this.onError) {
                this.onError(error as Error, {
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
    async chatCompletion(
        apiKey: string, 
        model: string, 
        messages: Array<{role: string, content: string}>, 
        options: Record<string, any> = {},
        endpoint: string = '/v1/chat/completions'
    ): Promise<any> {
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
            return await this._request('POST', endpoint, {
                data: {
                    model,
                    messages,
                    ...otherOptions
                },
                headers,
                includeAuth: false  // We're handling auth in the headers
            });
        } catch (error: unknown) {
            console.error('Error in chat completion:', error);
            if (this.onError) {
                const errorMessage = error instanceof Error ? error : new Error('An unknown error occurred during chat completion');
                this.onError(errorMessage, {
                    method: 'POST',
                    endpoint: '/v1/chat/completions',
                    context: 'Chat completion request'
                });
            }
            if (error instanceof Error) {
                throw error;
            }
            throw new Error('An unknown error occurred during chat completion');
        }
    }
}

// Attach to window for global access
declare global {
    interface Window {
        ApiClient: typeof ApiClient;
    }
}

// window.ApiClient = ApiClient;

