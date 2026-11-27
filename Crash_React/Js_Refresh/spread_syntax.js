const user = { id: 1, city: 'Nairobi' };
const updated = {...user, city: "Mombasa" };

//display original
console.log(`Previous: ${user.city}`);
console.log(`Updated: ${updated.city}`);

/**
 Js_Refresh>node spread_syntax.js
Previous: Nairobi
Updated: Mombasa

 */