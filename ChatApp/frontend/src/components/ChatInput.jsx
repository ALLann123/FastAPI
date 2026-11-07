import {useRef, useState} from 'react'

export default function ChatInput({onSend, onStop, isStreaming}){
    const [text, setText]=useState('')
    const textareaRef=useRef(null)

    //make the box grow with the text, up to a limit
    function resize(){
        const box=textareaRef.current
        box.style.height='auto'
        box.style.height=`${Math.min(box.scrollHeight, 200)}px`
    }

    function handleChange(event){
        setText(event.target.value)
        resize()
    }

    function submit(){
        const trimmed=text.trim()
        if(!trimmed || isStreaming) return
        onSend(trimmed)
        setText('')
        textareaRef.current.style.height='auto'
    }

    function handleKeyDown(event){
        //Enter sends. Shift+Enter adds a new line
        if(event.key==='Enter' && !event.shiftKey){
            event.preventDefault()
            submit()
        }
    }


    return (
        <footer className='composer'>
            <div className='composer-box'>
                <textarea
                    ref={textareaRef}
                    value={text}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    placeholder='Ask anything. Enter to send!'
                    rows={1}
                    autoFocus
                />
                {isStreaming?(
                    <button
                        className='round-button stop'
                        onClick={onStop}
                        aria-label='Stop generating'
                        title='Stop generating'
                    >
                        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                        <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />
                        </svg>                      
                    </button>
                ):(
                    <button
                        className='round-button send'
                        onClick={submit}
                        disabled={!text.trim()}
                        aria-label='Send message'
                        title='Send message'
                    >
                        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
                        <path
                            d="M12 19V5M5 12l7-7 7 7"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                        </svg>
                    </button>
                )}
            </div>
        </footer>
    )
}