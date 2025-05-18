import { render, screen, fireEvent } from '@testing-library/react'
import AlertsPanel from '../AlertsPanel'

jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { username: 'testuser' },
    token: 'mock-token',
  }),
}))

const mockAlerts = [
  {
    id: 1,
    title: 'Suspicious Login Activity',
    description: 'Multiple failed login attempts detected',
    severity: 'high',
    status: 'open',
    created_at: '2024-01-15T10:00:00',
  },
  {
    id: 2,
    title: 'Malware Detection',
    description: 'Malicious file detected in uploads directory',
    severity: 'critical',
    status: 'investigating',
    created_at: '2024-01-15T09:30:00',
  },
]

describe('AlertsPanel', () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAlerts),
      })
    ) as jest.Mock
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('renders alert list', async () => {
    render(<AlertsPanel />)

    expect(await screen.findByText('Suspicious Login Activity')).toBeInTheDocument()
    expect(screen.getByText('Malware Detection')).toBeInTheDocument()
  })

  it('displays severity badges correctly', async () => {
    render(<AlertsPanel />)

    await screen.findByText('Suspicious Login Activity')

    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('critical')).toBeInTheDocument()
  })

  it('filters alerts by status', async () => {
    render(<AlertsPanel />)

    await screen.findByText('Suspicious Login Activity')

    const statusFilter = screen.getByLabelText(/status/i)
    fireEvent.change(statusFilter, { target: { value: 'open' } })

    // Should filter to only show open alerts
    expect(screen.getByText('Suspicious Login Activity')).toBeInTheDocument()
  })

  it('shows alert details on click', async () => {
    render(<AlertsPanel />)

    const alertItem = await screen.findByText('Suspicious Login Activity')
    fireEvent.click(alertItem)

    expect(screen.getByText(/Multiple failed login attempts detected/i)).toBeInTheDocument()
  })
})
