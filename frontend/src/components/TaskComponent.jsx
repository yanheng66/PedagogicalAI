import React from 'react';

const styles = {
  container: {
    padding: '24px',
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
    fontFamily: 'sans-serif',
    marginTop: '20px',
  },
  task: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '16px',
    color: '#333',
  },
  schemaContainer: {
    display: 'flex',
    gap: '24px',
    marginBottom: '20px',
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
    backgroundColor: '#6c7ae0',
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
  inputContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  label: {
    fontWeight: 'bold',
    marginBottom: '4px',
  },
  textarea: {
    width: '100%',
    minHeight: '120px',
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
    fontFamily: 'monospace',
  },
  sqlTextarea: {
    backgroundColor: '#2d2d2d',
    color: '#f8f8f2',
    fontFamily: 'monospace',
  }
};

function TaskComponent({ data, userQuery, setUserQuery, userExplanation, setUserExplanation }) {
  if (!data) return null;

  const renderSchemaTable = (tableName, columns) => {
    if (!columns || columns.length === 0) return null;
    return (
      <div key={tableName}>
        <h4 style={styles.tableTitle}>{tableName}</h4>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Column</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Description</th>
            </tr>
          </thead>
          <tbody>
            {columns.map((col, index) => (
              <tr key={index}>
                <td style={styles.td}>{col.column}</td>
                <td style={styles.td}>{col.type}</td>
                <td style={styles.td}>{col.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.task}>{data.task}</h3>
      
      <p>Use the following schema as a reference:</p>
      <div style={styles.schemaContainer}>
        {Object.entries(data.schema).map(([tableName, columns]) => (
          renderSchemaTable(tableName, columns)
        ))}
      </div>

      <div style={styles.inputContainer}>
        <div>
          <label htmlFor="sql-query" style={styles.label}>Your SQL Query:</label>
          <textarea
            id="sql-query"
            style={{ ...styles.textarea, ...styles.sqlTextarea }}
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="SELECT ... FROM ... INNER JOIN ..."
          />
        </div>
        <div>
          <label htmlFor="explanation" style={styles.label}>Explain your query in your own words:</label>
          <textarea
            id="explanation"
            style={styles.textarea}
            value={userExplanation}
            onChange={(e) => setUserExplanation(e.target.value)}
            placeholder="This query first..."
          />
        </div>
      </div>
    </div>
  );
}

export default TaskComponent; 