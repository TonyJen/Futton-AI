/**
 * Funton AI - Typed API Client
 * 
 * Ready for FastAPI backend.
 * Currently backed by high-fidelity mocks with network simulation.
 * 
 * When backend is ready:
 *   1. Set VITE_API_URL in .env
 *   2. Replace mock implementations with axios/fetch calls
 *   3. Keep the same public interface
 */
import axios from 'axios';
import {
  Item, InventoryRecord, InventoryTransaction, ProductionOrder,
  WorkCenter, Agent, AgentRecommendation, KpiData
} from './types';

import * as mock from './mockData';

// ============================================
// Configuration
// ============================================
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = true; // Flip to false once real backend is live

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Simple delay helper to simulate network
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// ============================================
// ITEMS
// ============================================
export async function getItems(params?: { search?: string; type?: string }): Promise<Item[]> {
  if (USE_MOCK) {
    await delay(220);
    let items = [...mock.MOCK_ITEMS];
    
    if (params?.search) {
      const q = params.search.toLowerCase();
      items = items.filter(i =>
        i.itemCode.toLowerCase().includes(q) ||
        i.itemName.toLowerCase().includes(q)
      );
    }
    if (params?.type && params.type !== 'All') {
      items = items.filter(i => i.itemType === params.type);
    }
    return items;
  }
  
  const res = await api.get<Item[]>('/items', { params });
  return res.data;
}

export async function getItemBOM(itemId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(180);
    return mock.getBOMForItem(itemId);
  }
  const res = await api.get(`/items/${itemId}/bom`);
  return res.data;
}

// ============================================
// INVENTORY
// ============================================
export async function getInventory(warehouse?: string): Promise<InventoryRecord[]> {
  if (USE_MOCK) {
    await delay(260);
    let data = [...mock.getLiveInventory()];
    if (warehouse && warehouse !== 'All') {
      data = data.filter(i => i.warehouseName === warehouse);
    }
    return data;
  }
  const res = await api.get<InventoryRecord[]>('/inventory', { params: { warehouse } });
  return res.data;
}

export async function getInventoryTransactions(itemId?: number): Promise<InventoryTransaction[]> {
  if (USE_MOCK) {
    await delay(190);
    let txns = [...mock.MOCK_TRANSACTIONS];
    if (itemId) txns = txns.filter(t => t.itemId === itemId);
    return txns.sort((a, b) => b.transactionDate.localeCompare(a.transactionDate));
  }
  const res = await api.get<InventoryTransaction[]>('/inventory/transactions', { params: { itemId } });
  return res.data;
}

// ============================================
// PRODUCTION
// ============================================
export async function getProductionOrders(status?: string): Promise<ProductionOrder[]> {
  if (USE_MOCK) {
    await delay(210);
    let orders = [...mock.getLiveProductionOrders()];
    if (status && status !== 'All') {
      orders = orders.filter(o => o.status === status);
    }
    return orders;
  }
  const res = await api.get<ProductionOrder[]>('/production/orders', { params: { status } });
  return res.data;
}

export async function getWorkCenters(): Promise<WorkCenter[]> {
  if (USE_MOCK) {
    await delay(140);
    return [...mock.MOCK_WORK_CENTERS];
  }
  const res = await api.get<WorkCenter[]>('/production/workcenters');
  return res.data;
}

// ============================================
// AGENTS + RECOMMENDATIONS (AI HUB)
// ============================================
export async function getAgents(): Promise<Agent[]> {
  if (USE_MOCK) {
    await delay(130);
    return [...mock.MOCK_AGENTS];
  }
  const res = await api.get<Agent[]>('/agents');
  return res.data;
}

export async function getRecommendations(status?: string): Promise<AgentRecommendation[]> {
  if (USE_MOCK) {
    await delay(170);
    let recs = [...mock.getLiveRecommendations()];
    if (status) recs = recs.filter(r => r.status === status);
    return recs;
  }
  const res = await api.get<AgentRecommendation[]>('/agents/recommendations', { params: { status } });
  return res.data;
}

export async function runAgent(agentId: number): Promise<{ recommendations: AgentRecommendation[] }> {
  if (USE_MOCK) {
    await delay(1450); // Simulate serious thinking time
    const result = mock.simulateAgentRun(agentId);
    return { recommendations: result.newRecs };
  }
  const res = await api.post(`/agents/${agentId}/run`);
  return res.data;
}

