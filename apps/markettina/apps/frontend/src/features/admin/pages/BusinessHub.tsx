/**
 * Business Hub - Centro Operativo Aziendale
 * Unifica: Clienti (CRM) + Preventivi + Calendario Appuntamenti + Pipeline
 */

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  FileText,
  Calendar,
  TrendingUp,
  Plus,
  Search,
  Filter,
  Phone,
  Mail,
  Building2,
  MapPin,
  Euro,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Edit2,
  Trash2,
  Eye,
  Send,
  Download,
  ChevronLeft,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  MoreVertical,
  Video,
  X,
  Loader2,
  List,
  CalendarDays,
  Briefcase,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../../../shared/components/ui/dropdown-menu";
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { CustomerModal } from '../components/CustomerModal';
import { QuoteModal } from '../components/QuoteModal';
import { BookingModal } from '../components/BookingModal';
import { CalendarGrid } from '../components/CalendarGrid';
import { SPACING } from '../../../shared/config/constants';
import { useQuery } from '@tanstack/react-query';

// Types
interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  city?: string;
  status: 'active' | 'inactive' | 'lead';
  total_quotes: number;
  total_revenue: number;
  created_at: string;
  last_contact?: string;
}

interface Quote {
  id: number;
  number: string;
  customer_name: string;
  customer_id: number;
  total: number;
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired';
  created_at: string;
  valid_until: string;
  items_count: number;
}

interface Appointment {
  id: number;
  title: string;
  client_name: string;
  client_email: string;
  date: string;
  time: string;
  duration: number;
  type: 'call' | 'video' | 'meeting';
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
}

interface PipelineDeal {
  id: number;
  name: string;
  customer: string;
  value: number;
  stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: number;
  expected_close: string;
}

const QUOTE_STATUS = {
  draft: { label: 'Bozza', color: 'bg-gray-500', icon: FileText },
  sent: { label: 'Inviato', color: 'bg-blue-500', icon: Send },
  accepted: { label: 'Accettato', color: 'bg-green-500', icon: CheckCircle2 },
  rejected: { label: 'Rifiutato', color: 'bg-red-500', icon: XCircle },
  expired: { label: 'Scaduto', color: 'bg-yellow-500', icon: AlertCircle },
};

const APPOINTMENT_STATUS = {
  pending: { label: 'In attesa', color: 'bg-yellow-500' },
  confirmed: { label: 'Confermato', color: 'bg-green-500' },
  completed: { label: 'Completato', color: 'bg-blue-500' },
  cancelled: { label: 'Annullato', color: 'bg-red-500' },
};

const PIPELINE_STAGES = [
  { id: 'lead', label: 'Lead', color: 'bg-gray-500' },
  { id: 'qualified', label: 'Qualificato', color: 'bg-blue-500' },
  { id: 'proposal', label: 'Proposta', color: 'bg-purple-500' },
  { id: 'negotiation', label: 'Negoziazione', color: 'bg-yellow-500' },
  { id: 'closed_won', label: 'Chiuso Vinto', color: 'bg-green-500' },
  { id: 'closed_lost', label: 'Chiuso Perso', color: 'bg-red-500' },
];

