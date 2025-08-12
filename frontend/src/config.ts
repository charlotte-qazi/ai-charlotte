/*
 * AI Charlotte - Frontend Configuration
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

// Get the API base URL from environment variables
const getApiBaseUrl = (): string => {
  // In production, use the Railway backend URL
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_URL
  }
  
  // In development, use relative path (proxied by Vite)
  return ''
}

export const config = {
  apiBaseUrl: getApiBaseUrl(),
  isProduction: import.meta.env.PROD,
  isDevelopment: import.meta.env.DEV,
} as const

export default config 