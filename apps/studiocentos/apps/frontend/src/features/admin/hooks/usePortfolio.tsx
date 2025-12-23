/**
 * Portfolio Admin Hooks - React Query hooks for portfolio management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = '/api/v1/admin/portfolio';

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem('admin_token')}`
});

// ============================================================================
// PROJECTS HOOKS
// ============================================================================

export function useProjects(page = 1, filters = {}) {
  return useQuery({
    queryKey: ['admin-projects', page, filters],
    queryFn: async () => {
      try {
        const { data } = await axios.get(`${API_URL}/projects`, {
          params: { page, page_size: 20, ...filters },
          headers: getAuthHeaders()
        });
        return data;
      } catch (error: any) {
        // Se 401, cancella token e redirect a login
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_email');
          window.location.href = '/admin/login';
        }
        throw error;
      }
    }
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: ['admin-project', id],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/projects/${id}`, {
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!id
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (projectData: any) => {
      const { data } = await axios.post(`${API_URL}/projects`, projectData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-projects'] });
    }
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data: projectData }: { id: number; data: any }) => {
      const { data } = await axios.put(`${API_URL}/projects/${id}`, projectData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-projects'] });
      queryClient.invalidateQueries({ queryKey: ['admin-project'] });
    }
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`${API_URL}/projects/${id}`, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-projects'] });
    }
  });
}

export function useBulkUpdateProjectOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (items: Array<{ id: number; order: number }>) => {
      await axios.post(`${API_URL}/projects/bulk/order`, { items }, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-projects'] });
    }
  });
}

export function useBulkToggleProjects() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ ids, field, value }: { ids: number[]; field: string; value: boolean }) => {
      await axios.post(`${API_URL}/projects/bulk/toggle`, { ids, field, value }, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-projects'] });
    }
  });
}

// ============================================================================
// SERVICES HOOKS
// ============================================================================

export function useServices(page = 1, filters = {}) {
  return useQuery({
    queryKey: ['admin-services', page, filters],
    queryFn: async () => {
      try {
        const { data } = await axios.get(`${API_URL}/services`, {
          params: { page, page_size: 20, ...filters },
          headers: getAuthHeaders()
        });
        return data;
      } catch (error: any) {
        // Se 401, cancella token e redirect a login
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_email');
          window.location.href = '/admin/login';
        }
        throw error;
      }
    }
  });
}

export function useService(id: number) {
  return useQuery({
    queryKey: ['admin-service', id],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/services/${id}`, {
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!id
  });
}

export function useCreateService() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (serviceData: any) => {
      const { data } = await axios.post(`${API_URL}/services`, serviceData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-services'] });
    }
  });
}

export function useUpdateService() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data: serviceData }: { id: number; data: any }) => {
      const { data } = await axios.put(`${API_URL}/services/${id}`, serviceData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-services'] });
      queryClient.invalidateQueries({ queryKey: ['admin-service'] });
    }
  });
}

export function useDeleteService() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`${API_URL}/services/${id}`, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-services'] });
    }
  });
}

export function useBulkToggleServices() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ ids, field, value }: { ids: number[]; field: string; value: boolean }) => {
      await axios.post(`${API_URL}/services/bulk/toggle`, { ids, field, value }, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-services'] });
    }
  });
}
