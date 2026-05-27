import { 
  Item, InventoryRecord, InventoryTransaction, ProductionOrder, 
  WorkCenter, Agent, AgentRecommendation, KpiData, BOMComponent 
} from './types';

// ============================================
// REALISTIC FUTON MANUFACTURING MOCK DATA
// ============================================

export const MOCK_ITEMS: Item[] = [
  { itemId: 1, itemCode: 'FG-001', itemName: 'Deluxe Futon Frame - Oak', itemType: 'Finished Good', unit: 'EA', description: 'Premium solid oak futon frame with 3-position adjustment', standardCost: 187.50, listPrice: 449.00, isActive: true, leadTimeDays: 5, reorderPoint: 12, safetyStock: 8 },
  { itemId: 2, itemCode: 'FG-002', itemName: 'Classic Futon Mattress - Queen', itemType: 'Finished Good', unit: 'EA', description: '8-inch innerspring futon mattress with cotton cover', standardCost: 142.00, listPrice: 329.00, isActive: true, leadTimeDays: 4, reorderPoint: 20, safetyStock: 15 },
  { itemId: 3, itemCode: 'FG-003', itemName: 'Linen Blend Futon Cover - Natural', itemType: 'Finished Good', unit: 'EA', description: 'Heavyweight 55% linen / 45% cotton cover', standardCost: 48.75, listPrice: 119.00, isActive: true, leadTimeDays: 3, reorderPoint: 35, safetyStock: 25 },
  { itemId: 4, itemCode: 'RM-010', itemName: 'Oak Lumber 4x4x96"', itemType: 'Raw Material', unit: 'EA', description: 'Select kiln-dried red oak, FAS grade', standardCost: 31.20, listPrice: 54.00, isActive: true, leadTimeDays: 12, reorderPoint: 65, safetyStock: 40 },
  { itemId: 5, itemCode: 'RM-011', itemName: 'Oak Lumber 1x6x96"', itemType: 'Raw Material', unit: 'EA', description: 'Select kiln-dried red oak boards', standardCost: 14.80, listPrice: 26.50, isActive: true, leadTimeDays: 10, reorderPoint: 110, safetyStock: 80 },
  { itemId: 6, itemCode: 'RM-020', itemName: 'High-Density Foam 3"', itemType: 'Raw Material', unit: 'SQYD', description: '2.5lb density polyurethane foam for cushions', standardCost: 8.95, listPrice: 15.75, isActive: true, leadTimeDays: 7, reorderPoint: 280, safetyStock: 180 },
  { itemId: 7, itemCode: 'RM-025', itemName: 'Cotton Batting 60"', itemType: 'Raw Material', unit: 'YD', description: 'Premium 8oz cotton batting for quilting', standardCost: 3.85, listPrice: 7.25, isActive: true, leadTimeDays: 5, reorderPoint: 420, safetyStock: 300 },
  { itemId: 8, itemCode: 'CM-030', itemName: 'Futon Hinge Mechanism - Heavy Duty', itemType: 'Component', unit: 'EA', description: '3-position locking hinge set (pair)', standardCost: 14.65, listPrice: 29.00, isActive: true, leadTimeDays: 8, reorderPoint: 55, safetyStock: 35 },
  { itemId: 9, itemCode: 'CM-031', itemName: 'Wood Dowel 1/2" x 3"', itemType: 'Component', unit: 'EA', description: 'Hardwood alignment dowels', standardCost: 0.18, listPrice: 0.45, isActive: true, leadTimeDays: 3, reorderPoint: 1200, safetyStock: 800 },
  { itemId: 10, itemCode: 'RM-040', itemName: 'Linen-Cotton Blend Fabric 54"', itemType: 'Raw Material', unit: 'YD', description: 'Natural undyed 10oz blend fabric', standardCost: 11.40, listPrice: 22.00, isActive: true, leadTimeDays: 14, reorderPoint: 175, safetyStock: 110 },
  { itemId: 11, itemCode: 'CM-050', itemName: '8" Innerspring Unit - Queen', itemType: 'Component', unit: 'EA', description: '390 coil count bonnell spring unit', standardCost: 67.25, listPrice: 118.00, isActive: true, leadTimeDays: 9, reorderPoint: 28, safetyStock: 18 },
  { itemId: 12, itemCode: 'PK-001', itemName: 'Corrugated Shipping Carton - Large', itemType: 'Packaging', unit: 'EA', description: 'Double-wall 48x28x12" carton', standardCost: 3.85, listPrice: 6.95, isActive: true, leadTimeDays: 4, reorderPoint: 190, safetyStock: 120 },
];

