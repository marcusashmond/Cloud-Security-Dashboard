'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { SecurityLog } from '@/types'
import { FaDownload, FaFilter } from 'react-icons/fa'

export default function LogsTable() {
  const [logs, setLogs] = useState<SecurityLog[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    severity: '',
    is_threat: '',
  })
  const [temp, setTemp] = useState(null)
  // const [debugMode, setDebugMode] = useState(false)  // might need later

  useEffect(() => {
    fetchLogs()
    // Auto-refresh might be annoying but helpful for monitoring
  }, [filters])

  const fetchLogs = async () => {
    try {
      // console.log('[DEBUG] Fetching logs with filters:', filters)  // useful for debugging
      const params = new URLSearchParams()
      if (filters.severity) params.append('severity', filters.severity)
      if (filters.is_threat) params.append('is_threat', filters.is_threat)
      
      const resp = await apiClient.get(`/logs?${params.toString()}`)
      setLogs(resp.data.logs)
    } catch (err) {
      console.error('Failed to fetch logs:', err)
    } finally {
      setLoading(false)
    }
  }

  const exportToCSV = async () => {
    try {
      const res = await apiClient.get('/logs/export/csv', {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'security_logs.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (e) {
      console.error('Failed to export logs:', e)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Security Logs</h1>
          <p className="text-gray-400 mt-1">View and analyze security events</p>
        </div>
        <button
          onClick={exportToCSV}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <FaDownload />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex items-center space-x-4">
          <FaFilter className="text-gray-400" />
          <select
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <select
            value={filters.is_threat}
            onChange={(e) => setFilters({ ...filters, is_threat: e.target.value })}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Events</option>
            <option value="true">Threats Only</option>
            <option value="false">Safe Events</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr className="text-left text-gray-300">
                <th className="px-6 py-4 font-semibold">Timestamp</th>
                <th className="px-6 py-4 font-semibold">Event Type</th>
                <th className="px-6 py-4 font-semibold">Severity</th>
                <th className="px-6 py-4 font-semibold">Source IP</th>
                <th className="px-6 py-4 font-semibold">Username</th>
                <th className="px-6 py-4 font-semibold">Threat Score</th>
                <th className="px-6 py-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-400">
                    Loading logs...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-400">
                    No logs found
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    className="border-t border-gray-700 hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-6 py-4 text-gray-300 text-sm">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-gray-300">
                      <span className="font-mono text-sm">
                        {log.event_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
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
                    <td className="px-6 py-4 text-gray-300 font-mono text-sm">
                      {log.source_ip || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-gray-300">{log.username || 'N/A'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              log.threat_score > 0.7
                                ? 'bg-red-500'
                                : log.threat_score > 0.4
                                ? 'bg-yellow-500'
                                : 'bg-green-500'
                            }`}
                            style={{ width: `${log.threat_score * 100}%` }}
                          />
                        </div>
                        <span className="text-gray-300 text-sm">
                          {(log.threat_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {log.is_threat ? (
                        <span className="flex items-center space-x-1 text-red-400 font-semibold">
                          <span>⚠️</span>
                          <span>Threat</span>
                        </span>
                      ) : (
                        <span className="flex items-center space-x-1 text-green-400">
                          <span>✓</span>
                          <span>Safe</span>
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
