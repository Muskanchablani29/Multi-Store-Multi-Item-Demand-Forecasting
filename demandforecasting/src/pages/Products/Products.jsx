import { useState, useEffect } from 'react';
import { productsAPI } from '../../services/api';
import DataTable from '../../Components/tables/DataTable';
import './Products.css';

const columns = [
  { key: 'product_id', label: 'ID' },
  { key: 'name', label: 'Product Name' },
  { key: 'category', label: 'Category' },
  { key: 'subcategory', label: 'Subcategory' },
  { key: 'brand', label: 'Brand' },
  { key: 'gender', label: 'Gender' },
  { key: 'size', label: 'Size' },
  { key: 'color', label: 'Color' },
  { key: 'material', label: 'Material' },
  { key: 'unit_price', label: 'Price', render: (v) => v ? `₹${v}` : '—' },
  { key: 'supplier_name', label: 'Supplier' },
  { key: 'lead_time_days', label: 'Lead (days)' },
];

export default function Products() {
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    productsAPI.getAll().then((r) => {
      setProducts(r.data);
      setFiltered(r.data);
      const cats = [...new Set(r.data.map((p) => p.category).filter(Boolean))].sort();
      setCategories(cats);
    }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let data = products;
    if (category) data = data.filter((p) => p.category === category);
    if (search) data = data.filter((p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      p.brand?.toLowerCase().includes(search.toLowerCase())
    );
    setFiltered(data);
  }, [search, category, products]);

  if (loading) return <div className="page-loading">Loading products...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Products</h1>
        <p>Footwear product catalogue — {products.length} products</p>
      </div>

      <div className="products-toolbar">
        <input
          className="search-input"
          placeholder="Search by name or brand..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="cat-filter" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <span className="result-count">{filtered.length} results</span>
      </div>

      <DataTable columns={columns} data={filtered} emptyMessage="No products found." />
    </div>
  );
}