export const MOCK_BOM: Record<number, BOMComponent[]> = {
  // FG-001 Deluxe Futon Frame BOM (Level 0)
  1: [
    { bomId: 101, parentItemId: 1, componentItemId: 4, componentItemCode: 'RM-010', componentItemName: 'Oak Lumber 4x4x96"', quantity: 3, unit: 'EA', scrapRate: 8, level: 1 },
    { bomId: 102, parentItemId: 1, componentItemId: 5, componentItemCode: 'RM-011', componentItemName: 'Oak Lumber 1x6x96"', quantity: 5, unit: 'EA', scrapRate: 6, level: 1 },
    { bomId: 103, parentItemId: 1, componentItemId: 8, componentItemCode: 'CM-030', componentItemName: 'Futon Hinge Mechanism - Heavy Duty', quantity: 1, unit: 'EA', scrapRate: 0, level: 1 },
    { bomId: 104, parentItemId: 1, componentItemId: 9, componentItemCode: 'CM-031', componentItemName: 'Wood Dowel 1/2" x 3"', quantity: 24, unit: 'EA', scrapRate: 3, level: 1 },
  ],
  // FG-002 Classic Futon Mattress
  2: [
    { bomId: 201, parentItemId: 2, componentItemId: 11, componentItemCode: 'CM-050', componentItemName: '8" Innerspring Unit - Queen', quantity: 1, unit: 'EA', scrapRate: 0, level: 1 },
    { bomId: 202, parentItemId: 2, componentItemId: 6, componentItemCode: 'RM-020', componentItemName: 'High-Density Foam 3"', quantity: 4.5, unit: 'SQYD', scrapRate: 5, level: 1 },
    { bomId: 203, parentItemId: 2, componentItemId: 7, componentItemCode: 'RM-025', componentItemName: 'Cotton Batting 60"', quantity: 6, unit: 'YD', scrapRate: 4, level: 1 },
    { bomId: 204, parentItemId: 2, componentItemId: 10, componentItemCode: 'RM-040', componentItemName: 'Linen-Cotton Blend Fabric 54"', quantity: 4.2, unit: 'YD', scrapRate: 7, level: 1 },
  ],
  // FG-003 Cover
  3: [
    { bomId: 301, parentItemId: 3, componentItemId: 10, componentItemCode: 'RM-040', componentItemName: 'Linen-Cotton Blend Fabric 54"', quantity: 3.8, unit: 'YD', scrapRate: 9, level: 1 },
    { bomId: 302, parentItemId: 3, componentItemId: 7, componentItemCode: 'RM-025', componentItemName: 'Cotton Batting 60"', quantity: 2.5, unit: 'YD', scrapRate: 5, level: 1 },
  ],
};

export const MOCK_WAREHOUSES = ['Main Plant', 'East Warehouse', 'West Distribution', 'Finished Goods'] as const;

