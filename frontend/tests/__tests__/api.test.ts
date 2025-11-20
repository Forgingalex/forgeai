/**
 * Tests for API utility functions
 */
import { apiGet, apiPost, apiUpload } from '@/lib/api'

// Mock fetch
global.fetch = jest.fn()

describe('API utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('apiGet', () => {
    it('should make GET request with token', async () => {
      localStorage.setItem('token', 'test-token')
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' }),
      })

      const result = await apiGet('/test')

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      )
      expect(result).toEqual({ data: 'test' })
    })

    it('should handle errors', async () => {
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Error' }),
      })

      await expect(apiGet('/test')).rejects.toThrow('Error')
    })
  })

  describe('apiPost', () => {
    it('should make POST request with data', async () => {
      localStorage.setItem('token', 'test-token')
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      const result = await apiPost('/test', { key: 'value' })

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ key: 'value' }),
        })
      )
      expect(result).toEqual({ success: true })
    })
  })

  describe('apiUpload', () => {
    it('should upload file with FormData', async () => {
      localStorage.setItem('token', 'test-token')
      const formData = new FormData()
      formData.append('file', new Blob(['test']), 'test.pdf')

      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1 }),
      })

      const result = await apiUpload('/upload', formData)

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/upload'),
        expect.objectContaining({
          method: 'POST',
          body: formData,
        })
      )
      expect(result).toEqual({ id: 1 })
    })
  })
})

