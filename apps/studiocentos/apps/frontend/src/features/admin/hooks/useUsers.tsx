/**
 * Users Admin Hooks - React Query hooks for user management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { API_ENDPOINTS, STORAGE_KEYS } from '../../../shared/config/constants';

const API_URL = API_ENDPOINTS.admin.users;

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem(STORAGE_KEYS.adminToken)}`
});

export function useUsers(page = 1, filters = {}) {
  return useQuery({
    queryKey: ['admin-users', page, filters],
    queryFn: async () => {
      const { data } = await axios.get(API_URL, {
        params: { page, page_size: 50, ...filters },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useUser(id: number) {
  return useQuery({
    queryKey: ['admin-user', id],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/${id}`, {
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!id
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data: userData }: { id: number; data: any }) => {
      const { data } = await axios.put(`${API_URL}/${id}`, userData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-user'] });
    }
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`${API_URL}/${id}`, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    }
  });
}

export function useActivateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await axios.post(`${API_URL}/${id}/activate`, {}, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    }
  });
}

export function useDeactivateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await axios.post(`${API_URL}/${id}/deactivate`, {}, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    }
  });
}

export function useChangeUserRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, role }: { id: number; role: string }) => {
      const { data } = await axios.post(`${API_URL}/${id}/change-role`, { role }, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    }
  });
}

export function useResetUserPassword() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, new_password }: { id: number; new_password: string }) => {
      const { data } = await axios.post(`${API_URL}/${id}/reset-password`, { new_password }, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    }
  });
}