export const MOCK_INVENTORY: InventoryRecord[] = [
  // Main Plant
  { inventoryId: 1, itemId: 1, itemCode: 'FG-001', itemName: 'Deluxe Futon Frame - Oak', itemType: 'Finished Good', warehouseId: 1, warehouseName: 'Main Plant', quantityOnHand: 34, quantityAllocated: 9, available: 25, lastUpdated: '2026-05-25T08:14:00Z' },
  { inventoryId: 2, itemId: 4, itemCode: 'RM-010', itemName: 'Oak Lumber 4x4x96"', itemType: 'Raw Material', warehouseId: 1, warehouseName: 'Main Plant', quantityOnHand: 48, quantityAllocated: 31, available: 17, lastUpdated: '2026-05-25T07:55:00Z' },
  { inventoryId: 3, itemId: 6, itemCode: 'RM-020', itemName: 'High-Density Foam 3"', itemType: 'Raw Material', warehouseId: 1, warehouseName: 'Main Plant', quantityOnHand: 192, quantityAllocated: 88, available: 104, lastUpdated: '2026-05-24T16:30:00Z' },
  // East Warehouse
  { inventoryId: 4, itemId: 2, itemCode: 'FG-002', itemName: 'Classic Futon Mattress - Queen', itemType: 'Finished Good', warehouseId: 2, warehouseName: 'East Warehouse', quantityOnHand: 67, quantityAllocated: 12, available: 55, lastUpdated: '2026-05-25T09:02:00Z' },
  { inventoryId: 5, itemId: 5, itemCode: 'RM-011', itemName: 'Oak Lumber 1x6x96"', itemType: 'Raw Material', warehouseId: 2, warehouseName: 'East Warehouse', quantityOnHand: 82, quantityAllocated: 45, available: 37, lastUpdated: '2026-05-24T11:18:00Z' },
  // West Distribution
  { inventoryId: 6, itemId: 1, itemCode: 'FG-001', itemName: 'Deluxe Futon Frame - Oak', itemType: 'Finished Good', warehouseId: 3, warehouseName: 'West Distribution', quantityOnHand: 19, quantityAllocated: 14, available: 5, lastUpdated: '2026-05-25T10:41:00Z' },
  { inventoryId: 7, itemId: 3, itemCode: 'FG-003', itemName: 'Linen Blend Futon Cover - Natural', itemType: 'Finished Good', warehouseId: 3, warehouseName: 'West Distribution', quantityOnHand: 41, quantityAllocated: 8, available: 33, lastUpdated: '2026-05-23T14:55:00Z' },
  // Finished Goods
  { inventoryId: 8, itemId: 2, itemCode: 'FG-002', itemName: 'Classic Futon Mattress - Queen', itemType: 'Finished Good', warehouseId: 4, warehouseName: 'Finished Goods', quantityOnHand: 112, quantityAllocated: 27, available: 85, lastUpdated: '2026-05-25T06:30:00Z' },
  { inventoryId: 9, itemId: 8, itemCode: 'CM-030', itemName: 'Futon Hinge Mechanism - Heavy Duty', itemType: 'Component', warehouseId: 1, warehouseName: 'Main Plant', quantityOnHand: 29, quantityAllocated: 19, available: 10, lastUpdated: '2026-05-24T19:12:00Z' },
  { inventoryId: 10, itemId: 10, itemCode: 'RM-040', itemName: 'Linen-Cotton Blend Fabric 54"', itemType: 'Raw Material', warehouseId: 2, warehouseName: 'East Warehouse', quantityOnHand: 94, quantityAllocated: 61, available: 33, lastUpdated: '2026-05-25T08:55:00Z' },
];

