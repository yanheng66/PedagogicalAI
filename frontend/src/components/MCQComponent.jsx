import React from 'react';

const styles = {
  container: {
    padding: '24px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
    fontFamily: 'sans-serif',
    marginTop: '20px',
  },
  scenario: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '16px',
    color: '#333',
  },
  tableContainer: {
    display: 'flex',
    gap: '24px',
    marginBottom: '16px',
    flexWrap: 'wrap',
  },
  table: {
    borderCollapse: 'collapse',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  tableTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '8px',
  },
  th: {
    backgroundColor: '#4a90e2',
    color: 'white',
    padding: '8px 12px',
    border: '1px solid #ddd',
    textAlign: 'left',
  },
  td: {
    padding: '8px 12px',
    border: '1px solid #ddd',
    backgroundColor: 'white',
  },
  query: {
    backgroundColor: '#2d2d2d',
    color: '#f8f8f2',
    padding: '16px',
    borderRadius: '4px',
    marginBottom: '16px',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap',
    fontSize: '14px',
  },
  optionsContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '12px',
  },
  optionButton: {
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
    textAlign: 'left',
    backgroundColor: 'white',
    transition: 'all 0.2s ease',
    width: '100%',
    height: '100%',
  },
  selectedOption: {
    borderColor: '#4a90e2',
    backgroundColor: '#e9f2fc',
    boxShadow: '0 0 5px rgba(74, 144, 226, 0.5)',
  }
};

function MCQComponent({ data, onSelectAnswer, selectedAnswer }) {
  if (!data) return null;

  const renderTable = (tableName, tableData) => {
    if (!tableData || tableData.length === 0) return null;
    const headers = Object.keys(tableData[0]);
    return (
      <div key={tableName}>
        <h4 style={styles.tableTitle}>{tableName}</h4>
        <table style={styles.table}>
          <thead>
            <tr>
              {headers.map(header => <th key={header} style={styles.th}>{header}</th>)}
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr key={index}>
                {headers.map(header => <td key={header} style={styles.td}>{String(row[header])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.scenario}>{data.scenario}</h3>
      <div style={styles.tableContainer}>
        {Object.entries(data.tables).map(([tableName, tableData]) => (
          renderTable(tableName, tableData)
        ))}
      </div>
      <p>Given the tables above, what will this query return?</p>
      <pre style={styles.query}><code>{data.query}</code></pre>
      <div style={styles.optionsContainer}>
        {Object.entries(data.options).map(([key, value]) => (
          <button
            key={key}
            onClick={() => onSelectAnswer(key)}
            style={{
              ...styles.optionButton,
              ...(selectedAnswer === key ? styles.selectedOption : {})
            }}
          >
            <strong>{key}:</strong> {value}
          </button>
        ))}
      </div>
    </div>
  );
}

export default MCQComponent; 