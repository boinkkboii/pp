import { describe, it, expect } from 'vitest';
import { calculateStat, NATURES } from '../../frontend/src/pages/TeamBuilderPage';

/**
 * Requirement 5: Frontend React Component Testing (Unit)
 * Tests the core stat calculation logic used in the TeamBuilder UI.
 * 
 * Note: We are testing the logic function directly here for precision.
 * In a full UI test, we would use 'render' and 'fireEvent'.
 */

describe('Pokémon Stat Math', () => {
  
  it('Requirement 5.1: Slider Math Testing (Koraidon HP)', () => {
    /**
     * Koraidon Base HP: 100
     * Level: 50
     * IV: 31
     * EV: 252
     * Formula: Math.floor(0.01 * (2 * Base + IV + Math.floor(0.25 * EV)) * Level) + Level + 10
     */
    const base = 100;
    const ev = 252;
    const iv = 31;
    const level = 50;
    const nature = "Serious";
    
    const result = calculateStat('hp', base, ev, iv, level, nature);
    
    // Manual Calculation:
    // 2*100 = 200
    // + 31 = 231
    // + floor(252/4) = 231 + 63 = 294
    // * 0.5 (Level 50) = 147
    // + 50 + 10 = 207
    expect(result).toBe(207);
  });

  it('Requirement 5.2: Nature Modifiers (Adamant Koraidon)', () => {
    /**
     * Koraidon Base Atk: 135
     * Level: 50
     * IV: 31
     * EV: 252
     * Nature: Adamant (+Atk, -SpA)
     */
    const base = 135;
    const ev = 252;
    const iv = 31;
    const level = 50;
    
    // 1. Check Neutral (Hardy)
    const neutralAtk = calculateStat('atk', base, ev, iv, level, 'Hardy');
    // (2*135 + 31 + 63) * 0.5 + 5 = 364 * 0.5 + 5 = 182 + 5 = 187
    expect(neutralAtk).toBe(187);

    // 2. Check Positive Nature (Adamant)
    const positiveAtk = calculateStat('atk', base, ev, iv, level, 'Adamant');
    // 187 * 1.1 = 205.7 -> floor(205)
    expect(positiveAtk).toBe(205);

    // 3. Check Negative Nature (Modest -Atk)
    const negativeAtk = calculateStat('atk', base, ev, iv, level, 'Modest');
    // 187 * 0.9 = 168.3 -> floor(168)
    expect(negativeAtk).toBe(168);
  });

  /**
   * Potential Fails and Problems:
   * 1. Off-by-one errors: If Math.floor is applied at the wrong step, stats will be wrong.
   * 2. Nature handling: Forgetting that HP is NEVER modified by nature.
   * 3. Shedinja: Base 1 HP must always result in 1 HP regardless of EVs/IVs.
   */
  it('Shedinja Case: HP must always be 1', () => {
    const result = calculateStat('hp', 1, 252, 31, 50, 'Serious');
    expect(result).toBe(1);
  });
});
