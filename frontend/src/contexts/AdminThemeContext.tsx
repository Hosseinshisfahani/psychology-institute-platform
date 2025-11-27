import React, { createContext, useContext, useState, useMemo, ReactNode } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import rtlPlugin from 'stylis-plugin-rtl';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { getAdminTheme } from '../theme/adminTheme';

interface AdminThemeContextType {
  mode: 'light' | 'dark';
  toggleTheme: () => void;
}

const AdminThemeContext = createContext<AdminThemeContextType>({
  mode: 'light',
  toggleTheme: () => {},
});

export const useAdminTheme = () => useContext(AdminThemeContext);

// Create RTL cache
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [rtlPlugin],
});

interface AdminThemeProviderProps {
  children: ReactNode;
}

export const AdminThemeProvider: React.FC<AdminThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = useMemo(() => getAdminTheme(mode), [mode]);

  const value = useMemo(
    () => ({
      mode,
      toggleTheme,
    }),
    [mode]
  );

  return (
    <AdminThemeContext.Provider value={value}>
      <CacheProvider value={cacheRtl}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </CacheProvider>
    </AdminThemeContext.Provider>
  );
};

