/**
 * ExpensesCalendar - Calendario interattivo spese StudioCentOS
 * Timeline mensile con drag&drop e editing inline
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft, ChevronRight, Plus, Edit3, Trash2,
  Euro, Calendar as CalendarIcon, Clock, AlertTriangle,
  Check, X, Eye, Filter, Download
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Badge } from '../../../shared/components/ui/badge';
import { Input } from '../../../shared/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../../../shared/components/ui/select';
import { cn } from '../../../shared/lib/utils';

// Types
interface CalendarExpense {
  id: number;
  title: string;
  amount: number;
  currency: string;
  due_date: string;
  status: 'pending' | 'paid' | 'overdue' | 'canceled';
  category: string;
  subcategory?: string;
  supplier_name?: string;
  is_overdue: boolean;
  days_until_due: number;
  priority?: 'low' | 'medium' | 'high' | 'critical';
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  expenses: CalendarExpense[];
  totalAmount: number;
}

interface ExpensesCalendarProps {
  year?: number;
  month?: number;
  expenses: CalendarExpense[];
  onDateClick?: (date: Date, expenses: CalendarExpense[]) => void;
  onExpenseClick?: (expense: CalendarExpense) => void;
  onExpenseEdit?: (expense: CalendarExpense) => void;
  onExpenseDelete?: (expenseId: number) => void;
  onAddExpense?: (date: Date) => void;
  className?: string;
}

const MONTHS_IT = [
  'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
  'luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
];

const DAYS_IT = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];

const CATEGORIES_COLORS = {
  infrastruttura: 'bg-gold',
  marketing: 'bg-gold',
  formazione: 'bg-gold',
  business: 'bg-gold',
  tools: 'bg-gray-500',
  legale: 'bg-gray-500',
  investimenti: 'bg-gold',
} as const;

export function ExpensesCalendar({
  year = new Date().getFullYear(),
  month = new Date().getMonth(),
  expenses = [],
  onDateClick,
  onExpenseClick,
  onExpenseEdit,
  onExpenseDelete,
  onAddExpense,
  className
}: ExpensesCalendarProps) {
  const [currentYear, setCurrentYear] = useState(year);
  const [currentMonth, setCurrentMonth] = useState(month);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // Calcola giorni del calendario
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days: CalendarDay[] = [];
    const today = new Date();

    // Giorni del mese precedente
    const prevMonth = new Date(currentYear, currentMonth - 1, 0);
    for (let i = startingDay - 1; i >= 0; i--) {
      const date = new Date(currentYear, currentMonth - 1, prevMonth.getDate() - i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        expenses: [],
        totalAmount: 0
      });
    }

    // Giorni del mese corrente
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, currentMonth, day);
      const dayExpenses = expenses.filter(expense => {
        const expenseDate = new Date(expense.due_date);
        return expenseDate.toDateString() === date.toDateString();
      }).filter(expense => {
        // Applica filtri
        if (filterCategory !== 'all' && expense.category !== filterCategory) return false;
        if (filterStatus !== 'all' && expense.status !== filterStatus) return false;
        return true;
      });

      days.push({
        date,
        isCurrentMonth: true,
        isToday: date.toDateString() === today.toDateString(),
        expenses: dayExpenses,
        totalAmount: dayExpenses.reduce((sum, exp) => sum + exp.amount, 0)
      });
    }

    // Giorni del mese successivo per completare la griglia
    const remainingDays = 42 - days.length; // 6 settimane x 7 giorni
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(currentYear, currentMonth + 1, day);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        expenses: [],
        totalAmount: 0
      });
    }

    return days;
  }, [currentYear, currentMonth, expenses, filterCategory, filterStatus]);

  // Navigazione mesi
  const navigateMonth = useCallback((direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      if (currentMonth === 0) {
        setCurrentMonth(11);
        setCurrentYear(prev => prev - 1);
      } else {
        setCurrentMonth(prev => prev - 1);
      }
    } else {
      if (currentMonth === 11) {
        setCurrentMonth(0);
        setCurrentYear(prev => prev + 1);
      } else {
        setCurrentMonth(prev => prev + 1);
      }
    }
  }, [currentMonth]);

  // Handle date click
  const handleDateClick = useCallback((day: CalendarDay) => {
    setSelectedDate(day.date);
    onDateClick?.(day.date, day.expenses);
  }, [onDateClick]);

  // Handle add expense
  const handleAddExpense = useCallback((date: Date) => {
    setShowAddModal(true);
    onAddExpense?.(date);
  }, [onAddExpense]);

  // Statistiche mese corrente
  const monthStats = useMemo(() => {
    const monthExpenses = expenses.filter(expense => {
      const expenseDate = new Date(expense.due_date);
      return expenseDate.getMonth() === currentMonth &&
             expenseDate.getFullYear() === currentYear;
    });

    return {
      total: monthExpenses.reduce((sum, exp) => sum + exp.amount, 0),
      count: monthExpenses.length,
      overdue: monthExpenses.filter(exp => exp.is_overdue).length,
      pending: monthExpenses.filter(exp => exp.status === 'pending').length,
      paid: monthExpenses.filter(exp => exp.status === 'paid').length,
    };
  }, [expenses, currentMonth, currentYear]);

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header con controlli */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-4">
          {/* Navigazione mesi */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('prev')}
              className="h-8 w-8 p-0"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>

            <div className="text-center min-w-[200px]">
              <h2 className="text-xl font-bold text-white">
                {MONTHS_IT[currentMonth]} {currentYear}
              </h2>
              <p className="text-sm text-gray-400">
                €{monthStats.total.toLocaleString()} • {monthStats.count} spese
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('next')}
              className="h-8 w-8 p-0"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          {/* View Mode Selector */}
          <div className="flex gap-1 bg-white/5 rounded-lg p-1">
            {(['month', 'week', 'day'] as const).map((mode) => (
              <Button
                key={mode}
                variant={viewMode === mode ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode(mode)}
                className={cn(
                  "text-xs px-3 py-1 h-7",
                  viewMode === mode && "bg-gold text-black hover:bg-gold/90"
                )}
              >
                {mode === 'month' ? 'Mese' : mode === 'week' ? 'Settimana' : 'Giorno'}
              </Button>
            ))}
          </div>
        </div>

        {/* Filtri e azioni */}
        <div className="flex items-center gap-3">
          {/* Filtro categoria */}
          <Select value={filterCategory} onValueChange={setFilterCategory}>
            <SelectTrigger className="w-[140px] h-8 text-xs">
              <SelectValue placeholder="Categoria" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tutte</SelectItem>
              <SelectItem value="infrastruttura">Infrastruttura</SelectItem>
              <SelectItem value="marketing">Marketing</SelectItem>
              <SelectItem value="formazione">Formazione</SelectItem>
              <SelectItem value="business">Business</SelectItem>
              <SelectItem value="tools">Tools</SelectItem>
              <SelectItem value="legale">Legale</SelectItem>
            </SelectContent>
          </Select>

          {/* Filtro status */}
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[120px] h-8 text-xs">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tutti</SelectItem>
              <SelectItem value="pending">Da pagare</SelectItem>
              <SelectItem value="paid">Pagati</SelectItem>
              <SelectItem value="overdue">Scaduti</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>

          <Button
            className="bg-gold hover:bg-gold/90 text-black"
            size="sm"
            onClick={() => handleAddExpense(new Date())}
          >
            <Plus className="h-4 w-4 mr-2" />
            Nuova Spesa
          </Button>
        </div>
      </div>

      {/* Stats mensili */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Totale Mese</p>
                <p className="text-lg font-bold text-white">
                  €{monthStats.total.toLocaleString()}
                </p>
              </div>
              <Euro className="h-5 w-5 text-gold" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Da Pagare</p>
                <p className="text-lg font-bold text-gold">
                  {monthStats.pending}
                </p>
              </div>
              <Clock className="h-5 w-5 text-gold" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Scadute</p>
                <p className="text-lg font-bold text-gray-400">
                  {monthStats.overdue}
                </p>
              </div>
              <AlertTriangle className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Pagate</p>
                <p className="text-lg font-bold text-gold">
                  {monthStats.paid}
                </p>
              </div>
              <Check className="h-5 w-5 text-gold" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Calendario */}
      <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
        <CardContent className="p-6">
          {/* Header giorni settimana */}
          <div className="grid grid-cols-7 gap-2 mb-4">
            {DAYS_IT.map(day => (
              <div key={day} className="text-center text-sm font-medium text-gray-400 py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Griglia calendario */}
          <div className="grid grid-cols-7 gap-2">
            {calendarDays.map((day, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.01 }}
                className={cn(
                  "min-h-[120px] p-2 rounded-lg border cursor-pointer transition-all duration-200",
                  "hover:border-gold/50 hover:bg-white/5",
                  day.isCurrentMonth
                    ? "bg-white/5 border-white/10"
                    : "bg-white/2 border-white/5 opacity-50",
                  day.isToday && "ring-2 ring-gold/50 bg-gold/10",
                  selectedDate?.toDateString() === day.date.toDateString() &&
                    "ring-2 ring-gold border-gold/50"
                )}
                onClick={() => handleDateClick(day)}
              >
                {/* Numero giorno */}
                <div className="flex items-center justify-between mb-2">
                  <span className={cn(
                    "text-sm font-medium",
                    day.isCurrentMonth ? "text-white" : "text-gray-500",
                    day.isToday && "text-gold font-bold"
                  )}>
                    {day.date.getDate()}
                  </span>

                  {day.totalAmount > 0 && (
                    <span className="text-xs text-gold font-medium">
                      €{(day.totalAmount / 1000).toFixed(1)}k
                    </span>
                  )}
                </div>

                {/* Lista spese del giorno */}
                <div className="space-y-1 max-h-20 overflow-y-auto">
                  {day.expenses.slice(0, 3).map(expense => (
                    <motion.div
                      key={expense.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={cn(
                        "text-xs p-1 rounded border-l-2 cursor-pointer",
                        "hover:bg-white/10 transition-colors",
                        expense.is_overdue
                          ? "bg-gray-500/20 border-gray-500 text-gray-300"
                          : expense.status === 'paid'
                          ? "bg-gold/20 border-gold text-gold"
                          : "bg-white/10 border-gold text-white",
                        CATEGORIES_COLORS[expense.category as keyof typeof CATEGORIES_COLORS] &&
                          `border-l-2`
                      )}
                      onClick={(e) => {
                        e.stopPropagation();
                        onExpenseClick?.(expense);
                      }}
                    >
                      <div className="font-medium truncate">
                        {expense.title}
                      </div>
                      <div className="flex items-center justify-between">
                        <span>€{expense.amount.toLocaleString()}</span>
                        <Badge
                          variant={expense.status === 'paid' ? 'default' : 'secondary'}
                          className="text-xs px-1 py-0"
                        >
                          {expense.status === 'paid' ? '✓' :
                           expense.is_overdue ? '!' : '⏳'}
                        </Badge>
                      </div>
                    </motion.div>
                  ))}

                  {day.expenses.length > 3 && (
                    <div className="text-xs text-gray-400 text-center py-1">
                      +{day.expenses.length - 3} altre
                    </div>
                  )}
                </div>

                {/* Add button on hover */}
                {day.isCurrentMonth && (
                  <motion.button
                    initial={{ opacity: 0 }}
                    whileHover={{ opacity: 1 }}
                    className="absolute bottom-1 right-1 w-5 h-5 bg-gold hover:bg-gold/90 text-black rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAddExpense(day.date);
                    }}
                  >
                    <Plus className="h-3 w-3" />
                  </motion.button>
                )}
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Selected Date Details Modal */}
      <AnimatePresence>
        {selectedDate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setSelectedDate(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-[#0A0A0A] border border-white/10 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">
                  {selectedDate.toLocaleDateString('it', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedDate(null)}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Lista spese del giorno selezionato */}
              <div className="space-y-3">
                {calendarDays
                  .find(day => day.date.toDateString() === selectedDate.toDateString())
                  ?.expenses.map(expense => (
                    <div
                      key={expense.id}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10"
                    >
                      <div className="flex-1">
                        <h4 className="font-medium text-white">{expense.title}</h4>
                        <p className="text-sm text-gray-400">
                          {expense.category} • {expense.supplier_name}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-white">
                          €{expense.amount.toLocaleString()}
                        </p>
                        <Badge
                          variant={
                            expense.status === 'paid' ? 'default' :
                            expense.is_overdue ? 'destructive' : 'secondary'
                          }
                        >
                          {expense.status === 'paid' ? 'Pagata' :
                           expense.is_overdue ? 'Scaduta' : 'Da pagare'}
                        </Badge>
                      </div>
                    </div>
                  )) || (
                    <p className="text-center text-gray-400 py-8">
                      Nessuna spesa programmata per questo giorno
                    </p>
                  )}
              </div>

              {/* Azioni */}
              <div className="flex gap-3 mt-6">
                <Button
                  className="flex-1 bg-gold hover:bg-gold/90 text-black"
                  onClick={() => handleAddExpense(selectedDate)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Aggiungi Spesa
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setSelectedDate(null)}
                >
                  Chiudi
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
