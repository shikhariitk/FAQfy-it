import React, { useState } from 'react';
import './App.css'; // Import custom CSS

import dropboxIcon from './images/dropbox.svg';
import githubIcon from './images/github.svg';
import notionIcon from './images/notion.svg';
import awsIcon from './images/aws.svg';
import workplaceIcon from './images/workplace.svg'; // Updated the icon import name
import hubspotIcon from './images/Hubspot.svg';
import zoomIcon from './images/zoom.svg';
import slackIcon from './images/slack.svg';
import salesforceIcon from './images/salesforce.svg';
import asanaIcon from './images/asana.svg';
import databricksIcon from './images/databricks.svg';

const appNames = [
  { name: 'Dropbox', icon: dropboxIcon },
  { name: 'GitHub', icon: githubIcon },
  { name: 'Notion', icon: notionIcon },
  { name: 'AWS', icon: awsIcon },
  { name: 'Google Workspace', icon: workplaceIcon },
  { name: 'HubSpot', icon: hubspotIcon },
  { name: 'Zoom', icon: zoomIcon },
  { name: 'Slack', icon: slackIcon },
  { name: 'Salesforce', icon: salesforceIcon },
  { name: 'Asana', icon: asanaIcon },
  { name: 'Databricks', icon: databricksIcon },
];

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [question, setQuestion] = useState('');
  const [error, setError] = useState('');
  const [response, setResponse] = useState(null);

  // Handle dropdown toggle and suggestion filtering
  const handleDropdownToggle = () => {
    setSuggestions((prevSuggestions) => (prevSuggestions.length ? [] : appNames));
  };

  const handleSuggestionClick = (app) => {
    setSelectedApp(app);
    setSuggestions([]);
  };

  // Handle form submission to fetch data from the backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedApp || !question) {
      alert('Please select an app and enter a question.');
      return;
    }

    const app_name = selectedApp.name.toLowerCase();
    setError('');
    setResponse(null);

    try {
      // Send request to backend with selected app and question
      const response = await fetch(`http://127.0.0.1:5000/${app_name}?question=${encodeURIComponent(question)}`);
      const result = await response.json();

      if (response.ok) {
        // Filter the results based on a similarity threshold (e.g., 0.9)
        const filteredResults = result.filter((item) => item.similarity >= 0.9);
        setResponse(filteredResults);
      } else {
        setError(result.error || 'No results found.');
      }
    } catch (error) {
      console.error('Error fetching answer:', error);
      setError('Unable to fetch data.');
    }
  };

  return (
    <div className="container">
      <div className="header text-center mb-4">
        <h1>FAQ ASSISTANT</h1>
        <p className="text-muted">Get answers to your questions instantly!!</p>
      </div>

      <form onSubmit={handleSubmit} id="faq-form">
        <div className="mb-3">
          <label htmlFor="app_name" className="form-label">Search for an App:</label>
          <button
            type="button"
            className="dropdown-button"
            onClick={handleDropdownToggle}
          >
            {selectedApp ? selectedApp.name : 'Select an App'}
            <span style={{ float: 'right' }}> ▼</span>
          </button>
          {suggestions.length > 0 && (
            <div className="dropdown-list">
              {suggestions.map((app) => (
                <div
                  key={app.name}
                  className="dropdown-item"
                  onClick={() => handleSuggestionClick(app)}
                >
                  <img src={app.icon} alt={app.name} style={{ width: '20px', marginRight: '10px' }} />
                  {app.name}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mb-3">
          <label htmlFor="question" className="form-label">Ask a question:</label>
          <input
            type="text"
            name="question"
            id="question"
            className="form-control input-with-background"
            required
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Write your Query"
          />
        </div>
        <button type="submit" className="btn btn-primary" onSubmit={handleSubmit}>Get Answer</button>
      </form>

      {error && <p>{error}</p>}

      {response && (
        <div className="mt-4">
          <h4>Answer:</h4>
          <div className="accordion" id="faqAccordion">
            {response.map((item, index) => (
              <div className="accordion-item" key={index}>
                <h2 className="accordion-header" id={`heading${index}`}>
                  <button
                    className="accordion-button"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target={`#collapse${index}`}
                    aria-expanded="false"
                    aria-controls={`collapse${index}`}
                  >
                    <strong>{item.question}</strong>
                  </button>
                </h2>
                <div
                  id={`collapse${index}`}
                  className="accordion-collapse collapse"
                  aria-labelledby={`heading${index}`}
                  data-bs-parent="#faqAccordion"
                >
                  <div className="accordion-body">
                    {item.answer}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
