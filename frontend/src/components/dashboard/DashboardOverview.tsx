'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { DashboardStats } from '@/types'
import { FaExclamationTriangle, FaShieldAlt, FaFileAlt, FaBell } from 'react-icons/fa'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function DashboardOverview() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await apiClient.get('/analytics/dashboard')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-white">Loading dashboard...</div>
  }

  if (!stats) {
    return <div className="text-white">No data available</div>
  }

  const statCards = [
    {
      title: 'Total Logs',
      value: stats.total_logs,
      icon: FaFileAlt,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Alerts',
      value: stats.total_alerts,
      icon: FaBell,
      color: 'bg-yellow-500',
    },
    {
      title: 'Critical Alerts',
      value: stats.critical_alerts,
      icon: FaExclamationTriangle,
      color: 'bg-red-500',
    },
    {
      title: 'Threats Detected',
      value: stats.threats_detected,
      icon: FaShieldAlt,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h1>
        <p className="text-gray-400">Real-time security monitoring and threat detection</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.title}
              className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="text-white text-2xl" />
                </div>
                <span className="text-3xl font-bold text-white">{card.value}</span>
              </div>
              <h3 className="text-gray-400 text-sm font-medium">{card.title}</h3>
            </div>
          )
        })}
      </div>

      {/* Recent Logs */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">Recent Security Logs</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-3">Time</th>
                <th className="pb-3">Event Type</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Source IP</th>
                <th className="pb-3">Threat</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_logs.slice(0, 5).map((log) => (
                <tr key={log.id} className="border-b border-gray-700 text-gray-300">
                  <td className="py-3 text-sm">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3">{log.event_type.replace(/_/g, ' ')}</td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${
                        log.severity === 'critical'
                          ? 'bg-red-500/20 text-red-400'
                          : log.severity === 'high'
                          ? 'bg-orange-500/20 text-orange-400'
                          : log.severity === 'medium'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-green-500/20 text-green-400'
                      }`}
                    >
                      {log.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 font-mono text-sm">{log.source_ip || 'N/A'}</td>
                  <td className="py-3">
                    {log.is_threat ? (
                      <span className="text-red-400 font-semibold">⚠️ THREAT</span>
                    ) : (
                      <span className="text-green-400">✓ Safe</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">Recent Alerts</h2>
        <div className="space-y-3">
          {stats.recent_alerts.slice(0, 5).map((alert) => (
            <div
              key={alert.id}
              className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">{alert.title}</h3>
                  <p className="text-sm text-gray-400">{alert.description}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <span
                    className={`px-3 py-1 rounded text-xs font-semibold ${
                      alert.severity === 'critical'
                        ? 'bg-red-500/20 text-red-400'
                        : alert.severity === 'high'
                        ? 'bg-orange-500/20 text-orange-400'
                        : 'bg-yellow-500/20 text-yellow-400'
                    }`}
                  >
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="px-3 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                    {alert.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