export async function approveRecommendation(id: number): Promise<AgentRecommendation> {
  if (USE_MOCK) {
    await delay(380);
    const updated = mock.approveRecommendation(id);
    if (!updated) throw new Error('Recommendation not found');
    return updated;
  }
  const res = await api.post(`/agents/recommendations/${id}/approve`);
  return res.data;
}

export async function rejectRecommendation(id: number): Promise<void> {
  if (USE_MOCK) {
    await delay(220);
    const ok = mock.rejectRecommendation(id);
    if (!ok) throw new Error('Recommendation not found');
    return;
  }
  await api.post(`/agents/recommendations/${id}/reject`);
}

// ============================================
// DASHBOARD
// ============================================
export async function getDashboardKpis(): Promise<KpiData> {
  if (USE_MOCK) {
    await delay(160);
    // Compute live pending count
    const recs = mock.getLiveRecommendations();
    const pending = recs.filter(r => r.status === 'PENDING').length;
    return { ...mock.MOCK_KPIS, pendingRecommendations: pending };
  }
  const res = await api.get<KpiData>('/dashboard/kpis');
  return res.data;
}

export async function getInventoryDistribution() {
  if (USE_MOCK) {
    await delay(190);
    return mock.CHART_INVENTORY_BY_TYPE;
  }
  const res = await api.get('/dashboard/inventory-distribution');
  return res.data;
}

export async function getProductionTrend() {
  if (USE_MOCK) {
    await delay(150);
    return mock.CHART_PRODUCTION_TREND;
  }
  const res = await api.get('/dashboard/production-trend');
  return res.data;
}

export async function getWorkCenterUtilization() {
  if (USE_MOCK) {
    await delay(140);
    return mock.CHART_WORKCENTER_UTIL;
  }
  const res = await api.get('/dashboard/workcenter-utilization');
  return res.data;
}

// ============================================
// SALES (light for Phase 1)
// ============================================
export async function getSalesSummary() {
  if (USE_MOCK) {
    await delay(210);
    return {
      totalRevenueMTD: 847650,
      ordersMTD: 184,
      avgOrderValue: 4607,
      openQuotes: 27,
    };
  }
  const res = await api.get('/sales/summary');
  return res.data;
}

// ============================================
// QUOTES (Phase 2)
// ============================================

export async function getQuotes(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(240);
    return mock.getMockQuotes();
  }
  const res = await api.get('/sales/quotes');
  return res.data;
}

export async function getQuote(quoteId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(180);
    return mock.getMockQuoteById(quoteId);
  }
  const res = await api.get(`/sales/quotes/${quoteId}`);
  return res.data;
}

export async function createQuote(payload: any): Promise<any> {
  if (USE_MOCK) {
    await delay(350);
    // Simulate creation
    const newQuote = {
      quoteId: Math.floor(Math.random() * 1000) + 10,
      quoteNumber: `QT-2026-${String(Math.floor(Math.random() * 9000) + 1000).padStart(4, '0')}`,
      ...payload,
      status: 'Draft',
      createdAt: new Date().toISOString(),
    };
    return newQuote;
  }
  const normalized = toPascalQuotePayload(payload);
  const res = await api.post('/sales/quotes', normalized);
  return res.data;
}

export async function convertQuoteToOrder(quoteId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(400);
    return {
      success: true,
      orderId: Math.floor(Math.random() * 100) + 50,
      orderNumber: `SO-2026-${String(Math.floor(Math.random() * 9000) + 1000).padStart(4, '0')}`,
      message: 'Quote successfully converted to Sales Order',
    };
  }
  const res = await api.post(`/sales/quotes/${quoteId}/convert`);
  return res.data;
}

export async function updateQuoteStatus(quoteId: number, status: string): Promise<any> {
  if (USE_MOCK) {
    await delay(200);
    return { success: true, quoteId, newStatus: status };
  }
  const res = await api.patch(`/sales/quotes/${quoteId}/status`, { status });
  return res.data;
}

// ============================================
// CUSTOMERS (for Quote/Return pickers)
// ============================================
export async function getCustomers(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(160);
    return mock.getMockCustomers();
  }
  const res = await api.get('/sales/customers');
  return res.data;
}

