import { useAuth as useAuthContext } from '../auth/AuthContext';

// Re-export the useAuth hook from AuthContext for cleaner imports
export const useAuth = useAuthContext;