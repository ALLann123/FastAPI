const SUGGESTIONS=[
  'Explain Python functions',
  'How do I read a file in Python?',
  'What is Penetration testing?',
  'Blackhat python scripting?',
  'Blackhat bash?',
]

export default function EmptyState({onPick}){
    return (
        <div className="empty">
            <h2>What do you want to learn today?</h2>
            <p>The models runs locally</p>
            <div className="suggestions">
                {SUGGESTIONS.map((suggestion)=>(
                    <button key={suggestion} onClick={()=>onPick(suggestion)}>
                        {suggestion}
                    </button>
                ))}
            </div>
        </div>
    )
}