// ============================================
// SALES ORDERS (Phase 2 full)
// ============================================
export async function getSalesOrders(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(210);
    return mock.getMockSalesOrders();
  }
  const res = await api.get('/sales/orders');
  return res.data;
}

// ============================================
// RETURNS (Phase 2)
// ============================================
export async function getReturns(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(190);
    return mock.getMockReturns();
  }
  const res = await api.get('/sales/returns');
  return res.data;
}

export async function createReturn(payload: any): Promise<any> {
  if (USE_MOCK) {
    await delay(320);
    return {
      returnId: Math.floor(Math.random() * 900) + 100,
      returnNumber: `RT-2026-${String(Math.floor(Math.random() * 9000) + 1000).padStart(4, '0')}`,
      ...payload,
      status: 'Pending',
      returnDate: new Date().toISOString().slice(0, 10),
    };
  }
  const res = await api.post('/sales/returns', payload);
  return res.data;
}

// ============================================
// SALES REPS (basic CRM)
// ============================================
export async function getSalesReps(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(130);
    return mock.getMockSalesReps();
  }
  const res = await api.get('/sales/reps'); // backend may expose later
  return res.data;
}

// ============================================
// PURCHASING (Phase 3)
// ============================================

export async function getSuppliers(): Promise<any[]> {
  if (USE_MOCK) {
    await delay(150);
    return mock.getMockSuppliers();
  }
  const res = await api.get('/purchasing/suppliers');
  return res.data;
}

export async function getPurchaseOrders(status?: string): Promise<any[]> {
  if (USE_MOCK) {
    await delay(180);
    let pos = mock.getMockPurchaseOrders();
    if (status && status !== 'All') pos = pos.filter((p: any) => p.status === status);
    return pos;
  }
  const res = await api.get('/purchasing/purchase-orders', { params: { status } });
  return res.data;
}

export async function getPurchaseOrder(poId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(140);
    return mock.getMockPurchaseOrderById(poId);
  }
  const res = await api.get(`/purchasing/purchase-orders/${poId}`);
  return res.data;
}

export async function createPurchaseOrder(payload: any): Promise<any> {
  if (USE_MOCK) {
    await delay(280);
    const newPo = {
      poId: Math.floor(Math.random() * 800) + 200,
      poNumber: `PO-2026-${String(Math.floor(Math.random() * 9000) + 1000).padStart(4, '0')}`,
      ...payload,
      status: 'Draft',
      orderDate: new Date().toISOString().slice(0, 10),
    };
    return newPo;
  }
  const res = await api.post('/purchasing/purchase-orders', payload);
  return res.data;
}

export async function receiveGoods(poId: number, payload: any): Promise<any> {
  if (USE_MOCK) {
    await delay(350);
    return {
      success: true,
      purchaseOrderId: poId,
      status: 'Partial',
      message: 'Goods received and inventory updated',
    };
  }
  const res = await api.post(`/purchasing/purchase-orders/${poId}/receive`, payload);
  return res.data;
}

// Helper: normalize camelCase UI payload -> PascalCase backend schema for quotes
function toPascalQuotePayload(p: any) {
  return {
    CustomerID: p.customerId ?? p.CustomerID,
    SalesChannelID: p.salesChannelId ?? p.SalesChannelID,
    SalesRepID: p.salesRepId ?? p.SalesRepID,
    ExpirationDate: p.expirationDate ?? p.ExpirationDate,
    Notes: p.notes ?? p.Notes,
    TaxAmount: p.taxAmount ?? p.TaxAmount ?? 0,
    ShippingAmount: p.shippingAmount ?? p.ShippingAmount ?? 0,
    DiscountAmount: p.discountAmount ?? p.DiscountAmount ?? 0,
    details: (p.details || p.Details || []).map((d: any) => ({
      ItemID: d.itemId ?? d.ItemID,
      Quantity: d.quantity ?? d.Quantity,
      UnitPrice: d.unitPrice ?? d.UnitPrice,
      DiscountPercent: d.discountPercent ?? d.DiscountPercent ?? 0,
    })),
  };
}

// ============================================
// UTILITY - easy switch helper
// ============================================
export function isUsingMockData(): boolean {
  return USE_MOCK;
}

export const apiBaseUrl = API_BASE;
