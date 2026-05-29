import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getMock, postMock, patchMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
  postMock: vi.fn(),
  patchMock: vi.fn(),
}));

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: getMock,
      post: postMock,
      patch: patchMock,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
}));

import {
  createPurchaseOrder,
  getCustomers,
  getPurchaseOrders,
  receiveGoods,
} from './api';

describe('api contract normalization', () => {
  beforeEach(() => {
    getMock.mockReset();
    postMock.mockReset();
    patchMock.mockReset();
  });

  it('normalizes PascalCase customers to camelCase', async () => {
    getMock.mockResolvedValueOnce({
      data: [
        {
          CustomerID: 7,
          CustomerCode: 'CUST-007',
          CustomerName: 'Acme Furniture',
          Email: 'acme@example.com',
        },
      ],
    });

    const customers = await getCustomers();

    expect(customers).toEqual([
      expect.objectContaining({
        customerId: 7,
        customerCode: 'CUST-007',
        customerName: 'Acme Furniture',
        email: 'acme@example.com',
      }),
    ]);
  });

  it('normalizes purchase orders and their detail lines', async () => {
    getMock.mockResolvedValueOnce({
      data: [
        {
          PurchaseOrderID: 4,
          PONumber: 'PO-2026-0004',
          SupplierID: 2,
          SupplierName: 'North Supply',
          ExpectedDeliveryDate: '2026-06-04',
          details: [
            {
              PODetailID: 11,
              ItemID: 9,
              ItemCode: 'RM-009',
              ItemName: 'Steel Coil',
              Quantity: 12,
              QuantityReceived: 3,
              UnitPrice: 22.5,
            },
          ],
        },
      ],
    });

    const orders = await getPurchaseOrders();

    expect(orders[0]).toEqual(
      expect.objectContaining({
        poId: 4,
        poNumber: 'PO-2026-0004',
        supplierId: 2,
        supplierName: 'North Supply',
        expectedDeliveryDate: '2026-06-04',
      }),
    );
    expect(orders[0].details[0]).toEqual(
      expect.objectContaining({
        poDetailId: 11,
        itemId: 9,
        itemCode: 'RM-009',
        itemName: 'Steel Coil',
        quantity: 12,
        quantityReceived: 3,
        unitPrice: 22.5,
      }),
    );
  });

  it('translates purchase order payloads to backend field names', async () => {
    postMock.mockResolvedValueOnce({
      data: {
        PurchaseOrderID: 10,
        PONumber: 'PO-2026-0010',
        SupplierID: 3,
        ExpectedDeliveryDate: '2026-06-08',
      },
    });

    await createPurchaseOrder({
      supplierId: 3,
      warehouseId: 1,
      orderDate: '2026-05-28',
      expectedDeliveryDate: '2026-06-08',
      notes: 'Unit test PO',
      details: [{ itemId: 12, quantity: 4, unitPrice: 18.75 }],
    });

    expect(postMock).toHaveBeenCalledWith('/purchasing/purchase-orders', {
      SupplierID: 3,
      WarehouseID: 1,
      OrderDate: '2026-05-28',
      ExpectedDeliveryDate: '2026-06-08',
      Notes: 'Unit test PO',
      details: [{ LineNumber: 1, ItemID: 12, Quantity: 4, UnitPrice: 18.75 }],
    });
  });

  it('translates receiving payloads to backend field names', async () => {
    postMock.mockResolvedValueOnce({ data: { status: 'received' } });

    await receiveGoods(15, {
      receivedBy: 'Receiving',
      lines: [{ poDetailId: 22, quantityReceived: 5 }],
    });

    expect(postMock).toHaveBeenCalledWith('/purchasing/purchase-orders/15/receive', {
      received_by: 'Receiving',
      notes: undefined,
      lines: [{ PODetailID: 22, QuantityReceived: 5 }],
    });
  });
});
