/**
 * ForgeAI API client.
 *
 * All requests go through the Vercel rewrite proxy (/api/* → HF Space),
 * so cookies are first-party and credentials are sent automatically.
 */

const API_URL = ''

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

export async function apiPost<T>(endpoint: string, data: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'GET',
  })
}

export async function apiUpload<T>(
  endpoint: string,
  formData: FormData,
  timeout: number = 300000
): Promise<T> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      credentials: 'include',
      headers: {},
      body: formData,
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
      throw new Error(error.detail || 'Upload failed')
    }

    return response.json()
  } catch (error: any) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('Upload timed out. The file may be too large or processing is taking too long.')
    }
    throw error
  }
}
