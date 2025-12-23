/**
 * Courses Admin Hooks - React Query hooks for courses management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = '/api/v1/admin/courses';

const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('admin_token')}`
});

// ============================================================================
// COURSES HOOKS
// ============================================================================

export function useCourses(page = 1, filters = {}) {
    return useQuery({
        queryKey: ['admin-courses', page, filters],
        queryFn: async () => {
            try {
                const { data } = await axios.get(API_URL, {
                    params: { page, page_size: 20, ...filters },
                    headers: getAuthHeaders()
                });
                return data;
            } catch (error: any) {
                if (error.response?.status === 401) {
                    localStorage.removeItem('admin_token');
                    window.location.href = '/admin/login';
                }
                throw error;
            }
        }
    });
}

export function useCourse(id: number) {
    return useQuery({
        queryKey: ['admin-course', id],
        queryFn: async () => {
            const { data } = await axios.get(`${API_URL}/${id}`, {
                headers: getAuthHeaders()
            });
            return data;
        },
        enabled: !!id
    });
}

export function useCreateCourse() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (courseData: any) => {
            const { data } = await axios.post(API_URL, courseData, {
                headers: getAuthHeaders()
            });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-courses'] });
        }
    });
}

export function useUpdateCourse() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data: courseData }: { id: number; data: any }) => {
            const { data } = await axios.put(`${API_URL}/${id}`, courseData, {
                headers: getAuthHeaders()
            });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-courses'] });
            queryClient.invalidateQueries({ queryKey: ['admin-course'] });
        }
    });
}

export function useDeleteCourse() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (id: number) => {
            await axios.delete(`${API_URL}/${id}`, {
                headers: getAuthHeaders()
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-courses'] });
        }
    });
}

export function useBulkUpdateCourseOrder() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (items: Array<{ id: number; order: number }>) => {
            await axios.post(`${API_URL}/bulk/order`, items, {
                headers: getAuthHeaders()
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-courses'] });
        }
    });
}
