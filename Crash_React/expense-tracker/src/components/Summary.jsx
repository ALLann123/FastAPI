// src/components/Summary.jsx
import { categories, formatMoney, sumAmounts } from '../utils/expenses.js';

export default function Summary({ expenses }) {
  return (
    <section className="panel">
      <p>Total spent</p>
      <p className="total">{formatMoney(sumAmounts(expenses))}</p>

      <ul className="breakdown">
        {categories.map((category) => {
          const inCategory = expenses.filter((e) => e.category === category);
          return (
            <li key={category}>
              <span>{category}</span>
              <strong>{formatMoney(sumAmounts(inCategory))}</strong>
            </li>
          );
        })}
      </ul>
    </section>
  );
}