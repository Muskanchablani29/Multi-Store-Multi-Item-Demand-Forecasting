import { useState, useEffect } from 'react';
import { FiEdit2, FiSave, FiX, FiAlertTriangle } from 'react-icons/fi';
import { inventoryAPI, shopsAPI, productsAPI } from '../../services/api';
import DataTable from '../../Components/tables/DataTable';
import './Inventory.css';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [shops, setShops] = useState([]);
  const [products, setProducts] = useState([]);
  const [editId, setEditId] = useState(null);
  const [editData, setEditData] = useState({});
  const [newItem, setNewItem] = useState({
    shop_id: '', product_id: '', current_stock: '',
    reorder_point: '', safety_stock: '', lead_time_days: '7'
  });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const load = () => {
    inventoryAPI.getAll().then((r) => setInventory(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => setProducts(r.data));
  }, []);

  const handleSave = async (id) => {
    await inventoryAPI.update(id, editData);
    setEditId(null);
    load();
  };

  const handleAdd = async () => {
    if (!newItem.shop_id || !newItem.product_id) return;
    await inventoryAPI.create(newItem);
    setNewItem({ shop_id: '', product_id: '', current_stock: '', reorder_point: '', safety_stock: '', lead_time_days: '7' });
    load();
  };

  const filtered = filter === 'alerts' ? inventory.filter((i) => i.needs_reorder) : inventory;

  const statusColor = (s) => {
    if (s === 'Sufficient Stock') return 'badge-success';
    if (s === 'Low Stock') return 'badge-warning';
    return 'badge-danger';
  };

  const columns = [
    { key: 'shop_name', label: 'Shop' },
    { key: 'product_name', label: 'Product' },
    { key: 'category', label: 'Category' },
    { key: 'brand', label: 'Brand' },
    {
      key: 'current_stock', label: 'Stock',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.current_stock}
            onChange={(e) => setEditData({ ...editData, current_stock: e.target.value })} />
        : v?.toFixed(0)
    },
    {
      key: 'reorder_point', label: 'Reorder At',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.reorder_point}
            onChange={(e) => setEditData({ ...editData, reorder_point: e.target.value })} />
        : v?.toFixed(0)
    },
    {
      key: 'safety_stock', label: 'Safety Stock',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.safety_stock}
            onChange={(e) => setEditData({ ...editData, safety_stock: e.target.value })} />
        : v?.toFixed(0)
    },
    { key: 'lead_time_days', label: 'Lead (days)' },
    {
      key: 'inventory_status', label: 'Status',
      render: (v) => (
        <span className={`badge ${statusColor(v)}`}>
          {v !== 'Sufficient Stock' && <FiAlertTriangle style={{ marginRight: 4 }} />}{v}
        </span>
      )
    },
    {
      key: 'id', label: 'Actions',
      render: (id, row) => editId === id ? (
        <div className="action-btns">
          <button className="icon-btn save" onClick={() => handleSave(id)}><FiSave /></button>
          <button className="icon-btn cancel" onClick={() => setEditId(null)}><FiX /></button>
        </div>
      ) : (
        <button className="icon-btn edit" onClick={() => {
          setEditId(id);
          setEditData({
            current_stock: row.current_stock,
            reorder_point: row.reorder_point,
            safety_stock: row.safety_stock,
            lead_time_days: row.lead_time_days,
          });
        }}><FiEdit2 /></button>
      )
    },
  ];

  if (loading) return <div className="page-loading">Loading inventory...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Inventory Management</h1>
        <p>Track stock levels, safety stock, and reorder points</p>
      </div>

      <div className="inventory-toolbar">
        <div className="filter-tabs">
          {['all', 'alerts'].map((f) => (
            <button key={f} className={`tab-btn ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
              {f === 'all' ? 'All Items' : `⚠ Reorder Alerts (${inventory.filter(i => i.needs_reorder).length})`}
            </button>
          ))}
        </div>
      </div>

      <div className="add-inventory-form">
        <h3>Add Inventory Item</h3>
        <div className="add-form-row">
          <select value={newItem.shop_id} onChange={(e) => setNewItem({ ...newItem, shop_id: e.target.value })}>
            <option value="">Select shop...</option>
            {shops.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select value={newItem.product_id} onChange={(e) => setNewItem({ ...newItem, product_id: e.target.value })}>
            <option value="">Select product...</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input type="number" placeholder="Current Stock" value={newItem.current_stock}
            onChange={(e) => setNewItem({ ...newItem, current_stock: e.target.value })} />
          <input type="number" placeholder="Reorder Point" value={newItem.reorder_point}
            onChange={(e) => setNewItem({ ...newItem, reorder_point: e.target.value })} />
          <input type="number" placeholder="Safety Stock" value={newItem.safety_stock}
            onChange={(e) => setNewItem({ ...newItem, safety_stock: e.target.value })} />
          <input type="number" placeholder="Lead Time (days)" value={newItem.lead_time_days}
            onChange={(e) => setNewItem({ ...newItem, lead_time_days: e.target.value })} />
          <button className="btn-primary" onClick={handleAdd}>Add</button>
        </div>
      </div>

      <DataTable columns={columns} data={filtered} emptyMessage="No inventory records found." />
    </div>
  );
}
