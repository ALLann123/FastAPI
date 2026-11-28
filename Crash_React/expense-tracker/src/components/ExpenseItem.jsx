// src/components/ExpenseItem.jsx
import { formatMoney } from '../utils/expenses.js';

export default function ExpenseItem({ expense, onDelete }) {
  return (
    <li className="panel item">
      <div>
        <strong>{expense.title}</strong>
        <p className="muted">{expense.category}</p>
      </div>
      <div className="item-end">
        <span>{formatMoney(expense.amount)}</span>
        <button
          type="button"
          className="delete"
          onClick={() => onDelete(expense.id)}
          aria-label={`Delete ${expense.title}`}
        >
          ✕
        </button>
      </div>
    </li>
  );
}