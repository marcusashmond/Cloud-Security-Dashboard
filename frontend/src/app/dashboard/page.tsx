'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import Sidebar from '@/components/Sidebar'
import DashboardOverview from '@/components/dashboard/DashboardOverview'
import LogsTable from '@/components/dashboard/LogsTable'
import AlertsPanel from '@/components/dashboard/AlertsPanel'
import AnalyticsCharts from '@/components/dashboard/AnalyticsCharts'

export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview')
  // const [autoRefresh, setAutoRefresh] = useState(false)  // was experimenting with this

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-7xl mx-auto">
          {activeTab === 'overview' && <DashboardOverview />}
          {activeTab === 'logs' && <LogsTable />}
          {activeTab === 'alerts' && <AlertsPanel />}
          {activeTab === 'analytics' && <AnalyticsCharts />}
        </div>
      </main>
    </div>
  )
}
