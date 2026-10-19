export interface Invoice {
  id: number;
  invoice_number?: string;
  patient?: number;
  status: string;
  total_amount?: number | string;
  amount_due?: number | string;
  currency?: string;
  due_date?: string;
  paid_at?: string;
  created_at?: string;
  notes?: string;
}

export interface Payment {
  id: number;
  invoice?: number;
  amount: number | string;
  method?: string;
  status: string;
  reference?: string;
  created_at?: string;
}

export interface InsuranceClaim {
  id: number;
  claim_number?: string;
  status: string;
  amount_claimed?: number | string;
  amount_approved?: number | string;
  created_at?: string;
}

export interface BillingFilters {
  search?: string;
  status?: string;
  page?: number;
  page_size?: number;
}
