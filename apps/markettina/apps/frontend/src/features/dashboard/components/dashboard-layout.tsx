import { ReactNode } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Settings,
  CreditCard,
  LogOut,
  Menu,
  Bell,
  Search,
  User,
  MessageSquare,
  Briefcase,
  Calendar
} from 'lucide-react'
import { Button } from '../../../shared/components/ui/button'
import { Input } from '../../../shared/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '../../../shared/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../../../shared/components/ui/dropdown-menu'
import { useAuthStore } from '../../../shared/hooks/use-auth-store'
import { ROUTES, cn } from '../../../shared/lib/utils'

// Helper function to get initials from name
function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .filter(Boolean)
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'U';
}

interface DashboardLayoutProps {
  children?: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { name: 'Portfolio', href: '/dashboard/portfolio', icon: Briefcase },
  { name: 'Prenotazioni', href: '/dashboard/bookings', icon: Calendar },
  { name: 'Utenti', href: '/dashboard/users', icon: Users },
  { name: 'Supporto', href: '/dashboard/support', icon: MessageSquare },
  { name: 'Impostazioni', href: ROUTES.SETTINGS, icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0A0A0A]">
      {/* Mobile menu button */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-xl font-semibold">MARKETTINA</h1>
          <Button variant="ghost" size="sm">
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
          <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 px-6 pb-4">
            <div className="flex h-16 shrink-0 items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                🚀 MARKETTINA
              </h1>
            </div>
            <nav className="flex flex-1 flex-col">
              <ul role="list" className="flex flex-1 flex-col gap-y-7">
                <li>
                  <ul role="list" className="-mx-2 space-y-1">
                    {navigation.map((item) => {
                      const isActive = location.pathname === item.href
                      return (
                        <li key={item.name}>
                          <Link
                            to={item.href}
                            className={cn(
                              isActive
                                ? 'bg-gray-50 text-gold dark:bg-gray-700 dark:text-gold'
                                : 'text-gray-700 hover:text-gold hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gold',
                              'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors'
                            )}
                          >
                            <item.icon
                              className={cn(
                                isActive
                                  ? 'text-gold dark:text-gold'
                                  : 'text-gray-400 group-hover:text-gold dark:group-hover:text-gold',
                                'h-6 w-6 shrink-0'
                              )}
                            />
                            {item.name}
                          </Link>
                        </li>
                      )
                    })}
                  </ul>
                </li>
              </ul>
            </nav>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:pl-64 flex flex-col flex-1">
          {/* Top header */}
          <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
              <div className="relative flex flex-1">
                <Search className="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400 pl-3" />
                <Input
                  placeholder="Cerca..."
                  className="pl-10 border-0 bg-transparent focus:ring-0"
                />
              </div>
              <div className="flex items-center gap-x-4">
                {/* Notifications */}
                <Button variant="ghost" size="sm">
                  <Bell className="h-5 w-5" />
                </Button>

                {/* User menu */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="" alt={user?.username || ''} />
                        <AvatarFallback>
                          {user ? getInitials(`${user.first_name || ''} ${user.last_name || user.username}`) : 'U'}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-56" align="end" forceMount>
                    <DropdownMenuLabel>
                      <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium">
                          {user ? `${user.first_name || ''} ${user.last_name || user.username}`.trim() : 'Utente'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {user?.email}
                        </p>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link to={ROUTES.PROFILE} className="cursor-pointer">
                        <User className="mr-2 h-4 w-4" />
                        Profilo
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to={ROUTES.SETTINGS} className="cursor-pointer">
                        <Settings className="mr-2 h-4 w-4" />
                        Impostazioni
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                      <LogOut className="mr-2 h-4 w-4" />
                      Esci
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </div>

          {/* Page content */}
          <main className="flex-1 py-6">
            <div className="px-4 sm:px-6 lg:px-8">
              {children || <Outlet />}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
