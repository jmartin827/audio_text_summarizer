import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [uuid, setUuid] = useState(null);
  const [status, setStatus] = useState(null);
  const [ratio, setRatio] = useState(1);

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const onRatioChange = (event) => {
    setRatio(parseFloat(event.target.value));
  }

  const onSubmit = (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('in_file', file);
    formData.append('summary_ratio', ratio);

    console.log('Sending POST request to server...');
    axios.post('http://127.0.0.1:8000/api/process', formData, { responseType: 'json' })
      .then(response => {
        console.log('Received response from server:', response);
        if (response.data.Processing) {
          const uuid = response.data.Processing;
          setUuid(uuid);
          setStatus('Processing...');
          pollResult(uuid);
        }

      })
      .catch(error => {
        console.error('Error occurred during POST request:', error);
      });
  };

  const pollResult = (uuid) => {
  console.log('Sending GET request to server...');
  axios.get(`http://127.0.0.1:8000/api/result?task_uuid=${uuid}`)
    .then(response => {
      console.log('Received response from server:', response);
      //TODO refactor back and front end for better status checks
      if (response.data !== 'In Progress...') {
        setStatus(response.data);
      } else {
        setTimeout(() => pollResult(uuid), 1000);
      }
    })
    .catch(error => {
      console.error('Error occurred during GET request:', error);
    });
};


  return (
    <div>
      <form onSubmit={onSubmit}>
        <input type="file" onChange={onFileChange} />
        <label>Summary Ratio:</label>
        <input type="number" min="0.1" max="1" step="0.1" value={ratio} onChange={onRatioChange} />
        <button type="submit">Submit</button>
      </form>
      {uuid && <p>Task UUID: {uuid}</p>}
      {status && <p>Status: {status}</p>}
    </div>
  );
}

export default App;
