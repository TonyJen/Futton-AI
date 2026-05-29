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
  WorkCenter, Agent, AgentRecommendation, KpiData,
  InventoryDistributionEntry, ProductionTrendEntry, WorkCenterUtilizationEntry,
} from './types';

import * as mock from './mockData';

// ============================================
// Configuration
// ============================================
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = false; // Set to true only if you want to run completely offline (no real LLM)

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

function pick<T>(value: T | undefined, fallback: T | undefined): T | undefined {
  return value ?? fallback;
}

function normalizeCustomer(customer: any) {
  return {
    ...customer,
    customerId: pick(customer.customerId, customer.CustomerID),
    customerCode: pick(customer.customerCode, customer.CustomerCode),
    customerName: pick(customer.customerName, customer.CustomerName),
    customerType: pick(customer.customerType, customer.CustomerType),
    email: pick(customer.email, customer.Email),
    phone: pick(customer.phone, customer.Phone),
    city: pick(customer.city, customer.City),
    state: pick(customer.state, customer.State),
    country: pick(customer.country, customer.Country),
  };
}

function normalizeSalesRep(rep: any) {
  const firstName = pick(rep.firstName, rep.FirstName);
  const lastName = pick(rep.lastName, rep.LastName);
  return {
    ...rep,
    salesRepId: pick(rep.salesRepId, rep.SalesRepID),
    fullName: pick(rep.fullName, [firstName, lastName].filter(Boolean).join(' ')),
    email: pick(rep.email, rep.Email),
    territory: pick(rep.territory, rep.Territory),
    ytdSales: pick(rep.ytdSales, rep.YTDSales) ?? 0,
    commissionRate: pick(rep.commissionRate, rep.CommissionRate) ?? 0,
  };
}

function normalizeSalesDetail(detail: any) {
  return {
    ...detail,
    quoteDetailId: pick(detail.quoteDetailId, detail.QuoteDetailID),
    soDetailId: pick(detail.soDetailId, detail.SODetailID),
    salesOrderDetailId: pick(detail.salesOrderDetailId, detail.SODetailID),
    itemId: pick(detail.itemId, detail.ItemID),
    itemCode: pick(detail.itemCode, detail.ItemCode),
    itemName: pick(detail.itemName, detail.ItemName),
    quantity: pick(detail.quantity, detail.Quantity),
    unitPrice: pick(detail.unitPrice, detail.UnitPrice),
    lineTotal: pick(detail.lineTotal, detail.LineTotal),
    discountPercent: pick(detail.discountPercent, detail.DiscountPercent) ?? 0,
  };
}

function normalizeQuote(quote: any) {
  return {
    ...quote,
    quoteId: pick(quote.quoteId, quote.QuoteID),
    quoteNumber: pick(quote.quoteNumber, quote.QuoteNumber),
    customerId: pick(quote.customerId, quote.CustomerID),
    customerName: pick(quote.customerName, quote.CustomerName),
    salesRepId: pick(quote.salesRepId, quote.SalesRepID),
    quoteDate: pick(quote.quoteDate, quote.QuoteDate),
    expirationDate: pick(quote.expirationDate, quote.ExpirationDate),
    status: pick(quote.status, quote.Status),
    subtotal: pick(quote.subtotal, quote.Subtotal),
    discountAmount: pick(quote.discountAmount, quote.DiscountAmount) ?? 0,
    taxAmount: pick(quote.taxAmount, quote.TaxAmount) ?? 0,
    shippingAmount: pick(quote.shippingAmount, quote.ShippingAmount) ?? 0,
    totalAmount: pick(quote.totalAmount, quote.TotalAmount),
    convertedToOrderId: pick(quote.convertedToOrderId, quote.ConvertedToOrderID),
    details: Array.isArray(quote.details) ? quote.details.map(normalizeSalesDetail) : quote.details,
  };
}

