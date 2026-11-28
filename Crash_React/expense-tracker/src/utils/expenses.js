export const categories = ['Food', 'Transport', 'Bills', 'Other']

export function formatMoney(amount) {
    return `Ksh ${amount.toLocaleString('en-KE')}`;
}

export function sumAmounts(expenses) {
    return expenses.reduce((sum, expense) => sum + expense.amount, 0);
}