export const MOCK_TRANSACTIONS: InventoryTransaction[] = [
  { transactionId: 1001, itemId: 4, itemCode: 'RM-010', itemName: 'Oak Lumber 4x4x96"', warehouseName: 'Main Plant', transactionType: 'Issue', quantity: -12, unitCost: 31.20, referenceNumber: 'PO-88421', notes: 'Cutting - Frame FG-001', transactionDate: '2026-05-25T07:42:00Z', createdBy: 'Maria T.' },
  { transactionId: 1002, itemId: 1, itemCode: 'FG-001', itemName: 'Deluxe Futon Frame - Oak', warehouseName: 'Main Plant', transactionType: 'Receipt', quantity: 18, unitCost: 187.50, referenceNumber: 'PROD-4491', notes: 'Production completion', transactionDate: '2026-05-24T16:05:00Z', createdBy: 'System' },
  { transactionId: 1003, itemId: 6, itemCode: 'RM-020', itemName: 'High-Density Foam 3"', warehouseName: 'Main Plant', transactionType: 'Adjustment', quantity: -8, unitCost: 8.95, referenceNumber: 'ADJ-221', notes: 'Cycle count variance', transactionDate: '2026-05-24T14:20:00Z', createdBy: 'James K.' },
  { transactionId: 1004, itemId: 2, itemCode: 'FG-002', itemName: 'Classic Futon Mattress - Queen', warehouseName: 'East Warehouse', transactionType: 'Transfer', quantity: -15, unitCost: 142.00, referenceNumber: 'TRF-559', notes: 'Transfer to Finished Goods', transactionDate: '2026-05-23T11:30:00Z', createdBy: 'Elena R.' },
  { transactionId: 1005, itemId: 11, itemCode: 'CM-050', itemName: '8" Innerspring Unit - Queen', warehouseName: 'Main Plant', transactionType: 'Receipt', quantity: 30, unitCost: 67.25, referenceNumber: 'PO-88307', notes: 'Supplier delivery', transactionDate: '2026-05-22T09:15:00Z', createdBy: 'System' },
];

export const MOCK_PRODUCTION_ORDERS: ProductionOrder[] = [
  { productionOrderId: 4412, orderNumber: 'PO-4412', itemId: 1, itemName: 'Deluxe Futon Frame - Oak', itemCode: 'FG-001', quantity: 42, completedQty: 31, status: 'In Progress', workCenter: 'Assembly A', startDate: '2026-05-20', dueDate: '2026-05-28', priority: 'High', materialShortage: false },
  { productionOrderId: 4415, orderNumber: 'PO-4415', itemId: 2, itemName: 'Classic Futon Mattress - Queen', itemCode: 'FG-002', quantity: 65, completedQty: 65, status: 'Completed', workCenter: 'Upholstery', startDate: '2026-05-18', dueDate: '2026-05-25', priority: 'Normal', materialShortage: false },
  { productionOrderId: 4421, orderNumber: 'PO-4421', itemId: 1, itemName: 'Deluxe Futon Frame - Oak', itemCode: 'FG-001', quantity: 28, completedQty: 0, status: 'Released', workCenter: 'Cutting', startDate: '2026-05-26', dueDate: '2026-06-02', priority: 'Normal', materialShortage: true },
  { productionOrderId: 4423, orderNumber: 'PO-4423', itemId: 3, itemName: 'Linen Blend Futon Cover - Natural', itemCode: 'FG-003', quantity: 95, completedQty: 47, status: 'In Progress', workCenter: 'Sewing', startDate: '2026-05-22', dueDate: '2026-05-29', priority: 'High', materialShortage: false },
];

export const MOCK_WORK_CENTERS: WorkCenter[] = [
  { workCenterId: 1, code: 'CUT-01', name: 'Cutting', capacityPerDay: 120, currentUtilization: 87, activeOrders: 2, status: 'Running' },
  { workCenterId: 2, code: 'ASM-A', name: 'Assembly A', capacityPerDay: 48, currentUtilization: 94, activeOrders: 1, status: 'Running' },
  { workCenterId: 3, code: 'UPH-01', name: 'Upholstery', capacityPerDay: 38, currentUtilization: 71, activeOrders: 1, status: 'Running' },
  { workCenterId: 4, code: 'SEW-02', name: 'Sewing', capacityPerDay: 85, currentUtilization: 63, activeOrders: 1, status: 'Running' },
];

