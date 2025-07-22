import { useState, useEffect } from "react";
const API_BASE_URL = "http://localhost:8000";

function PDFList({ pdfs }) {
  return (
    <div>
      <div>
        <h1>PDFs</h1>
      </div>
      <div>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Date</th>
              <th>Creator</th>
            </tr>
          </thead>
          <tbody>
            {pdfs.map((pdf) => (
              <tr key={pdf.id}>
                <td>{pdf.name}</td>
                <td>{pdf.date}</td>
                <td>{pdf.creator}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function App() {
  const [name, setName] = useState("");
  const [pdfs, setPdfs] = useState([]);

  async function addPdf(event) {
    event.preventDefault();

    try {
      const endpoint = `${API_BASE_URL}/create`;
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name }),
        //credentials: "include",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "PDF creation failed");
      }
      console.log("PDF created successfully!");
      setName("");
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/pdfs");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPdfs(data.pdfs);
    };
    return () => ws.close();
  }, []);

  return (
    <>
      <div>
        <div>
          <h1>Create a pdf</h1>
        </div>
        <form onSubmit={addPdf}>
          <div>
            <label>PDF:</label>
            <input
              type="pdf"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <button type="submit">Create PDF</button>
          </div>
        </form>
      </div>
      <PDFList pdfs={pdfs} />
    </>
  );
}
