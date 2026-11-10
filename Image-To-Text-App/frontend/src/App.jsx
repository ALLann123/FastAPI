import {useState} from "react";
import "./App.css";

const API_URL="http://localhost:8000"

function App(){
  const [file, setFile]=useState(null);
  const [previewUrl, setPreviewUrl]=useState(null);
  const [text, setText]=useState("");
  const [loading, setLoading]=useState(false);
  const [error, setError]=useState("");

  function handleFileChange(event){
    const selected=event.target.files[0];
    if(!selected)return;

    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected)); //local preview
    setText("")
    setError("")
  }

  async function handleSubmit(event){
    event.preventDefault();
    if(!file)return;

    setLoading(true);
    setError("");
    setText("");

    //Files are sent as multipart form data
    const formData=new FormData();
    formData.append("file", file); //"file" must match the FastAPI parameter name

    try{
      const response=await fetch(`${API_URL}/ocr`,{
        method:"POST",
        body:formData,
      });

      if(!response.ok){
        const data=await response.json()
        throw new Error(data.detail || "Something went wrong");
      }

      const data=await response.json();
      setText(data.text || "(No text found)");
    }catch (err){
      setError(err.message);
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Image to Text</h1>

      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange}/>
        <button type="submit" disabled={!file || loading}>
          {loading?"Reading...":"Extract text"}
        </button>
      </form>

      {previewUrl && (
        <img src={previewUrl} alt="Selected Upload" className="preview" />
      )}

      {error && <p className="error">{error}</p>}

      {text && (
        <>
          <h2>Extracted text</h2>
          <textarea value={text} readOnly rows={12}/>
          <button onClick={()=>navigator.clipboard.writeText(text)}>
            Copy
          </button>
        </>
      )}
    </div>
  );
}

export default App;