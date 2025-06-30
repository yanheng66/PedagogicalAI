// Using require.context to dynamically import all medal images
const medalImages = require.context('../assets/kenneymedals/PNG', false, /\.png$/);

const medals = [
  { id: 'select-from', name: 'Data Novice', description: 'Mastered the basics of SELECT.', image: medalImages('./1.png') },
  { id: 'where', name: 'Filter Fanatic', description: 'Learned the art of the WHERE clause.', image: medalImages('./2.png') },
  { id: 'order-by', name: 'Orderly Oracle', description: 'For sorting results like a pro.', image: medalImages('./3.png') },
  { id: 'inner-join', name: 'Bridge Builder', description: 'Successfully joined tables.', image: medalImages('./4.png') },
  { id: 'left-join', name: 'Left Lane Legend', description: 'Mastered the LEFT JOIN.', image: medalImages('./5.png') },
  { id: 'right-join', name: 'Righteous Ruler', description: 'Mastered the RIGHT JOIN.', image: medalImages('./6.png') },
  { id: 'aggregates', name: 'Count Captain', description: 'For acing aggregate functions.', image: medalImages('./7.png') },
  { id: 'group-by', name: 'Group Guru', description: 'For skillfully grouping data.', image: medalImages('./8.png') },
  { id: 'having', name: 'Having Hero', description: 'Conquered the HAVING clause.', image: medalImages('./9.png') },
  { id: 'subqueries', name: 'Query Quester', description: 'Braved the world of subqueries.', image: medalImages('./10.png') },
  { id: 'case', name: 'Case Connoisseur', description: 'Mastered conditional logic with CASE.', image: medalImages('./11.png') },
];

const medalMap = new Map(medals.map(m => [m.id, m]));

export function getMedalForConcept(conceptId) {
  return medalMap.get(conceptId) || null;
} 