export const MOCK_AGENTS: Agent[] = [
  { id: 1, name: 'MRP & Material Planning Agent', description: 'Full BOM explosion, net requirements planning, and purchase order recommendations', category: 'Planning', lastRun: '2026-05-25T06:15:00Z', status: 'Completed', recommendationsGenerated: 7 },
  { id: 2, name: 'Inventory Intelligence Agent', description: 'ABC classification, dynamic reorder points, dead stock identification', category: 'Intelligence', lastRun: '2026-05-25T04:40:00Z', status: 'Idle', recommendationsGenerated: 4 },
  { id: 3, name: 'Production Scheduler Agent', description: 'Capacity-aware scheduling and bottleneck resolution proposals', category: 'Operations', lastRun: '2026-05-24T22:10:00Z', status: 'Idle', recommendationsGenerated: 3 },
  { id: 4, name: 'Quality & Process Agent', description: 'Defect pattern analysis and corrective action recommendations', category: 'Quality', lastRun: '2026-05-23T14:55:00Z', status: 'Idle', recommendationsGenerated: 2 },
];

export const MOCK_RECOMMENDATIONS: AgentRecommendation[] = [
  { id: 9001, agentName: 'MRP & Material Planning Agent', title: 'Create PO for Oak Lumber 4x4x96"', description: 'Net shortage of 87 units detected for FG-001 production orders. 3 suppliers available. Recommended: 120 EA from Oak Valley Lumber @ $29.80/EA.', impact: 'Prevents 3-day production delay', estimatedSavings: 1840, confidence: 94, actionType: 'CREATE_PO', relatedIds: { itemId: 4 }, status: 'PENDING', createdAt: '2026-05-25T06:18:00Z' },
  { id: 9002, agentName: 'Inventory Intelligence Agent', title: 'Transfer excess Linen Blend Fabric from East Warehouse', description: 'East Warehouse holds 61 YD excess above target. Main Plant needs 48 YD for current sewing runs.', impact: 'Avoids expedite shipping cost', estimatedSavings: 620, confidence: 87, actionType: 'ADJUST_INVENTORY', relatedIds: {}, status: 'PENDING', createdAt: '2026-05-25T04:43:00Z' },
  { id: 9003, agentName: 'Production Scheduler Agent', title: 'Release PO-4421 early to Cutting work center', description: 'Capacity opens up 14:00 today. Releasing now avoids conflict with high-priority cover run.', impact: 'Improves on-time completion +2 days', estimatedSavings: 0, confidence: 79, actionType: 'RELEASE_PRODUCTION', relatedIds: { productionOrderId: 4421 }, status: 'PENDING', createdAt: '2026-05-25T05:50:00Z' },
  { id: 9004, agentName: 'MRP & Material Planning Agent', title: 'Expedite hinges - low stock on CM-030', description: 'Only 10 available vs 55 needed for upcoming frame builds. Lead time is 8 days.', impact: 'Critical path item for 2 orders', estimatedSavings: 1250, confidence: 91, actionType: 'CREATE_PO', relatedIds: { itemId: 8 }, status: 'APPROVED', createdAt: '2026-05-24T21:30:00Z' },
];

export const MOCK_KPIS: KpiData = {
  totalSkus: 87,
  totalInventoryValue: 1248750,
  openProductionOrders: 3,
  lowStockItems: 7,
  avgOnTimeDelivery: 94,
  activeWorkCenters: 4,
  pendingRecommendations: 3,
  totalShortages: 2,
};

// Simulated chart data
export const CHART_INVENTORY_BY_TYPE = [
  { name: 'Finished Goods', value: 482300, fill: '#6366f1' },
  { name: 'Raw Materials', value: 391200, fill: '#a5b4fc' },
  { name: 'Components', value: 264100, fill: '#4f46e5' },
  { name: 'Packaging', value: 111150, fill: '#818cf8' },
];

export const CHART_PRODUCTION_TREND = [
  { day: 'May 19', completed: 58, planned: 62 },
  { day: 'May 20', completed: 61, planned: 65 },
  { day: 'May 21', completed: 49, planned: 55 },
  { day: 'May 22', completed: 73, planned: 70 },
  { day: 'May 23', completed: 67, planned: 68 },
  { day: 'May 24', completed: 82, planned: 75 },
  { day: 'May 25', completed: 54, planned: 60 },
];

