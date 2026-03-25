// backend/calc_bridge.js
const { calculate, Pokemon, Move, Field } = require('@smogon/calc');

// 1. Grab the JSON string passed from Python
const inputString = process.argv[2];
const input = JSON.parse(inputString);
const gen = 9; // Scarlet & Violet

try {
    // 2. Build the Attacker (Assuming max offenses for a "worst-case" scenario check)
    const attacker = new Pokemon(gen, input.attacker_name, {
        item: input.attacker_item || '',
        ability: input.attacker_ability || '',
        status: input.attacker_status || '',
        evs: { atk: 252, spa: 252, spe: 252 }, 
        nature: 'Adamant' 
    });

    // 3. Build the Defender (Assuming max bulk)
    const defender = new Pokemon(gen, input.defender_name, {
        item: input.defender_item || '',
        ability: input.defender_ability || '',
        evs: { hp: 252, def: 252, spd: 252 },
        nature: 'Relaxed'
    });

    // 4. Build the Move
    const move = new Move(gen, input.move_name);

    // 5. Build the Field (VGC is Doubles)
    const field = new Field({
        gameType: 'Doubles',
        defenderSide: {
            isReflect: input.has_reflect || false,
            isLightScreen: input.has_light_screen || false
        }
    });

    // 6. Calculate and Print!
    const result = calculate(gen, attacker, defender, move, field);
    console.log(result.desc());

} catch (error) {
    console.error("SMOGON_ERROR:", error.message);
    process.exit(1);
}