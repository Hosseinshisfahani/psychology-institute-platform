declare module 'notistack' {
  export interface OptionsObject {
    variant?: 'default' | 'error' | 'success' | 'warning' | 'info';
    autoHideDuration?: number;
  }

  export interface ProviderContext {
    enqueueSnackbar: (message: string, options?: OptionsObject) => void;
    closeSnackbar: (key?: string | number) => void;
  }

  export function useSnackbar(): ProviderContext;

  export interface SnackbarProviderProps {
    children?: React.ReactNode;
    maxSnack?: number;
    anchorOrigin?: {
      vertical: 'top' | 'bottom';
      horizontal: 'left' | 'center' | 'right';
    };
  }

  export const SnackbarProvider: React.FC<SnackbarProviderProps>;
}

