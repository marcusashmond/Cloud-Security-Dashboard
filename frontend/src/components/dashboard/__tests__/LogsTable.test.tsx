import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LogsTable from '../LogsTable'

// Mock the auth context
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { username: 'testuser' },
    isAuthenticated: true,
    token: 'mock-token',
  }),
}))

const mockLogs = [
  {
    id: 1,
    timestamp: '2024-01-15T10:30:00',
    event_type: 'failed_login',
    severity: 'medium',
    source_ip: '192.168.1.100',
    username: 'testuser',
    description: 'Failed login attempt',
    is_threat: false,
    confidence_score: 0.3,
  },
  {
    id: 2,
    timestamp: '2024-01-15T10:35:00',
    event_type: 'malware_detected',
    severity: 'critical',
    source_ip: '203.0.113.50',
    username: 'admin',
    description: 'Malware signature detected',
    is_threat: true,
    confidence_score: 0.95,
  },
]

describe('LogsTable', () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockLogs),
      })
    ) as jest.Mock
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('renders table headers', async () => {
    render(<LogsTable />)

    expect(await screen.findByText('Time')).toBeInTheDocument()
    expect(screen.getByText('Event Type')).toBeInTheDocument()
    expect(screen.getByText('Severity')).toBeInTheDocument()
    expect(screen.getByText('Source IP')).toBeInTheDocument()
    expect(screen.getByText('User')).toBeInTheDocument()
  })

  it('displays log data', async () => {
    render(<LogsTable />)

    expect(await screen.findByText('failed_login')).toBeInTheDocument()
    expect(screen.getByText('malware_detected')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.100')).toBeInTheDocument()
    expect(screen.getByText('203.0.113.50')).toBeInTheDocument()
  })

  it('filters logs by severity', async () => {
    render(<LogsTable />)

    // Wait for logs to load
    await screen.findByText('failed_login')

    // Find and click the severity filter
    const severityFilter = screen.getByLabelText(/severity/i)
    fireEvent.change(severityFilter, { target: { value: 'critical' } })

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('severity=critical'),
        expect.any(Object)
      )
    })
  })

  it('shows threat indicator for malicious logs', async () => {
    render(<LogsTable />)

    await screen.findByText('malware_detected')

    // Check for high confidence indicator
    const confidenceText = screen.getByText(/95%/i)
    expect(confidenceText).toBeInTheDocument()
  })

  it('handles empty logs list', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    })

    render(<LogsTable />)

    expect(await screen.findByText(/no logs found/i)).toBeInTheDocument()
  })
})
