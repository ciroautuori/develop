/**
 * Finance Hub - Centro Gestione Finanziaria
 * Unifica: Dashboard Finance + Fatture + Pagamenti + Report
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Euro,
  TrendingUp,
  TrendingDown,
  CreditCard,
  FileText,
  PieChart,
  BarChart3,
  Download,
  Filter,
  Calendar,
  ArrowUpRight,
  Plus,
  Eye,
  Send,
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
  Receipt,
  Wallet,
  Building2,
  Trash2,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { SPACING } from '../../../shared/config/constants';
import { ExpenseFormModal } from '../components/ExpenseFormModal';

// Types
interface Invoice {
  id: number;
  number: string;
  customer_name: string;
  amount: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  issue_date: string;
  due_date: string;
  paid_date?: string;
}

interface Payment {
  id: number;
  invoice_number: string;
  customer_name: string;
  amount: number;
  method: 'stripe' | 'bank_transfer' | 'cash' | 'paypal';
  date: string;
  status: 'completed' | 'pending' | 'failed';
}

interface FinancialMetrics {
  revenue_mtd: number;
  revenue_ytd: number;
  revenue_change: number;
  expenses_mtd: number;
  profit_mtd: number;
  profit_margin: number;
  outstanding_invoices: number;
  overdue_amount: number;
  avg_payment_days: number;
}

const INVOICE_STATUS: Record<string, { label: string; color: string; icon: any }> = {
  draft: { label: 'Bozza', color: 'bg-muted text-muted-foreground', icon: FileText },
  sent: { label: 'Inviata', color: 'bg-primary/10 text-primary', icon: Send },
  paid: { label: 'Pagata', color: 'bg-green-500/10 text-green-500', icon: CheckCircle2 },
  overdue: { label: 'Scaduta', color: 'bg-destructive/10 text-destructive', icon: AlertCircle },
  cancelled: { label: 'Annullata', color: 'bg-muted text-muted-foreground', icon: AlertCircle },
};

export function FinanceHub() {
  const [activeTab, setActiveTab] = useState<'overview' | 'expenses' | 'invoices' | 'payments' | 'reports'>('overview');

  // State
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [expenses, setExpenses] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<FinancialMetrics>({
    revenue_mtd: 0,
    revenue_ytd: 0,
    revenue_change: 0,
    expenses_mtd: 0,
    profit_mtd: 0,
    profit_margin: 0,
    outstanding_invoices: 0,
    overdue_amount: 0,
    avg_payment_days: 0,
  });
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState('month');
  const [monthlyData, setMonthlyData] = useState<{ month: string; revenue: number; expenses: number }[]>([]);
  const [revenueBreakdown, setRevenueBreakdown] = useState<{ label: string; value: number; color: string }[]>([]);

  // Expense modal state
  const [showExpenseModal, setShowExpenseModal] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<any>(null);

  // Fetch data
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch finance dashboard stats
      const summaryRes = await fetch('/api/v1/admin/finance/dashboard/stats', { headers });
      if (summaryRes.ok) {
        const data = await summaryRes.json();
        setMetrics({
          revenue_mtd: data.total_revenue || 0,
          revenue_ytd: data.total_revenue || 0,
          revenue_change: data.revenue_change || 0,
          expenses_mtd: data.total_expenses || 0,
          profit_mtd: (data.total_revenue || 0) - (data.total_expenses || 0),
          profit_margin: data.total_revenue ? (((data.total_revenue - data.total_expenses) / data.total_revenue) * 100) : 0,
          outstanding_invoices: data.pending_invoices || 0,
          overdue_amount: data.overdue_amount || 0,
          avg_payment_days: data.avg_payment_days || 0,
        });
      }

      // Fetch recent expenses as transactions proxy
      const transRes = await fetch('/api/v1/admin/finance/expenses?page=1&page_size=50', { headers });
      if (transRes.ok) {
        const data = await transRes.json();
        const transactions = data.items || data || [];
        setExpenses(transactions);

        // Transform to payments
        const recentPayments = transactions.slice(0, 10).map((t: any, idx: number) => ({
          id: t.id || idx,
          invoice_number: t.invoice_number || `INV-${new Date(t.due_date || t.date).getFullYear()}${String(idx + 1).padStart(4, '0')}`,
          customer_name: t.title || t.description || t.client_name || 'Cliente',
          amount: Math.abs(t.amount || 0),
          method: t.payment_method || (t.category === 'stripe' ? 'stripe' : 'bank_transfer'),
          date: t.due_date || t.date || new Date().toISOString(),
          status: t.status || 'completed',
        }));
        setPayments(recentPayments);

        // Build monthly data from real transactions
        const monthNames = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
        const monthlyMap: Record<string, { revenue: number; expenses: number }> = {};

        transactions.forEach((t: any) => {
          const date = new Date(t.due_date || t.date);
          const monthKey = `${date.getFullYear()}-${date.getMonth()}`;
          if (!monthlyMap[monthKey]) {
            monthlyMap[monthKey] = { revenue: 0, expenses: 0 };
          }
          if (t.amount > 0 || t.type === 'income') {
            monthlyMap[monthKey].revenue += Math.abs(t.amount || 0);
          } else {
            monthlyMap[monthKey].expenses += Math.abs(t.amount || 0);
          }
        });

        // Convert to array, last 6 months
        const sortedMonths = Object.keys(monthlyMap).sort().slice(-6);
        const chartData = sortedMonths.map(key => {
          const [year, month] = key.split('-');
          return {
            month: monthNames[parseInt(month)],
            revenue: monthlyMap[key].revenue,
            expenses: monthlyMap[key].expenses,
          };
        });
        setMonthlyData(chartData.length > 0 ? chartData : []);

        // Build revenue breakdown by category
        const categoryMap: Record<string, number> = {};
        transactions.filter((t: any) => t.amount > 0 || t.type === 'income').forEach((t: any) => {
          const cat = t.category || 'Altro';
          categoryMap[cat] = (categoryMap[cat] || 0) + Math.abs(t.amount || 0);
        });

        const colors = ['bg-primary', 'bg-primary/80', 'bg-primary/60', 'bg-primary/40', 'bg-muted'];
        const breakdown = Object.entries(categoryMap)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([label, value], idx) => ({
            label,
            value: Math.round(value),
            color: colors[idx % colors.length],
          }));

        // Calculate percentages
        const total = breakdown.reduce((acc, b) => acc + b.value, 0);
        const breakdownWithPercent = breakdown.map(b => ({
          ...b,
          value: total > 0 ? Math.round((b.value / total) * 100) : 0,
        }));
        setRevenueBreakdown(breakdownWithPercent);
      }

    } catch (error) {
      console.error('Error fetching finance data:', error);
    }
    setLoading(false);
  };

  const handleDeleteExpense = async (expenseId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questa spesa?')) return;

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/finance/expenses/${expenseId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Errore eliminazione');

      toast.success('Spesa eliminata!');
      fetchData();
    } catch (error) {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  const maxRevenue = Math.max(...monthlyData.map(d => d.revenue), 1);

  // Tab configuration
  const TABS = [
    { id: 'overview' as const, label: 'Panoramica', icon: PieChart, description: 'Dashboard finanziaria', color: 'from-amber-500 to-yellow-500' },
    { id: 'invoices' as const, label: 'Fatture', icon: FileText, description: 'Gestione fatture clienti', color: 'from-primary to-primary/60' },
    { id: 'expenses' as const, label: 'Spese', icon: Receipt, description: 'Tracciamento uscite e costi', color: 'from-primary via-primary/80 to-primary/60' },
    { id: 'payments' as const, label: 'Pagamenti', icon: CreditCard, description: 'Storico pagamenti ricevuti', color: 'from-emerald-500 to-teal-500' },
    { id: 'reports' as const, label: 'Report', icon: BarChart3, description: 'Analisi e reportistica', color: 'from-primary to-primary/70' },
  ];

  const currentTab = TABS.find(t => t.id === activeTab);

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Expense Form Modal */}
      <ExpenseFormModal
        isOpen={showExpenseModal}
        onClose={() => {
          setShowExpenseModal(false);
          setSelectedExpense(null);
        }}
        onSuccess={fetchData}
        expense={selectedExpense}
      />

      {/* Header with Tab Navigation - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Title Row */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <Wallet className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              Finance Hub
            </h1>
            <p className="text-sm text-muted-foreground">
              {currentTab?.description || 'Gestione finanziaria completa'}
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

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* KPI Cards - Mobile First */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Fatturato MTD</p>
                  <p className="text-2xl font-bold text-foreground">
                    €{metrics.revenue_mtd.toLocaleString('it-IT')}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-primary/10">
                  <Euro className="h-6 w-6 text-primary" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm text-primary">
                <ArrowUpRight className="h-4 w-4" />
                <span>+{metrics.revenue_change.toFixed(1)}% vs mese scorso</span>
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Spese MTD</p>
                  <p className="text-2xl font-bold text-foreground">
                    €{metrics.expenses_mtd.toLocaleString('it-IT')}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-muted">
                  <TrendingDown className="h-6 w-6 text-muted-foreground" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-muted-foreground">Mese corrente</span>
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Profitto MTD</p>
                  <p className="text-2xl font-bold text-foreground">
                    €{metrics.profit_mtd.toLocaleString('it-IT')}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-green-500/10">
                  <TrendingUp className="h-6 w-6 text-green-500" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-muted-foreground">
                  Margine: <span className="text-primary">{metrics.profit_margin.toFixed(1)}%</span>
                </span>
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Da Incassare</p>
                  <p className="text-2xl font-bold text-foreground">
                    €{metrics.outstanding_invoices.toLocaleString('it-IT')}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-orange-500/10">
                  <Clock className="h-6 w-6 text-orange-500" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-muted-foreground">Media incasso: {metrics.avg_payment_days} giorni</span>
              </div>
            </div>
          </div>

          {/* Charts - Mobile First */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {/* Revenue Chart */}
            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-foreground">Andamento Fatturato</h3>
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="px-3 py-1 rounded-lg text-sm border border-input bg-background text-foreground"
                >
                  <option value="month">Ultimi 6 mesi</option>
                  <option value="year">Anno corrente</option>
                </select>
              </div>

              <div className="h-64 flex items-end gap-4">
                {monthlyData.length === 0 ? (
                  <div className="flex-1 flex items-center justify-center">
                    <p className="text-muted-foreground">Nessun dato disponibile</p>
                  </div>
                ) : (
                  monthlyData.map((data, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                      <div className="w-full flex flex-col gap-1">
                        <div
                          className="w-full bg-primary rounded-t"
                          style={{ height: `${(data.revenue / maxRevenue) * 180}px` }}
                        />
                        <div
                          className="w-full bg-muted rounded-b"
                          style={{ height: `${(data.expenses / maxRevenue) * 180}px` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">{data.month}</span>
                    </div>
                  ))
                )}
              </div>

              <div className="flex items-center justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-primary" />
                  <span className="text-sm text-muted-foreground">Fatturato</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-muted" />
                  <span className="text-sm text-muted-foreground">Spese</span>
                </div>
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
              <h3 className="font-semibold text-foreground mb-6">Suddivisione Entrate</h3>

              <div className="space-y-4">
                {revenueBreakdown.length === 0 ? (
                  <p className="text-muted-foreground">Nessun dato disponibile</p>
                ) : (
                  revenueBreakdown.map((item, idx) => (
                    <div key={idx}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-foreground">{item.label}</span>
                        <span className="text-muted-foreground">{item.value}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div
                          className={cn('h-full rounded-full', item.color)}
                          style={{ width: `${item.value}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground">Ultimi Movimenti</h3>
              <Button variant="ghost" size="sm">
                Vedi tutti <ArrowUpRight className="h-4 w-4 ml-1" />
              </Button>
            </div>

            <div className="divide-y divide-border">
              {payments.slice(0, 5).map(payment => (
                <div key={payment.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Receipt className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{payment.customer_name}</p>
                      <p className="text-sm text-muted-foreground">{payment.invoice_number}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-primary">
                      +€{payment.amount.toLocaleString('it-IT')}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(payment.date).toLocaleDateString('it-IT')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )
      }

      {/* Invoices Tab */}
      {
        activeTab === 'invoices' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {/* Actions Bar - Mobile Responsive Fix */}
            <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
              {/* Scrollable Filters Group */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0 -mx-1 px-1 sm:mx-0 sm:px-0 no-scrollbar mask-gradient-right">
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Filter className="h-4 w-4 mr-2" />
                  Filtri
                </Button>
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Calendar className="h-4 w-4 mr-2" />
                  Periodo
                </Button>
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Download className="h-4 w-4 mr-2" />
                  Esporta
                </Button>
              </div>

              {/* Primary Action - Full width on mobile */}
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto shadow-md">
                <Plus className="h-4 w-4 mr-2" />
                Nuova Fattura
              </Button>
            </div>

            {/* Invoices List - Responsive */}
            <div className="space-y-4">
              {/* Mobile View - Cards */}
              <div className="grid grid-cols-1 gap-4 md:hidden">
                {invoices.length === 0 ? (
                  <div className="bg-card border border-border rounded-xl p-8 text-center">
                    <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <p className="text-muted-foreground">Nessuna fattura</p>
                    <Button className="mt-4 bg-primary text-primary-foreground">
                      <Plus className="h-4 w-4 mr-2" />
                      Crea Prima Fattura
                    </Button>
                  </div>
                ) : (
                  invoices.map(invoice => (
                    <div key={invoice.id} className="bg-card border border-border rounded-xl p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-foreground">#{invoice.number}</p>
                          <p className="text-sm text-muted-foreground">{invoice.customer_name}</p>
                        </div>
                        <span className={cn(
                          'px-2 py-1 rounded-full text-xs flex items-center gap-1',
                          INVOICE_STATUS[invoice.status]?.color || 'bg-muted text-muted-foreground'
                        )}>
                          {INVOICE_STATUS[invoice.status]?.label || invoice.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-muted-foreground text-xs">Importo</p>
                          <p className="font-bold text-foreground">€{invoice.amount.toLocaleString('it-IT')}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Scadenza</p>
                          <p className="text-foreground">{new Date(invoice.due_date).toLocaleDateString('it-IT')}</p>
                        </div>
                      </div>

                      <div className="flex justify-end gap-2 pt-3 border-t border-border">
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Desktop View - Table */}
              <div className="hidden md:block bg-card border border-border rounded-xl overflow-hidden shadow-sm">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Fattura</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Cliente</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Importo</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Scadenza</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Azioni</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {invoices.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center">
                          <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                          <p className="text-muted-foreground">Nessuna fattura</p>
                          <Button className="mt-4 bg-primary text-primary-foreground">
                            <Plus className="h-4 w-4 mr-2" />
                            Crea Prima Fattura
                          </Button>
                        </td>
                      </tr>
                    ) : (
                      invoices.map(invoice => (
                        <tr key={invoice.id} className="hover:bg-muted/50 transition-colors">
                          <td className="px-6 py-4">
                            <p className="font-medium text-foreground">#{invoice.number}</p>
                            <p className="text-sm text-muted-foreground">
                              {new Date(invoice.issue_date).toLocaleDateString('it-IT')}
                            </p>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-foreground">{invoice.customer_name}</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="font-bold text-foreground">
                              €{invoice.amount.toLocaleString('it-IT')}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={cn(
                              'px-2 py-1 rounded-full text-xs flex items-center gap-1 w-fit',
                              INVOICE_STATUS[invoice.status]?.color || 'bg-muted text-muted-foreground'
                            )}>
                              {INVOICE_STATUS[invoice.status]?.icon && (
                                <CheckCircle2 className="h-3 w-3" />
                              )}
                              {INVOICE_STATUS[invoice.status]?.label || invoice.status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-muted-foreground">
                              {new Date(invoice.due_date).toLocaleDateString('it-IT')}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button size="sm" variant="ghost">
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Download className="h-4 w-4" />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Send className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )
      }

      {/* Expenses Tab */}
      {
        activeTab === 'expenses' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {/* Actions Bar - Mobile Responsive Fix */}
            <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
              {/* Scrollable Filters Group */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0 -mx-1 px-1 sm:mx-0 sm:px-0 no-scrollbar mask-gradient-right">
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Filter className="h-4 w-4 mr-2" />
                  Filtri
                </Button>
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Calendar className="h-4 w-4 mr-2" />
                  Periodo
                </Button>
                <Button variant="outline" size="sm" className="border-input whitespace-nowrap flex-shrink-0">
                  <Download className="h-4 w-4 mr-2" />
                  Esporta CSV
                </Button>
              </div>

              {/* Primary Action - Full width on mobile */}
              <Button
                className="bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto shadow-md"
                onClick={() => {
                  setSelectedExpense(null);
                  setShowExpenseModal(true);
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                Nuova Spesa
              </Button>
            </div>

            {/* Expenses List - Responsive */}
            <div className="space-y-4">
              {/* Mobile View - Cards */}
              <div className="grid grid-cols-1 gap-4 md:hidden">
                {loading ? (
                  <div className="bg-card border border-border rounded-xl p-8 text-center">
                    <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
                  </div>
                ) : expenses.length === 0 ? (
                  <div className="bg-card border border-border rounded-xl p-8 text-center">
                    <Receipt className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <p className="text-muted-foreground">Nessuna spesa registrata</p>
                    <Button
                      className="mt-4 bg-primary text-primary-foreground"
                      onClick={() => {
                        setSelectedExpense(null);
                        setShowExpenseModal(true);
                      }}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Aggiungi Prima Spesa
                    </Button>
                  </div>
                ) : (
                  expenses.map(expense => (
                    <div key={expense.id} className="bg-card border border-border rounded-xl p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-foreground">{expense.title}</p>
                          {expense.supplier_name && (
                            <p className="text-sm text-muted-foreground">{expense.supplier_name}</p>
                          )}
                        </div>
                        <span className={cn(
                          'px-2 py-1 rounded-full text-xs capitalize',
                          'bg-primary/10 text-primary'
                        )}>
                          {expense.category}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-muted-foreground text-xs">Importo</p>
                          <p className="font-bold text-foreground">
                            €{(expense.amount || 0).toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Scadenza</p>
                          <p className={cn(
                            "text-foreground",
                            expense.is_overdue && 'text-destructive font-medium'
                          )}>
                            {new Date(expense.due_date).toLocaleDateString('it-IT')}
                          </p>
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-border">
                        <span className={cn(
                          'px-2 py-1 rounded-full text-xs',
                          expense.status === 'paid' ? 'bg-green-500/10 text-green-500' : 'bg-yellow-500/10 text-yellow-500'
                        )}>
                          {expense.status === 'paid' ? 'Pagata' : 'In Attesa'}
                        </span>

                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteExpense(expense.id)}
                          className="text-destructive hover:text-destructive/90 hover:bg-destructive/10 h-8 w-8"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Desktop View - Table */}
              <div className="hidden md:block bg-card border border-border rounded-xl overflow-x-auto shadow-sm">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Spesa</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Categoria</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Importo</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Scadenza</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Azioni</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {loading ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center">
                          <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
                        </td>
                      </tr>
                    ) : expenses.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center">
                          <Receipt className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                          <p className="text-muted-foreground">Nessuna spesa registrata</p>
                          <Button
                            className="mt-4 bg-primary text-primary-foreground"
                            onClick={() => {
                              setSelectedExpense(null);
                              setShowExpenseModal(true);
                            }}
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Aggiungi Prima Spesa
                          </Button>
                        </td>
                      </tr>
                    ) : (
                      expenses.map(expense => (
                        <tr key={expense.id} className="hover:bg-muted/50 transition-colors">
                          <td className="px-6 py-4">
                            <div>
                              <p className="font-medium text-foreground">{expense.title}</p>
                              {expense.supplier_name && (
                                <p className="text-sm text-muted-foreground">{expense.supplier_name}</p>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={cn(
                              'px-2 py-1 rounded-full text-xs capitalize',
                              'bg-primary/10 text-primary'
                            )}>
                              {expense.category}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="font-bold text-foreground">
                              €{(expense.amount || 0).toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                            </span>
                            {expense.vat_rate > 0 && (
                              <p className="text-xs text-muted-foreground">IVA {expense.vat_rate}%</p>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <span className={cn(
                              "text-muted-foreground",
                              expense.is_overdue && 'text-destructive font-medium'
                            )}>
                              {new Date(expense.due_date).toLocaleDateString('it-IT')}
                            </span>
                            {expense.is_overdue && (
                              <p className="text-xs text-destructive">Scaduta</p>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <span className={cn(
                              'px-2 py-1 rounded-full text-xs',
                              expense.status === 'paid' ? 'bg-green-500/10 text-green-500' : 'bg-yellow-500/10 text-yellow-500'
                            )}>
                              {expense.status === 'paid' ? 'Pagata' : 'In Attesa'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDeleteExpense(expense.id)}
                                className="text-destructive hover:text-destructive/90 hover:bg-destructive/10"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )
      }
    </div >
  );
}
