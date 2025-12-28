import axios from 'axios';

export interface Wallet {
  id: number;
  balance: string;
  created_at: string;
  updated_at: string;
}

export interface WalletTransaction {
  id: number;
  transaction_type: 'refund' | 'purchase' | 'admin_adjustment';
  transaction_type_display: string;
  amount: string;
  balance_after: string;
  reference_id?: number;
  description: string;
  created_at: string;
}

export interface WalletBalanceResponse {
  id: number;
  balance: string;
  created_at: string;
  updated_at: string;
}

export interface WalletTransactionsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: WalletTransaction[];
}

/**
 * Get current wallet balance
 */
export const getWalletBalance = async (): Promise<WalletBalanceResponse> => {
  const response = await axios.get<WalletBalanceResponse>('/api/payment/wallet/balance/');
  return response.data;
};

/**
 * Get wallet transaction history
 */
export const getWalletTransactions = async (
  page: number = 1,
  transactionType?: 'refund' | 'purchase' | 'admin_adjustment'
): Promise<WalletTransactionsResponse> => {
  const params: any = { page };
  if (transactionType) {
    params.transaction_type = transactionType;
  }
  const response = await axios.get<WalletTransactionsResponse>('/api/payment/wallet/transactions/', { params });
  return response.data;
};

/**
 * Use wallet credits for a purchase
 */
export const useWalletCredits = async (
  amount: number,
  orderId?: number
): Promise<{
  success: boolean;
  message: string;
  amount_used: string;
  remaining_balance: string;
  wallet: WalletBalanceResponse;
}> => {
  const response = await axios.post('/api/payment/wallet/use/', {
    amount,
    order_id: orderId,
  });
  return response.data;
};

