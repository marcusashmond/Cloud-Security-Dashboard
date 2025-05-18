'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { Alert } from '@/types'
import { FaBell, FaCheckCircle } from 'react-icons/fa'

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('open')

  useEffect(() => {
    fetchAlerts()
  }, [filter])

  const fetchAlerts = async () => {
    try {
      const params = filter !== 'all' ? `?status=${filter}` : ''
      const response = await apiClient.get(`/alerts${params}`)
      setAlerts(response.data)
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateAlertStatus = async (alertId: number, status: string) => {
    try {
      await apiClient.put(`/alerts/${alertId}`, { status })
      fetchAlerts()
    } catch (error) {
      console.error('Failed to update alert:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Security Alerts</h1>
          <p className="text-gray-400 mt-1">Manage and respond to security incidents</p>
        </div>
        <div className="flex items-center space-x-2">
          {['all', 'open', 'investigating', 'resolved'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8 text-gray-400">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700 text-center">
            <FaBell className="text-gray-600 text-4xl mx-auto mb-4" />
            <p className="text-gray-400">No alerts found</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        alert.severity === 'critical'
                          ? 'bg-red-500/20 text-red-400'
                          : alert.severity === 'high'
                          ? 'bg-orange-500/20 text-orange-400'
                          : alert.severity === 'medium'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-green-500/20 text-green-400'
                      }`}
                    >
                      {alert.severity.toUpperCase()}
                    </span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        alert.status === 'open'
                          ? 'bg-blue-500/20 text-blue-400'
                          : alert.status === 'investigating'
                          ? 'bg-purple-500/20 text-purple-400'
                          : 'bg-green-500/20 text-green-400'
                      }`}
                    >
                      {alert.status.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {alert.title}
                  </h3>
                  <p className="text-gray-400 mb-4">{alert.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Alert ID: #{alert.id}</span>
                    <span>•</span>
                    <span>Created: {new Date(alert.created_at).toLocaleString()}</span>
                    <span>•</span>
                    <span>Updated: {new Date(alert.updated_at).toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex flex-col space-y-2 ml-4">
                  {alert.status === 'open' && (
                    <button
                      onClick={() => updateAlertStatus(alert.id, 'investigating')}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
                    >
                      Investigate
                    </button>
                  )}
                  {alert.status !== 'resolved' && (
                    <button
                      onClick={() => updateAlertStatus(alert.id, 'resolved')}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors flex items-center space-x-2"
                    >
                      <FaCheckCircle />
                      <span>Resolve</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
