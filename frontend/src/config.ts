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
  console.log('🔍 Environment check:')
  console.log('  - PROD:', import.meta.env.PROD)
  console.log('  - DEV:', import.meta.env.DEV)
  console.log('  - VITE_API_URL:', import.meta.env.VITE_API_URL)
  console.log('  - All env vars:', import.meta.env)
  
  // In production, use the Railway backend URL
  if (import.meta.env.PROD) {
    const envApiUrl = import.meta.env.VITE_API_URL
    const fallbackUrl = 'https://ai-charlotte-production.up.railway.app'
    
    // Handle cases where env var might be empty string or undefined
    let apiUrl = (envApiUrl && envApiUrl.trim() !== '') ? envApiUrl.trim() : fallbackUrl
    
    // Ensure URL starts with https:// to prevent relative path issues
    if (apiUrl && !apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
      apiUrl = `https://${apiUrl}`
    }
    
    console.log('🚀 Production mode - Final API URL:', apiUrl)
    return apiUrl
  }
  
  // In development, use relative path (proxied by Vite)
  console.log('🔧 Development mode - using proxy')
  return ''
}

export const config = {
  apiBaseUrl: getApiBaseUrl(),
  isProduction: import.meta.env.PROD,
  isDevelopment: import.meta.env.DEV,
} as const

export default config 