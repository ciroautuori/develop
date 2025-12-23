import { cn } from "@/utils/cn"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  LayoutDashboard,
  Users,
  FileText,
  Calendar,
  Heart,
  Building,
  Settings,
  BarChart3,
  Shield,
  Database,
  Mail,
  Bell,
  LogOut,
  X,
  Home
} from "lucide-react"
import { Link, useLocation } from "@tanstack/react-router"

interface SidebarProps {
  userRole: 'admin' | 'user' | 'partner' | 'moderator'
  className?: string
  onClose?: () => void
}

export function DashboardSidebar({ userRole, className, onClose }: SidebarProps) {
  const location = useLocation()

  const adminMenuItems = [
    {
      title: "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard/admin",
      badge: null
    },
    {
      title: "Utenti",
      icon: Users,
      href: "/dashboard/admin/users",
      badge: null
    },
    {
      title: "Bandi",
      icon: FileText,
      href: "/dashboard/admin/bandi",
      badge: "74"
    },
    {
      title: "Eventi",
      icon: Calendar,
      href: "/dashboard/admin/events",
      badge: null
    },
    {
      title: "Volontariato",
      icon: Heart,
      href: "/dashboard/admin/volunteer",
      badge: null
    },
    {
      title: "Partner",
      icon: Building,
      href: "/dashboard/admin/partners",
      badge: null
    },
    {
      title: "Analytics",
      icon: BarChart3,
      href: "/dashboard/admin/analytics",
      badge: null
    },
    {
      title: "Sistema",
      icon: Database,
      href: "/dashboard/admin/system",
      badge: null
    },
    {
      title: "Sicurezza",
      icon: Shield,
      href: "/dashboard/admin/security",
      badge: null
    },
    {
      title: "Notifiche",
      icon: Bell,
      href: "/dashboard/admin/notifications",
      badge: null
    },
    {
      title: "Impostazioni",
      icon: Settings,
      href: "/dashboard/admin/settings",
      badge: null
    }
  ]

  const userMenuItems = [
    {
      title: "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard/user",
      badge: null
    },
    {
      title: "I Miei Corsi",
      icon: FileText,
      href: "/dashboard/user/courses",
      badge: null
    },
    {
      title: "Eventi",
      icon: Calendar,
      href: "/dashboard/user/events",
      badge: null
    },
    {
      title: "Volontariato",
      icon: Heart,
      href: "/dashboard/user/volunteer",
      badge: null
    },
    {
      title: "Messaggi",
      icon: Mail,
      href: "/dashboard/user/messages",
      badge: null
    },
    {
      title: "Profilo",
      icon: Users,
      href: "/dashboard/user/profile",
      badge: null
    },
    {
      title: "Impostazioni",
      icon: Settings,
      href: "/dashboard/user/settings",
      badge: null
    }
  ]

  const partnerMenuItems = [
    {
      title: "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard/partner",
      badge: null
    },
    {
      title: "Progetti",
      icon: FileText,
      href: "/dashboard/partner/projects",
      badge: null
    },
    {
      title: "Team",
      icon: Users,
      href: "/dashboard/partner/team",
      badge: null
    },
    {
      title: "Collaborazioni",
      icon: Building,
      href: "/dashboard/partner/collaborations",
      badge: null
    },
    {
      title: "Analytics",
      icon: BarChart3,
      href: "/dashboard/partner/analytics",
      badge: null
    },
    {
      title: "Documenti",
      icon: FileText,
      href: "/dashboard/partner/documents",
      badge: null
    },
    {
      title: "Messaggi",
      icon: Mail,
      href: "/dashboard/partner/messages",
      badge: null
    },
    {
      title: "Impostazioni",
      icon: Settings,
      href: "/dashboard/partner/settings",
      badge: null
    }
  ]

  const getMenuItems = () => {
    switch (userRole) {
      case 'admin':
        return adminMenuItems
      case 'user':
        return userMenuItems
      case 'partner':
        return partnerMenuItems
      default:
        return userMenuItems
    }
  }

  const getRoleInfo = () => {
    switch (userRole) {
      case 'admin':
        return { color: 'bg-red-500', label: 'Admin', icon: Shield }
      case 'user':
        return { color: 'bg-green-500', label: 'Utente', icon: Users }
      case 'partner':
        return { color: 'bg-purple-500', label: 'Partner', icon: Building }
      default:
        return { color: 'bg-blue-500', label: 'Utente', icon: Users }
    }
  }

  const menuItems = getMenuItems()
  const roleInfo = getRoleInfo()
  const RoleIcon = roleInfo.icon

  return (
    <div className={cn(
      "flex flex-col h-full bg-white border-r w-64",
      className
    )}>
      {/* Header */}
      <div className="flex h-14 sm:h-16 items-center justify-between px-4 border-b">
        <div className="flex items-center gap-3">
          <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center text-white", roleInfo.color)}>
            <RoleIcon className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold">{roleInfo.label}</p>
            <p className="text-xs text-gray-500">Dashboard</p>
          </div>
        </div>
        {/* Close button - only on mobile */}
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="lg:hidden h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Navigation */}
      <div className="flex-1 px-3 py-4 overflow-y-auto">
        <nav className="space-y-1">
          {/* Home Link */}
          <Link
            to="/"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
            onClick={onClose}
          >
            <Home className="h-4 w-4" />
            <span>Torna al Sito</span>
          </Link>

          <div className="pt-2 pb-1">
            <p className="px-3 text-xs font-medium text-gray-400 uppercase tracking-wider">Menu</p>
          </div>

          {menuItems.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.href}
                to={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                  "hover:bg-gray-100",
                  isActive
                    ? "bg-iss-bordeaux-50 text-iss-bordeaux-900 font-medium"
                    : "text-gray-600"
                )}
              >
                <item.icon className={cn("h-4 w-4", isActive && "text-iss-bordeaux-600")} />
                <span className="flex-1">{item.title}</span>
                {item.badge && (
                  <Badge variant="secondary" className="h-5 text-xs bg-iss-gold-100 text-iss-gold-800">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Footer */}
      <div className="border-t p-3">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-sm text-red-600 hover:text-red-700 hover:bg-red-50"
          onClick={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('iss_token')
            localStorage.removeItem('iss_user')
            window.location.href = '/'
          }}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}