function normalizeSalesOrder(order: any) {
  return {
    ...order,
    salesOrderId: pick(order.salesOrderId, order.SalesOrderID),
    orderId: pick(order.orderId, order.SalesOrderID),
    orderNumber: pick(order.orderNumber, order.OrderNumber),
    customerId: pick(order.customerId, order.CustomerID),
    customerName: pick(order.customerName, order.CustomerName),
    orderDate: pick(order.orderDate, order.OrderDate),
    dueDate: pick(order.dueDate, order.RequestedDeliveryDate),
    status: pick(order.status, order.Status),
    totalAmount: pick(order.totalAmount, order.TotalAmount),
    details: Array.isArray(order.details) ? order.details.map(normalizeSalesDetail) : order.details,
  };
}

function normalizeReturn(ret: any) {
  return {
    ...ret,
    returnId: pick(ret.returnId, ret.ReturnID),
    returnNumber: pick(ret.returnNumber, ret.ReturnNumber),
    salesOrderId: pick(ret.salesOrderId, ret.SalesOrderID),
    customerId: pick(ret.customerId, ret.CustomerID),
    customerName: pick(ret.customerName, ret.CustomerName),
    orderNumber: pick(ret.orderNumber, ret.OrderNumber),
    returnDate: pick(ret.returnDate, ret.ReturnDate),
    status: pick(ret.status, ret.Status),
    refundAmount: pick(ret.refundAmount, ret.RefundAmount) ?? 0,
    restockingFee: pick(ret.restockingFee, ret.RestockingFee) ?? 0,
    notes: pick(ret.notes, ret.Notes),
  };
}

function normalizeSupplier(supplier: any) {
  return {
    ...supplier,
    supplierId: pick(supplier.supplierId, supplier.SupplierID),
    supplierCode: pick(supplier.supplierCode, supplier.SupplierCode),
    supplierName: pick(supplier.supplierName, supplier.SupplierName),
    email: pick(supplier.email, supplier.Email),
    phone: pick(supplier.phone, supplier.Phone),
    city: pick(supplier.city, supplier.City),
    state: pick(supplier.state, supplier.State),
    country: pick(supplier.country, supplier.Country),
  };
}

function normalizePurchaseOrderDetail(detail: any) {
  return {
    ...detail,
    poDetailId: pick(detail.poDetailId, detail.PODetailID),
    itemId: pick(detail.itemId, detail.ItemID),
    itemCode: pick(detail.itemCode, detail.ItemCode),
    itemName: pick(detail.itemName, detail.ItemName),
    quantity: pick(detail.quantity, detail.Quantity),
    unitPrice: pick(detail.unitPrice, detail.UnitPrice),
    quantityReceived: pick(detail.quantityReceived, detail.QuantityReceived) ?? 0,
    lineTotal: pick(detail.lineTotal, detail.LineTotal),
  };
}

function normalizePurchaseOrder(po: any) {
  return {
    ...po,
    poId: pick(po.poId, po.PurchaseOrderID),
    poNumber: pick(po.poNumber, po.PONumber),
    supplierId: pick(po.supplierId, po.SupplierID),
    supplierName: pick(po.supplierName, po.SupplierName),
    warehouseId: pick(po.warehouseId, po.WarehouseID),
    orderDate: pick(po.orderDate, po.OrderDate),
    expectedDeliveryDate: pick(po.expectedDeliveryDate, po.ExpectedDeliveryDate),
    status: pick(po.status, po.Status),
    subtotal: pick(po.subtotal, po.Subtotal),
    taxAmount: pick(po.taxAmount, po.TaxAmount) ?? 0,
    shippingAmount: pick(po.shippingAmount, po.ShippingAmount) ?? 0,
    totalAmount: pick(po.totalAmount, po.TotalAmount),
    notes: pick(po.notes, po.Notes),
    details: Array.isArray(po.details) ? po.details.map(normalizePurchaseOrderDetail) : po.details,
  };
}

