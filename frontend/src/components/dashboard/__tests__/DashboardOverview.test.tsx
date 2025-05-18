import { render, screen } from '@testing-library/react'
import DashboardOverview from '../DashboardOverview'

// Mock the auth context
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { username: 'testuser' },
    isAuthenticated: true,
  }),
}))

// Mock fetch
global.fetch = jest.fn()

describe('DashboardOverview', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading state initially', () => {
    render(<DashboardOverview />)
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('displays stats after loading', async () => {
    const mockStats = {
      total_logs: 1500,
      total_alerts: 25,
      critical_alerts: 5,
      threats_detected: 12,
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockStats,
    })

    render(<DashboardOverview />)

    // Wait for stats to load
    expect(await screen.findByText('1,500')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  it('displays stat card titles', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        total_logs: 0,
        total_alerts: 0,
        critical_alerts: 0,
        threats_detected: 0,
      }),
    })

    render(<DashboardOverview />)

    expect(await screen.findByText('Total Logs')).toBeInTheDocument()
    expect(screen.getByText('Active Alerts')).toBeInTheDocument()
    expect(screen.getByText('Critical Alerts')).toBeInTheDocument()
    expect(screen.getByText('Threats Detected')).toBeInTheDocument()
  })

  it('handles API error gracefully', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'))

    render(<DashboardOverview />)

    // Should still render the component structure
    expect(screen.getByText(/dashboard overview/i)).toBeInTheDocument()
  })
})
