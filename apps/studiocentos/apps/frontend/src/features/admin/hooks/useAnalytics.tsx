/**
 * Analytics Hooks - React Query hooks for analytics data
 */
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { API_ENDPOINTS, STORAGE_KEYS } from '../../../shared/config/constants';

const API_URL = API_ENDPOINTS.admin.analytics;

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem(STORAGE_KEYS.adminToken)}`
});

export function useAnalyticsOverview(days = 30) {
  return useQuery({
    queryKey: ['analytics-overview', days],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/overview`, {
        params: { days },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useProjectAnalytics(projectId: number, days = 30) {
  return useQuery({
    queryKey: ['analytics-project', projectId, days],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/projects/${projectId}`, {
        params: { days },
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!projectId
  });
}

export function useServiceAnalytics(serviceId: number, days = 30) {
  return useQuery({
    queryKey: ['analytics-service', serviceId, days],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/services/${serviceId}`, {
        params: { days },
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!serviceId
  });
}

export function useTrafficAnalytics(days = 30) {
  return useQuery({
    queryKey: ['analytics-traffic', days],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/traffic`, {
        params: { days },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useTopProjects(days = 30, limit = 10) {
  return useQuery({
    queryKey: ['analytics-top-projects', days, limit],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/top-projects`, {
        params: { days, limit },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useTopServices(days = 30, limit = 10) {
  return useQuery({
    queryKey: ['analytics-top-services', days, limit],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/top-services`, {
        params: { days, limit },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}
