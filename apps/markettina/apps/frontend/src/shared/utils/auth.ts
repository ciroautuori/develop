import { STORAGE_KEYS } from '../config/constants';

/**
 * Get admin token from local storage
 */
export const getAdminToken = (): string | null => {
  return localStorage.getItem(STORAGE_KEYS.adminToken);
};
