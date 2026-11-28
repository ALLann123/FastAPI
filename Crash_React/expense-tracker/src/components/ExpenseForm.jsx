// src/components/ExpenseForm.jsx
import { useState } from 'react';
import { categories } from '../utils/expenses.js';

const emptyForm = { title: '', amount: '', category: 'Food' };

export default function ExpenseForm({ onAdd }) {
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');

  function handleChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  }

  function handleSubmit(e) {
    e.preventDefault();

    const title = form.title.trim();
    const amount = Number(form.amount);

    if (title === '') {
      setError('Enter a description.');
      return;
    }
    if (!(amount > 0)) {
      setError('Enter an amount greater than 0.');
      return;
    }

    onAdd({ title, amount, category: form.category });
    setForm(emptyForm);
    setError('');
  }

  return (
    <form className="panel form" onSubmit={handleSubmit} noValidate>
      <label>
        Description
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder="e.g. Lunch"
        />
      </label>

      <label>
        Amount (KSh)
        <input
          name="amount"
          type="number"
          min="0"
          step="any"
          value={form.amount}
          onChange={handleChange}
        />
      </label>

      <label>
        Category
        <select name="category" value={form.category} onChange={handleChange}>
          {categories.map((category) => (
            <option key={category}>{category}</option>
          ))}
        </select>
      </label>

      {error && <p className="error" role="alert">{error}</p>}

      <button type="submit">Add expense</button>
    </form>
  );
}