export function BusinessHub() {
  const [activeTab, setActiveTab] = useState<'customers' | 'quotes' | 'appointments' | 'pipeline'>('customers');
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Theme classes - Design System #0A0A0A
  const cardBg = isDark
    ? 'bg-[#0A0A0A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';
  const tabBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200';

  // State
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [deals, setDeals] = useState<PipelineDeal[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Modal states
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showQuoteModal, setShowQuoteModal] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
  const [selectedBooking, setSelectedBooking] = useState<any>(null);
  const [modalMode, setModalMode] = useState<'create' | 'edit' | 'view'>('create');
  const [openAppointmentMenu, setOpenAppointmentMenu] = useState<number | null>(null);
  const [openCustomerMenu, setOpenCustomerMenu] = useState<number | null>(null);
  const [openQuoteMenu, setOpenQuoteMenu] = useState<number | null>(null);
  const [appointmentsView, setAppointmentsView] = useState<'list' | 'calendar'>('list');
  const [calendarDate, setCalendarDate] = useState(new Date());
  const [prefilledDate, setPrefilledDate] = useState<Date | undefined>(undefined);

  // Stats - calculated from real data
  const stats = {
    totalCustomers: customers.length,
    activeCustomers: customers.filter(c => c.status === 'active').length,
    totalQuotes: quotes.length,
    pendingQuotes: quotes.filter(q => q.status === 'sent').length,
    acceptedQuotes: quotes.filter(q => q.status === 'accepted').length,
    totalRevenue: quotes.filter(q => q.status === 'accepted').reduce((acc, q) => acc + q.total, 0),
    todayAppointments: appointments.filter(a => {
      const today = new Date().toISOString().split('T')[0];
      return a.date === today;
    }).length,
  };

  // Fetch calendar bookings
  const { data: calendarBookings, isLoading: calendarLoading } = useQuery({
    queryKey: ['calendar', calendarDate.getFullYear(), calendarDate.getMonth() + 1],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      if (!token) throw new Error('No authentication token');
      const res = await fetch(
        `/api/v1/admin/bookings/calendar/month?year=${calendarDate.getFullYear()}&month=${calendarDate.getMonth() + 1}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error(`Calendar API Error: ${res.status}`);
      return res.json();
    },
    enabled: appointmentsView === 'calendar',
  });

  // Fetch data
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (openAppointmentMenu !== null && !target.closest('.appointment-dropdown')) {
        setOpenAppointmentMenu(null);
      }
      if (openCustomerMenu !== null && !target.closest('.customer-dropdown')) {
        setOpenCustomerMenu(null);
      }
      if (openQuoteMenu !== null && !target.closest('.quote-dropdown')) {
        setOpenQuoteMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openAppointmentMenu, openCustomerMenu, openQuoteMenu]);

  // API REALI - NO MOCK! ✅
  // Tutte le chiamate API usano endpoint reali del backend:
  // - /api/v1/admin/customers (CRM customers con encrypted email/phone)
  // - /api/v1/admin/quotes (Sistema preventivi con line items e totali)
  // - /api/v1/admin/bookings (Sistema appuntamenti con Google Meet)
  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch customers from real CRM database
      const customersRes = await fetch('/api/v1/admin/customers?page=1&page_size=50', { headers });
      if (customersRes.ok) {
        const data = await customersRes.json();
        setCustomers(data.items || data || []);
      } else {
        console.error('Customers API error:', customersRes.status);
      }

      // Fetch quotes from real quotes database
      const quotesRes = await fetch('/api/v1/admin/quotes?page=1&page_size=50', { headers });
      if (quotesRes.ok) {
        const data = await quotesRes.json();
        setQuotes(data.items || data || []);
      } else {
        console.error('Quotes API error:', quotesRes.status);
      }

      // Fetch appointments from real bookings database
      const appointmentsRes = await fetch('/api/v1/admin/bookings?page=1&page_size=50', { headers });
      if (appointmentsRes.ok) {
        const data = await appointmentsRes.json();
        const bookings = data.items || data || [];
        // Map bookings to appointment format
        setAppointments(bookings.map((b: any) => ({
          id: b.id,
          title: b.title || `Consulenza ${b.service_type || ''}`,
          client_name: b.client_name,
          client_email: b.client_email,
          date: b.scheduled_at?.split('T')[0] || b.scheduled_at,
          time: b.scheduled_at?.split('T')[1]?.substring(0, 5) || '',
          duration: b.duration_minutes || 60,
          type: b.meeting_url ? 'video' : 'call',
          status: b.status,
          notes: b.notes
        })));
      } else {
        console.error('Bookings API error:', appointmentsRes.status);
      }

    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Errore nel caricamento dei dati. Verifica il token admin.');
    }
    setLoading(false);
  };

  // Quote actions
  const handleQuoteAction = async (quoteId: number, action: 'send' | 'accept' | 'reject') => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/quotes/${quoteId}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error(`Errore ${action}`);

      toast.success(
        action === 'send' ? 'Preventivo inviato!' :
          action === 'accept' ? 'Preventivo accettato!' :
            'Preventivo rifiutato!'
      );
      fetchData();
    } catch (error) {
      toast.error(`Errore durante l'operazione`);
    }
  };

  const handleDeleteQuote = async (quoteId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo preventivo?')) return;

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/quotes/${quoteId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Errore eliminazione');

      toast.success('Preventivo eliminato!');
      fetchData();
    } catch (error) {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  const handleConfirmAppointment = async (id: number) => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/bookings/${id}/confirm`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Errore nella conferma');

      setAppointments(appointments.map(apt =>
        apt.id === id ? { ...apt, status: 'confirmed' } : apt
      ));
      setOpenAppointmentMenu(null);
      toast.success('✅ Appuntamento confermato e notifica inviata al cliente!');
      fetchData();
    } catch (error) {
      toast.error('Errore durante la conferma dell\'appuntamento');
    }
  };

  const handleCancelAppointment = async (id: number) => {
    if (!confirm('Sei sicuro di voler cancellare questo appuntamento?')) return;

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/bookings/${id}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Errore nella cancellazione');

      setAppointments(appointments.map(apt =>
        apt.id === id ? { ...apt, status: 'cancelled' } : apt
      ));
      setOpenAppointmentMenu(null);
      toast.success('Appuntamento cancellato');
      fetchData();
    } catch (error) {
      toast.error('Errore durante la cancellazione');
    }
  };

  const handleDeleteAppointment = async (id: number) => {
    if (!confirm('Sei sicuro di voler eliminare definitivamente questo appuntamento?')) return;

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/bookings/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Errore nell\'eliminazione');

      setAppointments(appointments.filter(apt => apt.id !== id));
      setOpenAppointmentMenu(null);
      toast.success('Appuntamento eliminato');
      fetchData();
    } catch (error) {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  const handleToggleCustomerStatus = async (customerId: number, currentStatus: string) => {
    try {
      const token = localStorage.getItem('admin_token');
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';

      const response = await fetch(`/api/v1/admin/customers/${customerId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) throw new Error('Errore aggiornamento status');

      setCustomers(customers.map(c =>
        c.id === customerId ? { ...c, status: newStatus } : c
      ));
      setOpenCustomerMenu(null);
      toast.success(newStatus === 'active' ? '✅ Cliente attivato' : '⚠️ Cliente disattivato');
      fetchData();
    } catch (error) {
      toast.error('Errore durante l\'aggiornamento dello status');
    }
  };

  const handleDeleteCustomer = async (customerId: number) => {
    if (!confirm('Sei sicuro di voler eliminare definitivamente questo cliente?')) return;

    try {
      const token = localStorage.getItem('admin_token');

      const response = await fetch(`/api/v1/admin/customers/${customerId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Delete failed:', errorText);
        throw new Error('Errore eliminazione');
      }

      // Rimuovi immediatamente dallo stato locale per feedback visivo istantaneo
      setCustomers(customers.filter(c => c.id !== customerId));

      toast.success('🗑️ Cliente eliminato definitivamente');

      // Ricarica comunque i dati per sicurezza
      fetchData();
    } catch (error) {
      console.error('Error deleting customer:', error);
      toast.error('Errore durante l\'eliminazione');
    }
  };  // Filter data based on search
  const filteredCustomers = customers.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.company?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredQuotes = quotes.filter(q =>
    q.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    q.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Tab configuration
  const TABS = [
    { id: 'customers' as const, label: 'Clienti', icon: Users, description: 'Gestione anagrafica clienti', color: 'from-blue-500 to-cyan-500' },
    { id: 'quotes' as const, label: 'Preventivi', icon: FileText, description: 'Preventivi e offerte commerciali', color: 'from-purple-500 to-indigo-500' },
    { id: 'appointments' as const, label: 'Appuntamenti', icon: Calendar, description: 'Calendario e prenotazioni', color: 'from-emerald-500 to-teal-500' },
    { id: 'pipeline' as const, label: 'Pipeline', icon: TrendingUp, description: 'Pipeline vendite e opportunità', color: 'from-amber-500 to-yellow-500' },
  ];

  const currentTab = TABS.find(t => t.id === activeTab);

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header with Tab Navigation - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Title Row */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <Briefcase className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              Business Hub
            </h1>
            <p className="text-sm text-muted-foreground">
              {currentTab?.description || 'Gestisci clienti, preventivi e appuntamenti'}
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-card border border-border rounded-2xl p-2 shadow-sm">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
                    isActive
                      ? `bg-gradient-to-r ${tab.color} text-white shadow-lg`
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium whitespace-nowrap">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Stats Cards - Responsive */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3 md:gap-4"
      >
        <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>Clienti Attivi</p>
              <p className={`text-lg sm:text-2xl font-bold ${textPrimary}`}>{stats.activeCustomers}</p>
            </div>
            <div className="p-2 sm:p-3 rounded-lg bg-green-500/20 flex-shrink-0">
              <Users className="h-4 w-4 sm:h-6 sm:w-6 text-green-500" />
            </div>
          </div>
          <div className="mt-1 sm:mt-2 flex items-center text-xs sm:text-sm">
            <span className={textSecondary}>su {stats.totalCustomers} totali</span>
          </div>
        </div>

        <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>Preventivi Attivi</p>
              <p className={`text-lg sm:text-2xl font-bold ${textPrimary}`}>{stats.pendingQuotes}</p>
            </div>
            <div className="p-2 sm:p-3 rounded-lg bg-blue-500/20 flex-shrink-0">
              <FileText className="h-4 w-4 sm:h-6 sm:w-6 text-blue-500" />
            </div>
          </div>
          <div className="mt-1 sm:mt-2 flex items-center text-xs sm:text-sm">
            <span className={textSecondary}>{stats.acceptedQuotes} accettati</span>
          </div>
        </div>

        <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>Appuntamenti Oggi</p>
              <p className={`text-lg sm:text-2xl font-bold ${textPrimary}`}>{stats.todayAppointments}</p>
            </div>
            <div className="p-2 sm:p-3 rounded-lg bg-purple-500/20 flex-shrink-0">
              <Calendar className="h-4 w-4 sm:h-6 sm:w-6 text-purple-500" />
            </div>
          </div>
          <div className="mt-1 sm:mt-2 flex items-center text-xs sm:text-sm">
            <span className={textSecondary}>{appointments.length} totali</span>
          </div>
        </div>

        <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>Fatturato Totale</p>
              <p className={`text-lg sm:text-2xl font-bold ${textPrimary}`}>
                €{stats.totalRevenue.toLocaleString('it-IT', { maximumFractionDigits: 0 })}
              </p>
            </div>
            <div className="p-2 sm:p-3 rounded-lg bg-gold/20 flex-shrink-0">
              <Euro className="h-4 w-4 sm:h-6 sm:w-6 text-gold" />
            </div>
          </div>
          <div className="mt-1 sm:mt-2 flex items-center text-xs sm:text-sm">
            <span className={textSecondary}>da preventivi</span>
          </div>
        </div>
      </motion.div>

      {/* Search & Actions Bar - Responsive */}
      <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
        <div className="flex flex-col gap-3">
          {/* Search Input */}
          <div className="relative w-full">
            <Search className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 ${textSecondary}`} />
            <input
              type="text"
              placeholder="Cerca..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={cn('w-full pl-10 pr-4 py-2.5 sm:py-2 rounded-lg border min-h-[44px]', inputBg)}
            />
          </div>

          {/* Actions - Responsive Mobile Stack */}
          <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
            {/* Secondary Actions - Scrollable on mobile */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0 -mx-1 px-1 sm:mx-0 sm:px-0 no-scrollbar mask-gradient-right flex-1">
              <Button
                variant="outline"
                size="sm"
                className={cn('min-h-[44px] flex-shrink-0', isDark ? 'border-white/20' : '')}
              >
                <Filter className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Filtri</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                className={cn('min-h-[44px] flex-shrink-0', isDark ? 'border-white/20' : '')}
              >
                <Download className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Esporta</span>
              </Button>
            </div>

            {/* Primary Action - Full width on mobile */}
            <Button
              onClick={() => {
                if (activeTab === 'customers') {
                  setModalMode('create');
                  setSelectedCustomer(null);
                  setShowCustomerModal(true);
                } else if (activeTab === 'quotes') {
                  setModalMode('create');
                  setSelectedQuote(null);
                  setShowQuoteModal(true);
                } else if (activeTab === 'appointments') {
                  setSelectedBooking(null);
                  setModalMode('create');
                  setPrefilledDate(undefined);
                  setShowBookingModal(true);
                } else {
                  toast.info('Feature in arrivo!');
                }
              }}
              className="bg-gold hover:bg-gold/90 text-black min-h-[44px] w-full sm:w-auto shadow-md flex-shrink-0"
            >
              <Plus className="h-4 w-4 mr-2" />
              <span>
                {activeTab === 'customers' ? 'Nuovo Cliente' :
                  activeTab === 'quotes' ? 'Nuovo Preventivo' :
                    activeTab === 'appointments' ? 'Nuovo Appuntamento' : 'Nuovo Deal'}
              </span>
            </Button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'customers' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl divide-y ${isDark ? 'divide-white/10' : 'divide-gray-100'}`}
        >
          {loading ? (
            <div className="p-8 sm:p-12 text-center">
              <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
            </div>
          ) : filteredCustomers.length === 0 ? (
            <div className="p-8 sm:p-12 text-center">
              <Users className={`h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 ${textSecondary} opacity-50`} />
              <p className={`text-sm sm:text-base ${textSecondary}`}>Nessun cliente trovato</p>
            </div>
          ) : (
            filteredCustomers.map(customer => (
              <div
                key={customer.id}
                className={cn(
                  'p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4',
                  isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'
                )}
              >
                {/* Avatar + Nome */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-[#D4AF37] font-medium text-sm sm:text-base">
                      {customer.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium text-sm sm:text-base ${textPrimary} truncate`}>{customer.name}</p>
                    {customer.company && (
                      <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>{customer.company}</p>
                    )}
                  </div>
                </div>

                {/* Contatti - Mobile sotto, Desktop a destra */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 flex-1">
                  <div className="space-y-1 flex-1 min-w-0">
                    <div className={`flex items-center gap-2 text-xs sm:text-sm ${textSecondary}`}>
                      <Mail className="h-3 w-3 flex-shrink-0" />
                      <span className="truncate">{customer.email}</span>
                    </div>
                    {customer.phone && (
                      <div className={`flex items-center gap-2 text-xs sm:text-sm ${textSecondary}`}>
                        <Phone className="h-3 w-3 flex-shrink-0" />
                        <span className="truncate">{customer.phone}</span>
                      </div>
                    )}
                  </div>

                  {/* Città */}
                  <div className={`hidden sm:flex items-center gap-2 ${textSecondary} w-32`}>
                    <MapPin className="h-4 w-4 flex-shrink-0" />
                    <span className="text-sm truncate">{customer.city || '-'}</span>
                  </div>
                </div>

                {/* Stats + Status + Actions */}
                <div className="flex items-center justify-between sm:justify-end gap-2 sm:gap-4">
                  {/* Stats - Desktop only */}
                  <div className="hidden lg:flex items-center gap-4">
                    <div className="text-center">
                      <p className={`text-xs ${textSecondary}`}>Preventivi</p>
                      <p className={`font-medium text-sm ${textPrimary}`}>{customer.total_quotes || 0}</p>
                    </div>
                    <div className="text-center">
                      <p className={`text-xs ${textSecondary}`}>Fatturato</p>
                      <p className={`font-medium text-sm ${textPrimary}`}>€{(customer.total_revenue || 0).toLocaleString('it-IT')}</p>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs whitespace-nowrap',
                    customer.status === 'active' ? 'bg-green-500/20 text-green-500' :
                      customer.status === 'lead' ? 'bg-blue-500/20 text-blue-500' :
                        'bg-gray-500/20 text-gray-500'
                  )}>
                    {customer.status === 'active' ? 'Attivo' :
                      customer.status === 'lead' ? 'Lead' : 'Inattivo'}
                  </span>

                  {/* Actions Dropdown */}
                  <div className="relative">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          size="sm"
                          variant="outline"
                          className={isDark ? 'border-white/20' : ''}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuItem onClick={() => {
                          setSelectedCustomer(customer);
                          setModalMode('view');
                          setShowCustomerModal(true);
                        }}>
                          <Eye className="h-4 w-4 mr-2 text-gray-500" />
                          Vedi Dettagli
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => {
                          setSelectedCustomer(customer);
                          setModalMode('edit');
                          setShowCustomerModal(true);
                        }}>
                          <Edit2 className="h-4 w-4 mr-2 text-gold" />
                          Modifica
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleToggleCustomerStatus(customer.id, customer.status)}>
                          {customer.status === 'active' ? (
                            <>
                              <XCircle className="h-4 w-4 mr-2 text-gold" />
                              Disattiva Cliente
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="h-4 w-4 mr-2 text-gold" />
                              Attiva Cliente
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => handleDeleteCustomer(customer.id)}
                          className="text-red-500 focus:text-red-500"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Elimina Definitivamente
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </div>
            ))
          )}
        </motion.div>
      )}

      {activeTab === 'quotes' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl divide-y ${isDark ? 'divide-white/10' : 'divide-gray-100'}`}
        >
          {loading ? (
            <div className="p-8 sm:p-12 text-center">
              <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
            </div>
          ) : filteredQuotes.length === 0 ? (
            <div className="p-8 sm:p-12 text-center">
              <FileText className={`h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 ${textSecondary} opacity-50`} />
              <p className={`text-sm sm:text-base ${textSecondary}`}>Nessun preventivo trovato</p>
            </div>
          ) : (
            filteredQuotes.map(quote => (
              <div
                key={quote.id}
                className={cn(
                  'p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4',
                  isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'
                )}
              >
                {/* Quote Number + Date */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gold/20 flex items-center justify-center flex-shrink-0">
                    <FileText className="h-5 w-5 sm:h-6 sm:w-6 text-gold" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium text-sm sm:text-base ${textPrimary}`}>#{quote.number}</p>
                    <p className={`text-xs sm:text-sm ${textSecondary}`}>
                      {new Date(quote.created_at).toLocaleDateString('it-IT')}
                    </p>
                  </div>
                </div>

                {/* Customer + Total */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 flex-1">
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm ${textPrimary} truncate`}>{quote.customer_name}</p>
                    <p className={`text-xs ${textSecondary}`}>
                      Scade: {new Date(quote.valid_until).toLocaleDateString('it-IT')}
                    </p>
                  </div>
                  <div className="text-left sm:text-right min-w-[100px]">
                    <p className={`font-bold text-lg ${textPrimary}`}>
                      €{quote.total.toLocaleString('it-IT')}
                    </p>
                  </div>
                </div>

                {/* Status + Actions */}
                <div className="flex items-center justify-between sm:justify-end gap-2 sm:gap-3">
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs text-white',
                    QUOTE_STATUS[quote.status]?.color || 'bg-gray-500'
                  )}>
                    {QUOTE_STATUS[quote.status]?.label || quote.status}
                  </span>

                  <div className="flex items-center gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="min-h-[44px] min-w-[44px]"
                      onClick={() => {
                        setSelectedQuote(quote);
                        setModalMode('view');
                        setShowQuoteModal(true);
                      }}
                      title="Visualizza"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="min-h-[44px] min-w-[44px]"
                      onClick={() => {
                        setSelectedQuote(quote);
                        setModalMode('edit');
                        setShowQuoteModal(true);
                      }}
                      title="Modifica"
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    {quote.status === 'draft' && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="min-h-[44px] min-w-[44px]"
                        onClick={() => handleQuoteAction(quote.id, 'send')}
                        title="Invia"
                      >
                        <Send className="h-4 w-4 text-blue-500" />
                      </Button>
                    )}
                    {quote.status === 'sent' && (
                      <>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="min-h-[44px] min-w-[44px]"
                          onClick={() => handleQuoteAction(quote.id, 'accept')}
                          title="Accetta"
                        >
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="min-h-[44px] min-w-[44px]"
                          onClick={() => handleQuoteAction(quote.id, 'reject')}
                          title="Rifiuta"
                        >
                          <XCircle className="h-4 w-4 text-red-500" />
                        </Button>
                      </>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      className="min-h-[44px] min-w-[44px]"
                      onClick={() => handleDeleteQuote(quote.id)}
                      title="Elimina"
                    >
                      <Trash2 className="h-4 w-4 text-gray-400" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </motion.div>
      )}
      {activeTab === 'appointments' && (
        <div className="space-y-4">
          {/* View Toggle + Navigation - Responsive */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
            {/* View Toggle */}
            <div className="flex gap-2">
              <Button
                variant={appointmentsView === 'list' ? 'default' : 'outline'}
                onClick={() => setAppointmentsView('list')}
                size="sm"
                className={cn(
                  "flex items-center gap-2 min-h-[44px] flex-1 sm:flex-none",
                  appointmentsView === 'list' && 'bg-gold hover:bg-gold/90 text-black'
                )}
              >
                <List className="h-4 w-4" />
                <span>Lista</span>
              </Button>
              <Button
                variant={appointmentsView === 'calendar' ? 'default' : 'outline'}
                onClick={() => setAppointmentsView('calendar')}
                size="sm"
                className={cn(
                  "flex items-center gap-2 min-h-[44px] flex-1 sm:flex-none",
                  appointmentsView === 'calendar' && 'bg-gold hover:bg-gold/90 text-black'
                )}
              >
                <CalendarDays className="h-4 w-4" />
                <span>Calendario</span>
              </Button>
            </div>

            {/* Calendar Navigation - Hidden on mobile when list view */}
            {appointmentsView === 'calendar' && (
              <div className="flex items-center justify-center gap-2 overflow-x-auto">
                <Button
                  variant="outline"
                  size="sm"
                  className="min-h-[44px] min-w-[44px]"
                  onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth() - 1))}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <h3 className={`text-sm sm:text-lg font-semibold ${textPrimary} min-w-[120px] sm:min-w-[180px] text-center`}>
                  {calendarDate.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' })}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  className="min-h-[44px] min-w-[44px]"
                  onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1))}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="min-h-[44px] hidden sm:flex"
                  onClick={() => setCalendarDate(new Date())}
                >
                  Oggi
                </Button>
              </div>
            )}

            {/* New Appointment Button */}
            <Button
              className="bg-gold hover:bg-gold/90 text-black min-h-[44px] w-full sm:w-auto"
              onClick={() => {
                setSelectedBooking(null);
                setModalMode('create');
                setPrefilledDate(undefined);
                setShowBookingModal(true);
              }}
            >
              <Plus className="h-4 w-4 mr-2" />
              <span className="sm:inline">Nuovo Appuntamento</span>
            </Button>
          </div>

          {appointmentsView === 'list' ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {loading ? (
                <div className={`${cardBg} rounded-xl p-8 sm:p-12 text-center`}>
                  <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
                </div>
              ) : appointments.length === 0 ? (
                <div className={`${cardBg} rounded-xl p-8 sm:p-12 text-center`}>
                  <Calendar className={`h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 ${textSecondary} opacity-50`} />
                  <p className={`text-sm sm:text-base ${textSecondary}`}>Nessun appuntamento programmato</p>
                  <Button
                    className="mt-4 bg-gold hover:bg-gold/90 text-black min-h-[44px]"
                    onClick={() => {
                      setSelectedBooking(null);
                      setModalMode('create');
                      setPrefilledDate(undefined);
                      setShowBookingModal(true);
                    }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Nuovo Appuntamento
                  </Button>
                </div>
              ) : (
                appointments.map(apt => (
                  <div key={apt.id} className={`${cardBg} rounded-xl p-3 sm:p-4`}>
                    {/* Mobile: Stack layout, Desktop: Row layout */}
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                      {/* Date Box */}
                      <div className="flex sm:block items-center gap-3">
                        <div className={cn(
                          'w-12 h-12 sm:w-16 sm:h-16 rounded-lg flex flex-col items-center justify-center flex-shrink-0',
                          isDark ? 'bg-white/10' : 'bg-gray-100'
                        )}>
                          <span className={`text-lg sm:text-2xl font-bold ${textPrimary}`}>
                            {new Date(apt.date).getDate()}
                          </span>
                          <span className={`text-[10px] sm:text-xs ${textSecondary}`}>
                            {new Date(apt.date).toLocaleDateString('it-IT', { month: 'short' })}
                          </span>
                        </div>
                        {/* Title + Status - Mobile only inline */}
                        <div className="flex-1 sm:hidden">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h4 className={`font-medium text-sm ${textPrimary} line-clamp-1`}>{apt.title}</h4>
                            <span className={cn(
                              'px-2 py-0.5 rounded-full text-[10px] text-white whitespace-nowrap',
                              APPOINTMENT_STATUS[apt.status]?.color || 'bg-gray-500'
                            )}>
                              {APPOINTMENT_STATUS[apt.status]?.label || apt.status}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        {/* Title + Status - Desktop */}
                        <div className="hidden sm:flex items-center gap-2 flex-wrap">
                          <h4 className={`font-medium ${textPrimary}`}>{apt.title}</h4>
                          <span className={cn(
                            'px-2 py-0.5 rounded-full text-xs text-white',
                            APPOINTMENT_STATUS[apt.status]?.color || 'bg-gray-500'
                          )}>
                            {APPOINTMENT_STATUS[apt.status]?.label || apt.status}
                          </span>
                        </div>

                        {/* Details - Responsive grid */}
                        <div className={`grid grid-cols-2 sm:flex sm:items-center gap-2 sm:gap-4 mt-1 sm:mt-2 ${textSecondary} text-xs sm:text-sm`}>
                          <span className="flex items-center gap-1 truncate">
                            <Users className="h-3 w-3 flex-shrink-0" />
                            <span className="truncate">{apt.client_name}</span>
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3 flex-shrink-0" />
                            {apt.time} ({apt.duration} min)
                          </span>
                          <span className="flex items-center gap-1 col-span-2 sm:col-span-1">
                            {apt.type === 'video' ? <Video className="h-3 w-3 flex-shrink-0" /> : <Phone className="h-3 w-3 flex-shrink-0" />}
                            {apt.type === 'video' ? 'Videocall' : apt.type === 'call' ? 'Chiamata' : 'Meeting'}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center justify-end gap-2 mt-2 sm:mt-0">
                        {apt.type === 'video' && apt.status === 'confirmed' && (
                          <Button className="bg-gold hover:bg-gold text-white" size="sm">
                            <Video className="h-4 w-4 mr-2" />
                            Partecipa
                          </Button>
                        )}

                        {/* Dropdown Menu Azioni */}
                        <div className="relative">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                className={isDark ? 'border-white/20' : ''}
                              >
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-56">
                              {apt.status === 'pending' && (
                                <DropdownMenuItem onClick={() => handleConfirmAppointment(apt.id)}>
                                  <CheckCircle2 className="h-4 w-4 mr-2 text-gold" />
                                  Conferma e Invia
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem onClick={() => {
                                setSelectedBooking(apt);
                                setModalMode('edit');
                                setShowBookingModal(true);
                              }}>
                                <Edit2 className="h-4 w-4 mr-2 text-gold" />
                                Modifica
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => {
                                setSelectedBooking(apt);
                                setModalMode('view');
                                setShowBookingModal(true);
                              }}>
                                <Eye className="h-4 w-4 mr-2 text-gray-500" />
                                Vedi Dettagli
                              </DropdownMenuItem>
                              {apt.status !== 'cancelled' && apt.status !== 'completed' && (
                                <DropdownMenuItem onClick={() => handleCancelAppointment(apt.id)}>
                                  <XCircle className="h-4 w-4 mr-2 text-gold" />
                                  Cancella
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => handleDeleteAppointment(apt.id)}
                                className="text-red-500 focus:text-red-500"
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Elimina
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="min-h-[600px]"
            >
              {calendarLoading ? (
                <div className={`${cardBg} rounded-xl p-12 text-center`}>
                  <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
                  <p className={`mt-4 ${textSecondary}`}>Caricamento calendario...</p>
                </div>
              ) : calendarBookings?.days?.length > 0 ? (
                <CalendarGrid
                  days={calendarBookings.days}
                  onBookingClick={(booking) => {
                    setSelectedBooking(booking);
                    setModalMode('view');
                    setShowBookingModal(true);
                  }}
                />
              ) : (
                <div className={`${cardBg} rounded-xl p-12 text-center`}>
                  <Calendar className={`h-12 w-12 mx-auto mb-4 ${textSecondary} opacity-50`} />
                  <p className={textSecondary}>Nessuna prenotazione questo mese</p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      )}

      {activeTab === 'pipeline' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4"
        >
          {PIPELINE_STAGES.filter(s => !s.id.includes('closed')).map(stage => (
            <div key={stage.id} className={`${cardBg} rounded-xl p-4`}>
              <div className="flex items-center gap-2 mb-4">
                <div className={cn('w-3 h-3 rounded-full', stage.color)} />
                <h4 className={`font-medium ${textPrimary}`}>{stage.label}</h4>
                <span className={`ml-auto text-sm ${textSecondary}`}>
                  {deals.filter(d => d.stage === stage.id).length}
                </span>
              </div>

              <div className="space-y-3">
                {deals.filter(d => d.stage === stage.id).length === 0 ? (
                  <div className={`p-4 rounded-lg border-2 border-dashed ${isDark ? 'border-white/10' : 'border-gray-200'} text-center`}>
                    <p className={`text-sm ${textSecondary}`}>Nessun deal</p>
                  </div>
                ) : (
                  deals.filter(d => d.stage === stage.id).map(deal => (
                    <div
                      key={deal.id}
                      className={cn(
                        'p-3 rounded-lg cursor-pointer transition-all',
                        isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                      )}
                    >
                      <p className={`font-medium ${textPrimary}`}>{deal.name}</p>
                      <p className={`text-sm ${textSecondary}`}>{deal.customer}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className={`font-bold text-[#D4AF37]`}>
                          €{deal.value.toLocaleString('it-IT')}
                        </span>
                        <span className={`text-xs ${textSecondary}`}>
                          {deal.probability}%
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <Button
                variant="ghost"
                className="w-full mt-3"
                size="sm"
              >
                <Plus className="h-4 w-4 mr-1" />
                Aggiungi
              </Button>
            </div>
          ))}
        </motion.div>
      )}

      {/* Modals */}
      <CustomerModal
        isOpen={showCustomerModal}
        onClose={() => {
          setShowCustomerModal(false);
          setSelectedCustomer(null);
        }}
        customer={selectedCustomer}
        onSuccess={fetchData}
        mode={modalMode}
      />

      <QuoteModal
        isOpen={showQuoteModal}
        onClose={() => {
          setShowQuoteModal(false);
          setSelectedQuote(null);
        }}
        quote={selectedQuote}
        onSuccess={fetchData}
        mode={modalMode}
        customers={customers}
      />

      <BookingModal
        isOpen={showBookingModal}
        booking={selectedBooking}
        onClose={() => {
          setShowBookingModal(false);
          setSelectedBooking(null);
          setPrefilledDate(undefined);
        }}
        onSuccess={fetchData}
      />
    </div>
  );
}

export default BusinessHub;
