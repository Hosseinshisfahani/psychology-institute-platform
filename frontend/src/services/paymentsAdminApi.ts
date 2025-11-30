import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://185.8.175.241:8000';

// Reuse an axios instance configured for admin endpoints
// Note: CSRF token is handled by the global axios interceptor in AuthContext
const adminApi = axios.create({
  baseURL: `${API_BASE_URL}/api/admin`,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

export interface AdminPaymentsOverview {
  totalRevenue: number;
  totalOrders: number;
  completedPayments: number;
  failedPayments: number;
  refunds: number;
  methods: { name: string; count: number }[];
}

export interface RevenuePoint {
  date: string; // YYYY-MM-DD
  revenue: number;
}

export interface PaymentRow {
  id: number | string;
  orderNumber: string;
  amount: number;
  status: string;
  method: string;
  createdAt: string;
  item_types?: string[];  // List of item types (sections) in this order
}

// Temporary: use existing analytics endpoint to back some visuals until dedicated payments APIs exist
export const paymentsAdminApi = {
  async getOverview(itemType?: string): Promise<AdminPaymentsOverview> {
    const params: any = {};
    if (itemType) params.item_type = itemType;
    const { data } = await adminApi.get('/payments/overview/', { params });
    return {
      totalRevenue: Number(data.total_revenue || 0),
      totalOrders: Number(data.total_orders || 0),
      completedPayments: Number(data.completed_payments || 0),
      failedPayments: Number(data.failed_payments || 0),
      refunds: Number(data.refunds || 0),
      methods: Array.isArray(data.methods) ? data.methods : [],
    };
  },

  async getRevenueSeries(days: number = 30, itemType?: string): Promise<RevenuePoint[]> {
    const params: any = { days };
    if (itemType) params.item_type = itemType;
    const { data } = await adminApi.get('/payments/revenue-series/', { params });
    return (data as any[]).map((d) => ({ date: d.date, revenue: Number(d.revenue || 0) }));
  },

  async getRecentPayments(itemType?: string): Promise<PaymentRow[]> {
    const params: any = {};
    if (itemType) params.item_type = itemType;
    const { data } = await adminApi.get('/payments/recent/', { params });
    return (data as any[]).map((p) => ({
      id: p.id,
      orderNumber: p.order_number,
      amount: Number(p.amount || 0),
      status: p.status,
      method: p.method,
      createdAt: p.created_at,
      item_types: p.item_types || [],
    }));
  },
};

export default paymentsAdminApi;


