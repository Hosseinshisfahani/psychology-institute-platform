import React from 'react';
import { CacheProvider } from '@emotion/react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import createRtlCache from '../theme/rtlCache';

const theme = createTheme({ 
  direction: 'rtl',
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      'Vazir',
      'Samim', 
      'Shabnam',
      'Tahoma',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

const cache = createRtlCache();

interface MUIProviderProps {
  children: React.ReactNode;
}

export default function MUIProvider({ children }: MUIProviderProps) {
  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
