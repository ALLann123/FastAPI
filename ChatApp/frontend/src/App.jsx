import { useState, useRef, useEffect } from "react";
import { checkServer, streamChat } from "./api";
import ChatInput from "./components/ChatInput";
import EmptyState from "./components/EmptyState";
import Message from "./components/Message";
import { context } from "langchain";

//Crypto.randomUUID() only works on https or localhost, so we make our own
const makeId=()=>`${Date.now()}-${Math.random().toString(36).slice(2)}`


export default function App(){
  // All the things that can change while the App is running
  const [messages, setMessages]=useState([])
  const [isStreaming, setIsStreaming]=useState(false)
  const [server, setServer]=useState({status:'checking', model:''})

  // Refs hold values that should not cause a re-render when they change
  const abortRef=useRef(null)
  const bottomRef=useRef(null)

  //Run once when the page loads: is the server up?
  useEffect(()=>{
    checkServer()
    .then((info)=>setServer({status:'online', model:info.model}))
    .catch(()=>setServer({status:'offline', model:''}))
  }, [])

  // Everytime messages change, scroll to the neweset text
  useEffect(()=>{
    bottomRef.current?.scrollIntoView({block:'end'})
  },[messages])


  //Update one message by id(used to greow the assistant's reply)
  function updateMessage(id, changes){
    setMessages((previous)=>
    previous.map((m)=>(m.id===id?{...m, ...changes(m)}:m)),
  )
  }

  async function sendMessage(text){
    const userMessage={id:makeId(), role:'user', content:text}
    const assistantMessage={id:makeId(), role:'assistant', content:''}

    //The model gets the whole conversation so it remembers context
    // We skip the empty replies(stopped early and error messages)
    const history=[...messages, userMessage]
    .filter((m)=> m.content.trim() !=='' && !m.isError)
    .map(({role, content})=> ({role, content}))


    //shows the user's message and an empty assistant bubble right away
    setMessages([...messages, userMessage, assistantMessage])
    setIsStreaming(true)

    const controller=new AbortController()
    abortRef.current=controller

    try{
      await streamChat(
        history,
        (token)=>
          updateMessage(assistantMessage.id, (m)=>({
            content:m.content+token,
          })),
          controller.signal,
      )
    }catch(error){
      //Stopping on purpose is not an error
      if(error.name!=='AbortError'){
        updateMessage(assistantMessage.id,(m)=>({
          content:m.content+ `\n\n ${error.Message}`,
          isError:true
        }))
      }
    } finally{
      setIsStreaming(false)
      abortRef.current=null
    }
  }

  function stopStreaming(){
    abortRef.current?.abort()
  }

  function newChat(){
    abortRef.current?.abort()
    setMessages([])
  }

  return(
    <div className="app">
      <header className="header">
        <h1 className="title">Local Chat</h1>

        <div className="header-right">
          <span className={`status status-${server.status}`}>
            <span className="status-dot"/>
              {server.status==='online' && server.model}
              {server.status==='offline' && 'Server offline'}
              {server.status==='checking' && 'Connecting'}  
            </span>
            <button
              className="ghost-button"
              onClick={newChat}
              disabled={messages.length===0}
            >
              New Chat
            </button>
        </div>
      </header>

      <main className="messages">
        <div className="thread">
          {messages.length===0?(
            <EmptyState onPick={sendMessage}/>
          ):(
            messages.map((message, index)=>(
              <Message
                key={message.id}
                message={message}
                isStreaming={isStreaming && index===messages.length-1}
              />
            ))
          )}
          <div ref={bottomRef}/>
        </div>
      </main>

      <ChatInput
        onSend={sendMessage}
        onStop={stopStreaming}
        isStreaming={isStreaming}
      />
    </div>
  )
}