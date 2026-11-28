// src/components/ExpenseList.jsx
import ExpenseItem from './ExpenseItem.jsx';

export default function ExpenseList({ expenses, onDelete }) {
  if (expenses.length === 0) {
    return <p className="muted">No expenses to show.</p>;
  }

  return (
    <ul className="list">
      {expenses.map((expense) => (
        <ExpenseItem key={expense.id} expense={expense} onDelete={onDelete} />
      ))}
    </ul>
  );
}