function toPascalPurchaseOrderPayload(payload: any) {
  return {
    SupplierID: payload.supplierId ?? payload.SupplierID,
    WarehouseID: payload.warehouseId ?? payload.WarehouseID ?? 1,
    OrderDate: payload.orderDate ?? payload.OrderDate,
    ExpectedDeliveryDate: payload.expectedDeliveryDate ?? payload.ExpectedDeliveryDate,
    Notes: payload.notes ?? payload.Notes,
    details: (payload.details ?? payload.Details ?? []).map((detail: any, index: number) => ({
      LineNumber: detail.lineNumber ?? detail.LineNumber ?? index + 1,
      ItemID: detail.itemId ?? detail.ItemID,
      Quantity: detail.quantity ?? detail.Quantity ?? detail.orderedQty ?? detail.OrderedQty,
      UnitPrice: detail.unitPrice ?? detail.UnitPrice ?? detail.unitCost ?? detail.UnitCost,
    })),
  };
}

function toPascalReceivePayload(payload: any) {
  return {
    received_by: payload.received_by ?? payload.receivedBy ?? 'UI User',
    notes: payload.notes ?? payload.Notes,
    lines: (payload.lines ?? payload.Lines ?? []).map((line: any) => ({
      PODetailID: line.poDetailId ?? line.PODetailID,
      QuantityReceived: line.quantityReceived ?? line.QuantityReceived,
    })),
  };
}

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
  const data = res.data;

  // Normalize backend rich BOMExplosionResult into the camelCase BOMComponent[] the UI components expect
  if (data && Array.isArray(data.Components)) {
    return data.Components.map((c: any) => ({
      bomId: 0,
      parentItemId: c.ParentItemID ?? c.parent_item_id ?? 0,
      componentItemId: c.ComponentItemID ?? c.component_item_id,
      componentItemCode: c.ComponentItemCode ?? c.component_item_code,
      componentItemName: c.ComponentItemName ?? c.component_item_name,
      quantity: c.TotalQuantityRequired ?? c.total_quantity_required ?? c.QuantityPerParent ?? c.quantity ?? 1,
      unit: c.UnitCode ?? c.unit_code ?? '',
      scrapRate: c.ScrapRate ?? c.scrap_rate ?? 0,
      level: c.Level ?? c.level ?? 0,
    }));
  }
  // Fallback: if backend already returned a flat array, pass it through
  return Array.isArray(data) ? data : [];
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

export async function runAgent(agentId: number): Promise<{
  proposals_created: number;
  reasoning_trace?: string[];
  agent_name?: string;
  status?: string;
}> {
  if (USE_MOCK) {
    await delay(1450);
    const result = mock.simulateAgentRun(agentId);
    return {
      proposals_created: result.newRecs?.length || 0,
      reasoning_trace: ["Mock agent completed analysis", "Generated recommendations based on current data"],
    };
  }

  const agentNameMap: Record<number, string> = {
    1: 'mrp',
    2: 'inventory',
    3: 'production_scheduler',
  };

  const agent_name = agentNameMap[agentId] || 'mrp';

  const res = await api.post('/agents/run', { agent_name, params: {} });
  return res.data;
}

export async function approveRecommendation(id: number): Promise<AgentRecommendation> {
  if (USE_MOCK) {
    await delay(380);
    const updated = mock.approveRecommendation(id);
    if (!updated) throw new Error('Recommendation not found');
    return updated;
  }
  // Correct backend path + required body
  const res = await api.post(`/agents/actions/${id}/approve`, {
    approved_by: "UI User",
    notes: "Approved from Agents Hub"
  });
  return res.data;
}

export async function rejectRecommendation(id: number): Promise<void> {
  if (USE_MOCK) {
    await delay(220);
    const ok = mock.rejectRecommendation(id);
    if (!ok) throw new Error('Recommendation not found');
    return;
  }
  // Correct backend path + required body
  await api.post(`/agents/actions/${id}/reject`, {
    rejected_by: "UI User",
    reason: "Rejected from Agents Hub"
  });
}

