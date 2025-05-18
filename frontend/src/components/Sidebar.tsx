'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { 
  FaHome, 
  FaList, 
  FaExclamationTriangle, 
  FaChartBar, 
  FaSignOutAlt,
  FaShieldAlt 
} from 'react-icons/fa'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: FaHome },
    { id: 'logs', label: 'Security Logs', icon: FaList },
    { id: 'alerts', label: 'Alerts', icon: FaExclamationTriangle },
    { id: 'analytics', label: 'Analytics', icon: FaChartBar },
  ]

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gray-800 text-white shadow-xl">
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <FaShieldAlt className="text-2xl" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Security Hub</h1>
            <p className="text-xs text-gray-400">Cloud Dashboard</p>
          </div>
        </div>
      </div>

      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Icon className="text-xl" />
              <span className="font-medium">{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
        <div className="mb-4 p-3 bg-gray-700 rounded-lg">
          <p className="text-sm font-medium">{user?.username}</p>
          <p className="text-xs text-gray-400">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-4 py-3 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors"
        >
          <FaSignOutAlt />
          <span>Logout</span>
        </button>
      </div>
    </div>
  )
}
