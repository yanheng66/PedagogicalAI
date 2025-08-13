import { calculateLevelRequirements, calculateLevelInfo, getLevelTitle } from './levelSystem';

/**
 * Demo script to show the new progressive level system
 */

console.log('🎓 New Progressive Level System for SQL Learning Platform');
console.log('='.repeat(70));

// Show level requirements table
const levels = calculateLevelRequirements(15);
console.log('\n📊 Level Requirements Table:');
console.log('Level | Title                  | XP Required | XP for This Level');
console.log('-'.repeat(70));

levels.forEach(level => {
  const title = getLevelTitle(level.level);
  console.log(
    `${level.level.toString().padStart(2)} | ${title.padEnd(22)} | ${level.totalXPRequired.toString().padStart(11)} | ${level.xpForThisLevel.toString().padStart(16)}`
  );
});

console.log('\n💡 Context:');
console.log('- Each unit provides 110 XP (10+20+30+40+10 across 5 steps)');
console.log('- Early levels are achievable with 1-2 units');
console.log('- Later levels require mastering multiple concepts');
console.log('- Level 15+ requires completing most/all available content');

// Show progression examples
console.log('\n🚀 Progression Examples:');
const testXPs = [0, 110, 220, 450, 700, 1000, 1350, 2200];

testXPs.forEach(xp => {
  const info = calculateLevelInfo(xp);
  console.log(`\nXP: ${xp}`);
  console.log(`  ➜ Level ${info.currentLevel}: ${getLevelTitle(info.currentLevel)}`);
  if (!info.isMaxLevel) {
    console.log(`  ➜ Progress: ${info.xpIntoCurrentLevel}/${info.xpRequiredForCurrentLevel} XP (${Math.round(info.progressPercent)}%)`);
    console.log(`  ➜ Next Level: ${info.xpToNextLevel} XP needed`);
  } else {
    console.log(`  ➜ Maximum Level Achieved! 🎉`);
  }
});

console.log('\n✨ Benefits of This System:');
console.log('• Progressive difficulty keeps users engaged');
console.log('• Early levels provide quick wins for motivation');
console.log('• Later levels reward dedication and mastery');
console.log('• Named titles give a sense of achievement');
console.log('• System scales well with additional content');

export default { calculateLevelRequirements, calculateLevelInfo, getLevelTitle }; 