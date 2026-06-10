/**
 * FinPilot — API Client
 * Centralized API wrapper for all backend calls.
 */
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 60000, // LLM calls can be slow
  headers: { 'Content-Type': 'application/json' },
});

// ── Copilot Chat ────────────────────────────────────────────────
export const copilotChat = (query, profile = null) =>
  API.post('/copilot/chat', { query, profile });

// ── Boardroom ───────────────────────────────────────────────────
export const runBoardroom = (scenario, question) =>
  API.post('/boardroom/run', { scenario, question });

export const runSmartBoardroom = (scenario, question) =>
  API.post('/boardroom/smart', { scenario, question });

// ── Cash Flow ───────────────────────────────────────────────────
export const getCashFlowData = () => API.get('/cashflow/data');
export const getTransactions = () => API.get('/cashflow/transactions');
export const getHealthScore = () => API.get('/cashflow/health');

// ── Decision Simulator ─────────────────────────────────────────
export const runSimulator = (params) =>
  API.post('/simulator/run', params);

// ── Spending ────────────────────────────────────────────────────
export const getSpendingSummary = () => API.get('/spending/summary');
export const predictSpending = (params) =>
  API.post('/spending/predict', params);

// ── Health ──────────────────────────────────────────────────────
export const healthCheck = () => API.get('/health');

// ── Bill Scanner ────────────────────────────────────────────────
export const scanBill = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return API.post('/bills/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000, // OCR can take time
  });
};
export const listBills = (search = '', category = '') =>
  API.get('/bills/list', { params: { search, category } });
export const getBillMetrics = () => API.get('/bills/metrics');
export const deleteBill = (billId) => API.delete(`/bills/${billId}`);

export default API;
