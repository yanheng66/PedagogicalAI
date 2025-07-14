/**
 * SQL Trivia and Fun Facts for Loading Screens
 * Organized by difficulty level and topic relevance
 */

export const SQL_TRIVIA = {
  // General SQL fun facts
  general: [
    {
      fact: "SQL stands for 'Structured Query Language', but it's often pronounced as 'sequel'!",
      icon: "💡"
    },
    {
      fact: "SQL was initially developed at IBM in the 1970s and was originally called SEQUEL.",
      icon: "📚"
    },
    {
      fact: "The largest database ever recorded contained over 200 petabytes of data!",
      icon: "🗄️"
    },
    {
      fact: "SQL is case-insensitive, so 'SELECT' and 'select' work exactly the same way.",
      icon: "🔤"
    },
    {
      fact: "The semicolon (;) at the end of SQL statements is like a period at the end of a sentence.",
      icon: "📝"
    },
    {
      fact: "NULL in SQL doesn't mean zero or empty string - it means 'unknown' or 'missing'!",
      icon: "❓"
    },
    {
      fact: "SQL is the 4th most popular programming language according to Stack Overflow surveys.",
      icon: "🏆"
    },
    {
      fact: "A single SQL query once processed 1.3 trillion rows of data in under 24 hours!",
      icon: "⚡"
    }
  ],

  // Concept-specific trivia
  concepts: {
    "SELECT & FROM": [
      {
        fact: "SELECT * is convenient but can slow down queries - it's better to select only what you need!",
        icon: "🎯"
      },
      {
        fact: "The FROM clause tells SQL where to find your data - like giving directions to a library!",
        icon: "📍"
      },
      {
        fact: "You can SELECT without FROM to do calculations: SELECT 2 + 2 returns 4!",
        icon: "🧮"
      }
    ],
    "WHERE": [
      {
        fact: "WHERE is like a bouncer at a club - it decides which rows get to pass through!",
        icon: "🚪"
      },
      {
        fact: "You can use wildcards with LIKE: '%' matches any sequence, '_' matches any single character.",
        icon: "🃏"
      },
      {
        fact: "WHERE conditions are evaluated for each row individually - like checking tickets one by one.",
        icon: "🎫"
      }
    ],
    "ORDER BY": [
      {
        fact: "ORDER BY is like organizing your bookshelf - you can sort by title, author, or date!",
        icon: "📚"
      },
      {
        fact: "ASC is the default for ORDER BY, so you don't need to write it (but DESC is required).",
        icon: "📈"
      },
      {
        fact: "You can ORDER BY multiple columns - it's like sorting by last name, then first name.",
        icon: "📋"
      }
    ],
    "INNER JOIN": [
      {
        fact: "JOINs are like finding common friends on social media - matching connections!",
        icon: "🤝"
      },
      {
        fact: "INNER JOIN only returns rows where there's a match in both tables - no 'lonely' data!",
        icon: "💑"
      },
      {
        fact: "The ON clause in JOINs is like a bridge connecting two tables together.",
        icon: "🌉"
      }
    ],
    "LEFT JOIN": [
      {
        fact: "LEFT JOIN keeps all rows from the left table, even if they don't have a match!",
        icon: "👈"
      },
      {
        fact: "LEFT JOIN is perfect for finding 'what's missing' - like customers without orders.",
        icon: "🔍"
      }
    ],
    "GROUP BY": [
      {
        fact: "GROUP BY is like sorting mail by zip code - grouping similar things together!",
        icon: "📮"
      },
      {
        fact: "COUNT, SUM, AVG only make sense with GROUP BY - like counting items in each group.",
        icon: "🧮"
      }
    ]
  },

  // Fun programming jokes
  jokes: [
    {
      fact: "A SQL query walks into a bar, walks up to two tables and asks... 'Can I JOIN you?'",
      icon: "😄"
    },
    {
      fact: "Why do programmers prefer dark mode? Because light attracts bugs! (In databases too!)",
      icon: "🐛"
    },
    {
      fact: "There are only 10 types of people: those who understand binary and those who don't... and NULL!",
      icon: "😅"
    },
    {
      fact: "A database administrator's favorite type of music? Heavy metal... because of all the indexes!",
      icon: "🎸"
    }
  ],

  // Motivational learning tips
  tips: [
    {
      fact: "Practice makes perfect! Try writing the same query in different ways to understand SQL better.",
      icon: "💪"
    },
    {
      fact: "Read your SQL queries out loud - if they make sense in English, they're probably correct!",
      icon: "🗣️"
    },
    {
      fact: "Start simple, then add complexity. Master SELECT before tackling complex JOINs!",
      icon: "🎯"
    },
    {
      fact: "Every expert was once a beginner. You're building valuable skills that will last a lifetime!",
      icon: "🌟"
    },
    {
      fact: "SQL skills are in high demand - you're learning one of the most practical programming languages!",
      icon: "💼"
    }
  ]
};

/**
 * Get random trivia based on current concept and user preference
 * @param {string} concept - Current learning concept
 * @param {string} type - Type of trivia (general, concept, joke, tip)
 * @returns {Object} Random trivia object with fact and icon
 */
export function getRandomTrivia(concept = null, type = 'mixed') {
  let triviaPool = [];

  if (type === 'concept' && concept && SQL_TRIVIA.concepts[concept]) {
    triviaPool = SQL_TRIVIA.concepts[concept];
  } else if (type === 'general') {
    triviaPool = SQL_TRIVIA.general;
  } else if (type === 'joke') {
    triviaPool = SQL_TRIVIA.jokes;
  } else if (type === 'tip') {
    triviaPool = SQL_TRIVIA.tips;
  } else {
    // Mixed mode - combine all types, with preference for concept-specific
    triviaPool = [
      ...SQL_TRIVIA.general,
      ...SQL_TRIVIA.jokes,
      ...SQL_TRIVIA.tips
    ];
    
    // Add concept-specific trivia if available
    if (concept && SQL_TRIVIA.concepts[concept]) {
      triviaPool = [
        ...triviaPool,
        ...SQL_TRIVIA.concepts[concept],
        ...SQL_TRIVIA.concepts[concept] // Add twice for higher chance
      ];
    }
  }

  if (triviaPool.length === 0) {
    // Fallback
    return {
      fact: "SQL is an amazing language for working with data!",
      icon: "✨"
    };
  }

  const randomIndex = Math.floor(Math.random() * triviaPool.length);
  return triviaPool[randomIndex];
}

export default SQL_TRIVIA; 