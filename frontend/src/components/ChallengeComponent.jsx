import React from 'react';

const styles = {
  container: {
    padding: '24px',
    backgroundColor: '#f0f4f8',
    borderRadius: '8px',
    border: '1px solid #d6e0f0',
    fontFamily: 'sans-serif',
    marginTop: '20px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '8px',
    color: '#1e3a8a',
  },
  difficulty: {
    display: 'inline-block',
    padding: '4px 8px',
    borderRadius: '12px',
    backgroundColor: '#fee2e2',
    color: '#b91c1c',
    fontSize: '12px',
    fontWeight: 'bold',
    marginBottom: '16px',
  },
  problem: {
    fontSize: '16px',
    marginBottom: '16px',
    color: '#334155',
  },
  schemaContainer: {
    marginBottom: '20px',
  },
  schemaTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#1e3a8a',
    marginBottom: '8px',
    borderBottom: '2px solid #d6e0f0',
    paddingBottom: '4px',
  },
  schemaContent: {
    backgroundColor: '#ffffff',
    padding: '12px',
    borderRadius: '4px',
    fontFamily: 'monospace',
    color: '#475569',
    whiteSpace: 'pre-wrap',
  },
  inputContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  textarea: {
    width: '100%',
    minHeight: '150px',
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
    fontFamily: 'monospace',
    backgroundColor: '#1e293b',
    color: '#f8fafc',
    resize: 'vertical',
  }
};

function ChallengeComponent({ data }) {
  if (!data) return null;

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>{data.title}</h3>
      <span style={styles.difficulty}>{data.difficulty}</span>
      <p style={styles.problem}>{data.problem}</p>

      <div style={styles.schemaContainer}>
        <h4 style={styles.schemaTitle}>Schema Reference</h4>
        <pre style={styles.schemaContent}>
          <code>{JSON.stringify(data.schema, null, 2)}</code>
        </pre>
      </div>
      
      <div style={styles.inputContainer}>
        <textarea
          style={styles.textarea}
          placeholder="Write your SQL query here..."
        />
      </div>
    </div>
  );
}

export default ChallengeComponent; 