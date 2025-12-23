import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export interface Subscriber {
    id: number;
    email: string;
    source: string;
    status: string;
    created_at: string;
}

const API_URL = '/api/v1/newsletter';

// Subscribe (Public)
export const useSubscribe = () => {
    return useMutation({
        mutationFn: async (data: { email: string; source?: string }) => {
            const response = await axios.post(`${API_URL}/subscribe`, data);
            return response.data;
        },
    });
};

// List Subscribers (Admin)
export const useNewsletterSubscribers = () => {
    return useQuery<Subscriber[]>({
        queryKey: ['newsletter-subscribers'],
        queryFn: async () => {
            const response = await axios.get(`${API_URL}/subscribers`);
            return response.data;
        },
    });
};