export const CHART_WORKCENTER_UTIL = MOCK_WORK_CENTERS.map(wc => ({
  name: wc.name,
  utilization: wc.currentUtilization,
}));

// Helper to get BOM for an item
export function getBOMForItem(itemId: number): BOMComponent[] {
  return MOCK_BOM[itemId] || [];
}

// Simulate a small in-memory state for mutations during session
let liveRecommendations = [...MOCK_RECOMMENDATIONS];
let liveProductionOrders = [...MOCK_PRODUCTION_ORDERS];
let liveInventory = [...MOCK_INVENTORY];

export function getLiveRecommendations() { return liveRecommendations; }
export function getLiveProductionOrders() { return liveProductionOrders; }
export function getLiveInventory() { return liveInventory; }

export function approveRecommendation(id: number): AgentRecommendation | null {
  const idx = liveRecommendations.findIndex(r => r.id === id);
  if (idx === -1) return null;
  
  const rec = { ...liveRecommendations[idx], status: 'APPROVED' as const };
  liveRecommendations[idx] = rec;

  // Simulate side effects on other data
  if (rec.actionType === 'RELEASE_PRODUCTION' && rec.relatedIds?.productionOrderId) {
    const poIdx = liveProductionOrders.findIndex(p => p.productionOrderId === rec.relatedIds!.productionOrderId);
    if (poIdx > -1) {
      liveProductionOrders[poIdx] = { ...liveProductionOrders[poIdx], status: 'In Progress' };
    }
  }
  if (rec.actionType === 'ADJUST_INVENTORY') {
    // minor optimistic inventory change
    liveInventory = liveInventory.map(inv => 
      inv.itemCode === 'RM-040' ? { ...inv, quantityAllocated: Math.max(0, inv.quantityAllocated - 48) } : inv
    );
  }
  return rec;
}

export function rejectRecommendation(id: number): boolean {
  const idx = liveRecommendations.findIndex(r => r.id === id);
  if (idx === -1) return false;
  liveRecommendations[idx] = { ...liveRecommendations[idx], status: 'REJECTED' as const };
  return true;
}

export function simulateAgentRun(agentId: number): { newRecs: AgentRecommendation[] } {
  const newRecs: AgentRecommendation[] = [];
  
  if (agentId === 1) { // MRP
    newRecs.push({
      id: Date.now(),
      agentName: 'MRP & Material Planning Agent',
      title: 'Create PO for 8" Innerspring Units',
      description: 'Projected shortage of 18 units for Mattress production next week. Recommend ordering 40 EA.',
      impact: 'Maintains 99% service level',
      confidence: 88,
      actionType: 'CREATE_PO',
      relatedIds: { itemId: 11 },
      status: 'PENDING',
      createdAt: new Date().toISOString(),
    });
  }
  if (agentId === 2) {
    newRecs.push({
      id: Date.now() + 1,
      agentName: 'Inventory Intelligence Agent',
      title: 'Reduce safety stock on packaging',
      description: 'PK-001 has 3.1x coverage. Suggest lowering reorder point from 190 to 145.',
      impact: 'Frees $1,840 working capital',
      estimatedSavings: 1840,
      confidence: 82,
      actionType: 'ADJUST_INVENTORY',
      status: 'PENDING',
      createdAt: new Date().toISOString(),
    });
  }
  // Add to live
  liveRecommendations = [...newRecs, ...liveRecommendations];
  return { newRecs };
}

// ============================================
// PHASE 2 - SALES QUOTES MOCK DATA
// ============================================

