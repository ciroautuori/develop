/**
 * Portfolio Management Component
 * Admin panel per gestire servizi e progetti
 * LIGHT MODE SUPPORT
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit, Trash2, Eye, EyeOff } from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { Badge } from '../../../shared/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../../shared/components/ui/table';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';

interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
  is_active: boolean;
  is_featured: boolean;
  order: number;
}

export function PortfolioManagement() {
  const [activeTab, setActiveTab] = useState<'services' | 'projects'>('services');
  const queryClient = useQueryClient();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Dynamic classes
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const borderColor = isDark ? 'border-white/10' : 'border-gray-200';

  // Fetch services
  const { data: services, isLoading } = useQuery({
    queryKey: ['admin-services'],
    queryFn: async () => {
      const response = await fetch('/api/v1/portfolio/admin/services', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch services');
      return response.json();
    }
  });

  // Delete service mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`/api/v1/portfolio/admin/services/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to delete service');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-services'] });
      toast.success('Servizio eliminato con successo');
    },
    onError: () => {
      toast.error('Errore durante l\'eliminazione');
    }
  });

  const handleDelete = (id: number, title: string) => {
    if (confirm(`Sei sicuro di voler eliminare "${title}"?`)) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-gold border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className={textSecondary}>Caricamento...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className={`text-3xl font-bold ${textPrimary}`}>Gestione Portfolio</h1>
          <p className={textSecondary}>Gestisci servizi e progetti del portfolio</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Nuovo Servizio
        </Button>
      </div>

      {/* Tabs */}
      <div className={`border-b ${borderColor}`}>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('services')}
            className={`px-4 py-2 border-b-2 transition ${
              activeTab === 'services'
                ? 'border-gold text-gold'
                : `border-transparent ${textSecondary} hover:${textPrimary}`
            }`}
          >
            Servizi ({services?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('projects')}
            className={`px-4 py-2 border-b-2 transition ${
              activeTab === 'projects'
                ? 'border-gold text-gold'
                : `border-transparent ${textSecondary} hover:${textPrimary}`
            }`}
          >
            Progetti
          </button>
        </div>
      </div>

      {/* Services Table */}
      {activeTab === 'services' && (
        <div className={`border rounded-lg ${borderColor}`}>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">Icona</TableHead>
                <TableHead>Titolo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Stato</TableHead>
                <TableHead className="w-20">Ordine</TableHead>
                <TableHead className="w-32 text-right">Azioni</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {services?.map((service: Service) => (
                <TableRow key={service.id}>
                  <TableCell className="text-2xl">{service.icon}</TableCell>
                  <TableCell>
                    <div>
                      <div className={`font-medium ${textPrimary}`}>{service.title}</div>
                      <div className={`text-sm ${textSecondary}`}>{service.slug}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{service.category}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      {service.is_active ? (
                        <Badge variant="default" className="bg-gold">
                          <Eye className="mr-1 h-3 w-3" />
                          Attivo
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <EyeOff className="mr-1 h-3 w-3" />
                          Disattivo
                        </Badge>
                      )}
                      {service.is_featured && (
                        <Badge variant="default" className="bg-gold">
                          ⭐ Featured
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{service.order}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end">
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(service.id, service.title)}
                      >
                        <Trash2 className="h-4 w-4 text-gray-400" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Projects placeholder */}
      {activeTab === 'projects' && (
        <div className={`text-center py-12 ${textSecondary}`}>
          Gestione progetti - Coming soon
        </div>
      )}
    </div>
  );
}
