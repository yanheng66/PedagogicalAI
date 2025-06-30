const curriculumData = [
  {
    id: 'unit-1',
    title: 'Unit 1: Foundations of Querying',
    concepts: [
      { id: 'select-from', title: 'SELECT & FROM', description: 'The absolute basics of retrieving data.' },
      { id: 'where', title: 'WHERE', description: 'Filtering data based on conditions.' },
      { id: 'order-by', title: 'ORDER BY', description: 'Sorting your results.' },
    ],
  },
  {
    id: 'unit-2',
    title: 'Unit 2: Combining Data',
    concepts: [
      { id: 'inner-join', title: 'INNER JOIN', description: 'Combining rows from multiple tables.' },
      { id: 'left-join', title: 'LEFT JOIN', description: 'Getting all records from the "left" table.' },
      { id: 'right-join', title: 'RIGHT JOIN', description: 'Getting all records from the "right" table.' },
    ],
  },
  {
    id: 'unit-3',
    title: 'Unit 3: Aggregating & Grouping Data',
    concepts: [
      { id: 'aggregates', title: 'COUNT, SUM, AVG', description: 'Basic aggregate functions.' },
      { id: 'group-by', title: 'GROUP BY', description: 'Grouping rows that have the same values.' },
      { id: 'having', title: 'HAVING', description: 'Filtering data after aggregation.' },
    ],
  },
  {
    id: 'unit-4',
    title: 'Unit 4: Advanced Concepts',
    concepts: [
      { id: 'subqueries', title: 'Subqueries', description: 'Nesting a query inside another query.' },
      { id: 'case', title: 'CASE Statements', description: 'Adding conditional logic to your queries.' },
    ],
  },
];

export default curriculumData; 