export const MOCK_QUOTES: any[] = [
  {
    quoteId: 1,
    quoteNumber: 'QT-2026-0001',
    customerId: 5,
    customerName: 'Restoration Hardware',
    salesChannelId: 3,
    quoteDate: '2026-05-20',
    expirationDate: '2026-06-19',
    status: 'Sent',
    subtotal: 24500,
    discountAmount: 1225,
    taxAmount: 1862,
    totalAmount: 25137,
    convertedToOrderId: null,
    notes: 'Volume discount applied for Q3 commitment',
    createdBy: 'Elena Rodriguez',
    createdAt: '2026-05-20T10:30:00Z',
    details: [
      { quoteDetailId: 1, quoteId: 1, lineNumber: 1, itemId: 2, itemCode: 'FG-002', itemName: 'Classic Futon Mattress - Queen', quantity: 50, unitPrice: 329, discountPercent: 5, lineTotal: 15627.5 },
      { quoteDetailId: 2, quoteId: 1, lineNumber: 2, itemId: 1, itemCode: 'FG-001', itemName: 'Deluxe Futon Frame - Oak', quantity: 25, unitPrice: 449, discountPercent: 5, lineTotal: 10663.75 },
    ]
  },
  {
    quoteId: 2,
    quoteNumber: 'QT-2026-0002',
    customerId: 8,
    customerName: 'Urban Outfitters',
    salesChannelId: 3,
    quoteDate: '2026-05-22',
    expirationDate: '2026-06-21',
    status: 'Draft',
    subtotal: 12400,
    discountAmount: 0,
    taxAmount: 992,
    totalAmount: 13392,
    convertedToOrderId: null,
    notes: 'New store opening in Austin - pilot order',
    createdBy: 'Marcus Chen',
    createdAt: '2026-05-22T14:15:00Z',
    details: [
      { quoteDetailId: 3, quoteId: 2, lineNumber: 1, itemId: 3, itemCode: 'FG-003', itemName: 'Linen Blend Futon Cover - Natural', quantity: 80, unitPrice: 119, discountPercent: 0, lineTotal: 9520 },
      { quoteDetailId: 4, quoteId: 2, lineNumber: 2, itemId: 12, itemCode: 'PK-001', itemName: 'Corrugated Shipping Carton - Large', quantity: 80, unitPrice: 6.95, discountPercent: 0, lineTotal: 556 },
    ]
  },
  {
    quoteId: 3,
    quoteNumber: 'QT-2026-0003',
    customerId: 2,
    customerName: 'West Elm Retail',
    salesChannelId: 3,
    quoteDate: '2026-05-18',
    expirationDate: '2026-06-17',
    status: 'Accepted',
    subtotal: 67240,
    discountAmount: 3362,
    taxAmount: 5110,
    totalAmount: 68988,
    convertedToOrderId: 17,
    notes: 'Converted to SO-8917',
    createdBy: 'Elena Rodriguez',
    createdAt: '2026-05-18T09:00:00Z',
    details: []
  }
];

export function getMockQuotes() {
  return [...MOCK_QUOTES];
}

export function getMockQuoteById(id: number) {
  return MOCK_QUOTES.find(q => q.quoteId === id);
}

// ============================================
// PHASE 2 - CUSTOMERS, ORDERS, RETURNS, REPS (for pickers + Returns UI)
// ============================================

