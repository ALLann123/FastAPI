//const user = true;
const user = false;

const getUser = (user) => ({ role: user ? "admin" : "user" })

//see if the current user is admin
console.log(`ROLE: ${getUser(user).role}`)

/*
Js_Refresh>node boool_arrow.js
ROLE: admin

*/