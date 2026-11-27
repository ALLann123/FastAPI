const users = [
    { id: 123, name: "Alice" },
    { id: 234, name: "Barasa" },
    { id: 654, name: "Ruto" },
];

const names = users.map((user) => {
    return user.name
});

console.log(`NAMES: ${names}`);

/*
>node extracting_properties_map.js
NAMES: Alice,Barasa,Ruto

*/