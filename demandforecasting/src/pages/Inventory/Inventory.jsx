import { useState, useCallback, useEffect } from 'react';
import { FiEdit2, FiSave, FiX, FiAlertTriangle, FiPlus } from 'react-icons/fi';
import { inventoryAPI, productsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import DataTable from '../../Components/tables/DataTable';
import './Inventory.css';

const EMPTY_NEW = { product_id: '', current_stock: '', reorder_point: '', safety_stock: '', lead_time_days: '7' };

export default function Inventory() {
  const { shop } = useAuth();
  const [inventory, setInventory] = useState([]);
  const [products, setProducts]   = useState([]);
  const [editId, setEditId]       = useState(null);
  const [editData, setEditData]   = useState({});
  const [newItem, setNewItem]     = useState(EMPTY_NEW);
  const [loading, setLoading]     = useState(true);
  const [saving, setSaving]       = useState(false);
  const [filter, setFilter]       = useState('all');
  const [error, setError]         = useState('');
  const [success, setSuccess]     = useState('');

  const loadInventory = useCallback(() => {
    inventoryAPI.getAll().then((r) => setInventory(r.data)).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadInventory();
    productsAPI.getAll().then((r) => setProducts(r.data));
  }, [loadInventory]);

  const flash = (msg, isError = false) => {
    if (isError) setError(msg); else setSuccess(msg);
    setTimeout(() => { setError(''); setSuccess(''); }, 3000);
  };

  const handleSave = async (id) => {
    setSaving(true);
    try {
      await inventoryAPI.update(id, editData);
      setEditId(null);
      loadInventory();
      flash('Stock updated.');
    } catch { flash('Failed to update.', true); }
    finally { setSaving(false); }
  };

  const handleAdd = async () => {
    if (!newItem.product_id) { flash('Select a product.', true); return; }
    setSaving(true);
    try {
      await inventoryAPI.create({
        shop:           shop?.id,
        product:        newItem.product_id,
        current_stock:  Number(newItem.current_stock)  || 0,
        reorder_point:  Number(newItem.reorder_point)  || 0,
        safety_stock:   Number(newItem.safety_stock)   || 0,
        lead_time_days: Number(newItem.lead_time_days) || 7,
      });
      setNewItem(EMPTY_NEW);
      loadInventory();
      flash('Inventory item added.');
    } catch (e) { flash(e.response?.data?.detail || 'Failed to add item.', true); }
    finally { setSaving(false); }
  };

  const filtered = filter === 'alerts' ? inventory.filter((i) => i.needs_reorder) : inventory;

  const statusColor = (s) => {
    if (s === 'Sufficient Stock') return 'badge-success';
    if (s === 'Low Stock')        return 'badge-warning';
    return 'badge-danger';
  };

  const columns = [
    { key: 'product_name', label: 'Product' },
    { key: 'category',     label: 'Category' },
    { key: 'brand',        label: 'Brand' },
    {
      key: 'current_stock', label: 'Stock',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.current_stock}
            onChange={(e) => setEditData({ ...editData, current_stock: e.target.value })} />
        : Math.round(v ?? 0),
    },
    {
      key: 'reorder_point', label: 'Reorder At',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.reorder_point}
            onChange={(e) => setEditData({ ...editData, reorder_point: e.target.value })} />
        : Math.round(v ?? 0),
    },
    {
      key: 'safety_stock', label: 'Safety Stock',
      render: (v, row) => editId === row.id
        ? <input className="inline-input" type="number" value={editData.safety_stock}
            onChange={(e) => setEditData({ ...editData, safety_stock: e.target.value })} />
        : Math.round(v ?? 0),
    },
    { key: 'lead_time_days', label: 'Lead (days)' },
    {
      key: 'inventory_status', label: 'Status',
      render: (v) => (
        <span className={`badge ${statusColor(v)}`}>
          {v !== 'Sufficient Stock' && <FiAlertTriangle style={{ marginRight: 4 }} />}{v}
        </span>
      ),
    },
    {
      key: 'id', label: 'Actions',
      render: (id, row) => editId === id ? (
        <div className="action-btns">
          <button className="icon-btn save" onClick={() => handleSave(id)} disabled={saving}><FiSave /></button>
          <button className="icon-btn cancel" onClick={() => setEditId(null)}><FiX /></button>
        </div>
      ) : (
        <button className="icon-btn edit" onClick={() => {
          setEditId(id);
          setEditData({ current_stock: row.current_stock, reorder_point: row.reorder_point, safety_stock: row.safety_stock, lead_time_days: row.lead_time_days });
        }}><FiEdit2 /></button>
      ),
    },
  ];

  if (loading) return <div className="page-loading">Loading inventory...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Inventory Management</h1>
        <p>Track stock levels for {shop?.name} — {inventory.length} items</p>
      </div>

      {error   && <div className="inv-msg inv-msg-error">{error}</div>}
      {success && <div className="inv-msg inv-msg-success">{success}</div>}

      <div className="inventory-toolbar">
        <div className="filter-tabs">
          {['all', 'alerts'].map((f) => (
            <button key={f} className={`tab-btn ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
              {f === 'all' ? `All Items (${inventory.length})` : `Reorder Alerts (${inventory.filter(i => i.needs_reorder).length})`}
            </button>
          ))}
        </div>
      </div>

      <div className="add-inventory-form">
        <h3><FiPlus style={{ marginRight: 6 }} />Add Inventory Item</h3>
        <div className="add-form-row">
          <select value={newItem.product_id} onChange={(e) => setNewItem({ ...newItem, product_id: e.target.value })}>
            <option value="">Select product...</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input type="number" placeholder="Current Stock" min="0" value={newItem.current_stock}
            onChange={(e) => setNewItem({ ...newItem, current_stock: e.target.value })} />
          <input type="number" placeholder="Reorder Point" min="0" value={newItem.reorder_point}
            onChange={(e) => setNewItem({ ...newItem, reorder_point: e.target.value })} />
          <input type="number" placeholder="Safety Stock" min="0" value={newItem.safety_stock}
            onChange={(e) => setNewItem({ ...newItem, safety_stock: e.target.value })} />
          <input type="number" placeholder="Lead Time (days)" min="1" value={newItem.lead_time_days}
            onChange={(e) => setNewItem({ ...newItem, lead_time_days: e.target.value })} />
          <button className="btn-primary" onClick={handleAdd} disabled={saving}>
            {saving ? 'Adding...' : 'Add'}
          </button>
        </div>
      </div>

      <DataTable columns={columns} data={filtered} emptyMessage="No inventory records. Add one above." />
    </div>
  );
}