export const MOCK_CUSTOMERS: any[] = [
  { customerId: 1, customerCode: 'CUST-001', customerName: 'Home Comfort Retailers', contactName: 'Jennifer Adams', email: 'jadams@homecomfort.com', city: 'Portland', state: 'OR', customerType: 'Retail' },
  { customerId: 2, customerCode: 'CUST-002', customerName: 'West Elm Retail', contactName: 'Robert Taylor', email: 'rtaylor@westelm.com', city: 'Seattle', state: 'WA', customerType: 'Retail' },
  { customerId: 3, customerCode: 'CUST-003', customerName: 'Coastal Living Stores', contactName: 'Maria Garcia', email: 'mgarcia@coastalliving.com', city: 'San Francisco', state: 'CA', customerType: 'Retail' },
  { customerId: 4, customerCode: 'CUST-004', customerName: 'University Dorm Supplies', contactName: 'Kevin Lee', email: 'klee@univdorm.com', city: 'Eugene', state: 'OR', customerType: 'Wholesale' },
  { customerId: 5, customerCode: 'CUST-005', customerName: 'Restoration Hardware', contactName: 'Amanda White', email: 'awhite@rh.com', city: 'Portland', state: 'OR', customerType: 'Retail' },
  { customerId: 6, customerCode: 'CUST-006', customerName: 'Budget Furniture Outlet', contactName: 'Chris Martinez', email: 'cmartinez@budget.com', city: 'Vancouver', state: 'WA', customerType: 'Wholesale' },
  { customerId: 7, customerCode: 'CUST-007', customerName: 'Luxury Living Inc', contactName: 'Patricia Johnson', email: 'pjohnson@luxury.com', city: 'Bellevue', state: 'WA', customerType: 'Retail' },
  { customerId: 8, customerCode: 'CUST-008', customerName: 'Urban Outfitters', contactName: 'Daniel Kim', email: 'dkim@urban.com', city: 'Corvallis', state: 'OR', customerType: 'Wholesale' },
];

export const MOCK_SALES_ORDERS: any[] = [
  { orderId: 17, orderNumber: 'SO-8917', customerId: 2, customerName: 'West Elm Retail', orderDate: '2026-05-18', status: 'Shipped', totalAmount: 68988 },
  { orderId: 21, orderNumber: 'SO-8921', customerId: 5, customerName: 'Restoration Hardware', orderDate: '2026-05-24', status: 'Shipped', totalAmount: 18420 },
  { orderId: 24, orderNumber: 'SO-8924', customerId: 8, customerName: 'Urban Outfitters', orderDate: '2026-05-25', status: 'Processing', totalAmount: 918 },
];

export const MOCK_RETURNS: any[] = [
  {
    returnId: 1,
    returnNumber: 'RT-2026-0001',
    salesOrderId: 17,
    customerId: 2,
    customerName: 'West Elm Retail',
    returnDate: '2026-05-23',
    status: 'Approved',
    refundAmount: 1430,
    restockingFee: 71.5,
    notes: '3x FG-002 damaged in transit',
    details: [
      { itemName: 'Classic Futon Mattress - Queen', quantityReturned: 3, unitPrice: 329, refundAmount: 987, disposition: 'Restock' },
    ],
  },
  {
    returnId: 2,
    returnNumber: 'RT-2026-0002',
    salesOrderId: 21,
    customerId: 5,
    customerName: 'Restoration Hardware',
    returnDate: '2026-05-25',
    status: 'Pending',
    refundAmount: 449,
    restockingFee: 0,
    notes: 'Customer changed mind on frame finish',
    details: [
      { itemName: 'Deluxe Futon Frame - Oak', quantityReturned: 1, unitPrice: 449, refundAmount: 449, disposition: 'Restock' },
    ],
  },
];

export const MOCK_SALES_REPS: any[] = [
  { salesRepId: 1, employeeCode: 'SR-001', firstName: 'Michael', lastName: 'Johnson', email: 'mjohnson@futonmfg.com', territory: 'NW-01', isActive: true, ytdSales: 312400, commissionRate: 0.035 },
  { salesRepId: 2, employeeCode: 'SR-002', firstName: 'Emily', lastName: 'Williams', email: 'ewilliams@futonmfg.com', territory: 'CA-01', isActive: true, ytdSales: 287900, commissionRate: 0.035 },
  { salesRepId: 3, employeeCode: 'SR-003', firstName: 'David', lastName: 'Brown', email: 'dbrown@futonmfg.com', territory: 'CA-02', isActive: true, ytdSales: 198500, commissionRate: 0.04 },
];

export function getMockCustomers() { return [...MOCK_CUSTOMERS]; }
export function getMockSalesOrders() { return [...MOCK_SALES_ORDERS]; }
export function getMockReturns() { return [...MOCK_RETURNS]; }
export function getMockSalesReps() { return [...MOCK_SALES_REPS]; }
