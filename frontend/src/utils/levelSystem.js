/**
 * Advanced Level System for SQL Learning Platform
 * 
 * This system provides a progressive XP requirement where higher levels need more XP.
 * Early levels are achievable quickly to give users a sense of progress,
 * while later levels require more dedication and mastery.
 */

/**
 * Define XP requirements for each level
 * Level 1: 100 XP (1 unit = 110 XP, so achievable)
 * Level 2: 250 XP total (150 more needed)
 * Level 3: 450 XP total (200 more needed) 
 * Level 4: 700 XP total (250 more needed)
 * Level 5: 1000 XP total (300 more needed)
 * etc.
 * 
 * Pattern: Each level requires 50 more XP than the previous level increment
 */

export function calculateLevelRequirements(maxLevel = 20) {
  const levels = [];
  let totalXP = 0;
  let increment = 100; // Starting increment
  
  for (let level = 1; level <= maxLevel; level++) {
    if (level === 1) {
      totalXP = 100; // First level needs 100 XP
    } else {
      totalXP += increment;
      increment += 50; // Each level increment grows by 50
    }
    
    levels.push({
      level: level,
      totalXPRequired: totalXP,
      xpForThisLevel: level === 1 ? 100 : increment - 50
    });
  }
  
  return levels;
}

/**
 * Get the level requirements lookup table
 */
const LEVEL_REQUIREMENTS = calculateLevelRequirements(20);

/**
 * Calculate current level and progress based on total XP
 * @param {number} currentXP - User's total XP
 * @returns {Object} Level information
 */
export function calculateLevelInfo(currentXP) {
  // Find current level
  let currentLevel = 1;
  let xpIntoCurrentLevel = currentXP;
  let xpRequiredForCurrentLevel = 100;
  
  for (let i = 0; i < LEVEL_REQUIREMENTS.length; i++) {
    const levelData = LEVEL_REQUIREMENTS[i];
    
    if (currentXP >= levelData.totalXPRequired) {
      currentLevel = levelData.level;
      
      // Calculate XP progress within this level
      if (i < LEVEL_REQUIREMENTS.length - 1) {
        const nextLevelData = LEVEL_REQUIREMENTS[i + 1];
        xpRequiredForCurrentLevel = nextLevelData.totalXPRequired - levelData.totalXPRequired;
        xpIntoCurrentLevel = currentXP - levelData.totalXPRequired;
      } else {
        // Max level reached
        xpRequiredForCurrentLevel = 0;
        xpIntoCurrentLevel = 0;
      }
    } else {
      // Found the level we're working towards
      break;
    }
  }
  
  // Handle case where user is working towards first level
  if (currentLevel === 1 && currentXP < 100) {
    xpIntoCurrentLevel = currentXP;
    xpRequiredForCurrentLevel = 100;
  }
  
  // Calculate next level info
  const nextLevel = currentLevel + 1;
  const nextLevelData = LEVEL_REQUIREMENTS.find(l => l.level === nextLevel);
  const totalXPForNextLevel = nextLevelData ? nextLevelData.totalXPRequired : null;
  const xpToNextLevel = totalXPForNextLevel ? totalXPForNextLevel - currentXP : 0;
  
  // Calculate progress percentage
  const progressPercent = xpRequiredForCurrentLevel > 0 
    ? Math.min(100, (xpIntoCurrentLevel / xpRequiredForCurrentLevel) * 100)
    : 100;
  
  return {
    currentLevel,
    currentXP,
    xpIntoCurrentLevel,
    xpRequiredForCurrentLevel,
    xpToNextLevel,
    progressPercent,
    nextLevel: nextLevelData ? nextLevel : null,
    totalXPForNextLevel,
    isMaxLevel: !nextLevelData,
    levelRequirements: LEVEL_REQUIREMENTS
  };
}

/**
 * Get a level title/name based on the level number
 * @param {number} level - The level number
 * @returns {string} Level title
 */
export function getLevelTitle(level) {
  const titles = {
    1: "SQL Newcomer",
    2: "Data Explorer", 
    3: "Query Apprentice",
    4: "Database Navigator",
    5: "SQL Practitioner",
    6: "Data Analyst",
    7: "Query Specialist",
    8: "Database Expert",
    9: "SQL Architect",
    10: "Data Wizard",
    11: "Query Master",
    12: "Database Guru",
    13: "SQL Virtuoso",
    14: "Data Sage",
    15: "Query Legend",
    16: "Database Oracle",
    17: "SQL Grandmaster",
    18: "Data Deity",
    19: "Query Immortal",
    20: "SQL Supreme"
  };
  
  return titles[level] || `SQL Master Level ${level}`;
}

/**
 * Get XP milestones for progress visualization
 * @param {number} currentXP - Current user XP
 * @param {number} context - Number of levels to show around current level
 * @returns {Array} Array of milestone objects
 */
export function getXPMilestones(currentXP, context = 3) {
  const levelInfo = calculateLevelInfo(currentXP);
  const milestones = [];
  
  const startLevel = Math.max(1, levelInfo.currentLevel - context);
  const endLevel = Math.min(LEVEL_REQUIREMENTS.length, levelInfo.currentLevel + context + 1);
  
  for (let i = startLevel - 1; i < endLevel && i < LEVEL_REQUIREMENTS.length; i++) {
    const levelData = LEVEL_REQUIREMENTS[i];
    milestones.push({
      level: levelData.level,
      xpRequired: levelData.totalXPRequired,
      title: getLevelTitle(levelData.level),
      isCurrentLevel: levelData.level === levelInfo.currentLevel,
      isCompleted: currentXP >= levelData.totalXPRequired,
      isNext: levelData.level === levelInfo.currentLevel + 1
    });
  }
  
  return milestones;
}

export default {
  calculateLevelInfo,
  getLevelTitle,
  getXPMilestones,
  calculateLevelRequirements
}; 