// ============================================
// DASHBOARD
// ============================================
export async function getDashboardKpis(): Promise<KpiData> {
  if (USE_MOCK) {
    await delay(160);
    // Compute live pending count
    const recs = mock.getLiveRecommendations();
    const pending = recs.filter(r => r.status === 'PENDING' || r.status === 'PROPOSED').length;
    return { ...mock.MOCK_KPIS, pendingRecommendations: pending };
  }
  const res = await api.get<KpiData>('/dashboard/kpis');
  return res.data;
}

export async function getInventoryDistribution(): Promise<InventoryDistributionEntry[]> {
  if (USE_MOCK) {
    await delay(190);
    return mock.CHART_INVENTORY_BY_TYPE;
  }
  const res = await api.get<InventoryDistributionEntry[]>('/dashboard/inventory-distribution');
  return res.data;
}

export async function getProductionTrend(): Promise<ProductionTrendEntry[]> {
  if (USE_MOCK) {
    await delay(150);
    return mock.CHART_PRODUCTION_TREND;
  }
  const res = await api.get<ProductionTrendEntry[]>('/dashboard/production-trend');
  return res.data;
}

export async function getWorkCenterUtilization(): Promise<WorkCenterUtilizationEntry[]> {
  if (USE_MOCK) {
    await delay(140);
    return mock.CHART_WORKCENTER_UTIL;
  }
  const res = await api.get<WorkCenterUtilizationEntry[]>('/dashboard/workcenter-utilization');
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
  return res.data.map(normalizeQuote);
}

export async function getQuote(quoteId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(180);
    return mock.getMockQuoteById(quoteId);
  }
  const res = await api.get(`/sales/quotes/${quoteId}`);
  return normalizeQuote(res.data);
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
  return normalizeQuote(res.data);
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
  return normalizeSalesOrder(res.data);
}

export async function updateQuoteStatus(quoteId: number, status: string): Promise<any> {
  if (USE_MOCK) {
    await delay(200);
    return { success: true, quoteId, newStatus: status };
  }
  const res = await api.patch(`/sales/quotes/${quoteId}/status`, { status });
  return normalizeQuote(res.data);
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
  return res.data.map(normalizeCustomer);
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
  return res.data.map(normalizeSalesOrder);
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
  return res.data.map(normalizeReturn);
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
  return normalizeReturn(res.data);
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
  return res.data.map(normalizeSalesRep);
}

// ============================================
// AI SUPERVISOR (LLM-powered chat)
// ============================================

export async function chatWithSupervisor(messages: Array<{ role: string; text: string }>): Promise<{ response: string; suggested_agent?: string }> {
  // Always hit the real LLM backend for the AI Supervisor
  const res = await api.post('/agents/supervisor/chat', { messages });
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
  return res.data.map(normalizeSupplier);
}

export async function getPurchaseOrders(status?: string): Promise<any[]> {
  if (USE_MOCK) {
    await delay(180);
    let pos = mock.getMockPurchaseOrders();
    if (status && status !== 'All') pos = pos.filter((p: any) => p.status === status);
    return pos;
  }
  const res = await api.get('/purchasing/purchase-orders', { params: { status } });
  return res.data.map(normalizePurchaseOrder);
}

export async function getPurchaseOrder(poId: number): Promise<any> {
  if (USE_MOCK) {
    await delay(140);
    return mock.getMockPurchaseOrderById(poId);
  }
  const res = await api.get(`/purchasing/purchase-orders/${poId}`);
  return normalizePurchaseOrder(res.data);
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
  const res = await api.post('/purchasing/purchase-orders', toPascalPurchaseOrderPayload(payload));
  return normalizePurchaseOrder(res.data);
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
  const res = await api.post(`/purchasing/purchase-orders/${poId}/receive`, toPascalReceivePayload(payload));
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
