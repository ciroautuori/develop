
export const getAdminToken = () => {
    return localStorage.getItem('admin_token');
};

export const setAdminToken = (token: string) => {
    localStorage.setItem('admin_token', token);
};

export const removeAdminToken = () => {
    localStorage.removeItem('admin_token');
};
