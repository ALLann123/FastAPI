// src/components/CategoryFilter.jsx
import { categories } from '../utils/expenses.js';

export default function CategoryFilter({ selected, onSelect }) {
  const options = ['All', ...categories];

  return (
    <div className="filters">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className={option === selected ? 'chip chip-active' : 'chip'}
          aria-pressed={option === selected}
          onClick={() => onSelect(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
}