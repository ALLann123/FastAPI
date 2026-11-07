import ReactMarkdown from 'react-markdown'

export default function Message({message, isStreaming}){
    const isUser=message.role==='user'
    const isWaiting=isStreaming && message.content===''

    if(isUser){
        return (
            <div className='message message-user'>
                <div className='bubble'>
                    {message.content}
                </div>
            </div>
        )
    }

    return (
        <div className='message message-assistant'>
            {isWaiting?(
                <span className='thinking' role='status' aria-label='Thinking'>
                    <i/>
                    <i/>
                    <i/>
                </span>
            ): (
                <div
                    className={[
                        'markdown',
                        isStreaming?'is-streaming':'',
                        message.isError?'is-error':'',
                    ].join(' ')}
                >
                    {/*The model answers in Markdown: headings, lists, code blocks */}
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
            )}
        </div>
    )
}