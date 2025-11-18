const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token')
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
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
  formData: FormData
): Promise<T> {
  const token = localStorage.getItem('token')
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || 'Upload failed')
  }

  return response.json()
}

