// src/App.jsx
import { useState } from 'react';
import Summary from './components/Summary.jsx';
import ExpenseForm from './components/ExpenseForm.jsx';
import CategoryFilter from './components/CategoryFilter.jsx';
import ExpenseList from './components/ExpenseList.jsx';
import './App.css';

const startingExpenses = [
  { id: 'e1', title: 'Matatu fare', amount: 150, category: 'Transport' },
  { id: 'e2', title: 'Lunch', amount: 350, category: 'Food' },
  { id: 'e3', title: 'Electricity tokens', amount: 1000, category: 'Bills' },
];

export default function App() {
  const [expenses, setExpenses] = useState(startingExpenses);
  const [filter, setFilter] = useState('All');

  // Calculated on every render, so it is always up to date
  const visibleExpenses =
    filter === 'All' ? expenses : expenses.filter((e) => e.category === filter);

  function handleAdd(newExpense) {
    const expense = { ...newExpense, id: crypto.randomUUID() };
    setExpenses((current) => [expense, ...current]);
  }

  function handleDelete(id) {
    setExpenses((current) => current.filter((e) => e.id !== id));
  }

  return (
    <main className="container">
      <h1>Expense Tracker</h1>
      <Summary expenses={expenses} />
      <ExpenseForm onAdd={handleAdd} />
      <CategoryFilter selected={filter} onSelect={setFilter} />
      <ExpenseList expenses={visibleExpenses} onDelete={handleDelete} />
    </main>
  );
}