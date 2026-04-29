const { calculate, Pokemon, Move, Field } = require('@smogon/calc');
const GEN = 9;

describe('Damage Calculator', () => {
  test('Validates STAB modifier (1.5x damage)', () => {
    // Ursaluna (Normal/Ground) with Facade (Normal) should have STAB
    const attackerWithStab = new Pokemon(GEN, 'Ursaluna', { evs: { atk: 252 } });
    const attackerWithoutStab = new Pokemon(GEN, 'Garchomp', { evs: { atk: 252 } }); // Dragon/Ground
    const defender = new Pokemon(GEN, 'Amoonguss', { evs: { hp: 252 } });
    const move = new Move(GEN, 'Facade');
    const field = new Field();
    
    const resStab = calculate(GEN, attackerWithStab, defender, move, field);
    const resNoStab = calculate(GEN, attackerWithoutStab, defender, move, field);
    
    // Ursaluna (STAB) should deal more damage than Garchomp (No STAB)
    expect(resStab.damage[0]).toBeGreaterThan(resNoStab.damage[0]);
  });
});
