
const fruits=[
  {id:'f1', name:'Mango'},
  {id:'f2', name:'Banana'},
  {id:'f3', name:'Passion fruit'},
];

function App(){
  return (
    <ul>
      {fruits.map((fruit)=>(
        <li key={fruit.id}>{fruit.name}</li>
      ))}
    </ul>
  )
}

export default App;