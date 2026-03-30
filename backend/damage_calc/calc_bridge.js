// backend/damage_calc/calc_bridge.js
const { calculate, Pokemon, Move, Field } = require('@smogon/calc');

// 1. Grab the JSON string passed from Python
const inputString = process.argv[2];
const input = JSON.parse(inputString);
const gen = 9; // Scarlet & Violet

try {
    // 2. Build the Attacker dynamically
    const attacker = new Pokemon(gen, input.attacker_name, {
        item: input.attacker_item || '',
        ability: input.attacker_ability || '',
        status: input.attacker_status || '',
        nature: input.attacker_nature || 'Serious', // 'Serious' is a neutral nature
        // Use the AI's EVs, or default to 0 if none are provided
        evs: input.attacker_evs || { hp: 0, atk: 0, def: 0, spa: 0, spd: 0, spe: 0 } 
    });

    // 3. Build the Defender dynamically
    const defender = new Pokemon(gen, input.defender_name, {
        item: input.defender_item || '',
        ability: input.defender_ability || '',
        nature: input.defender_nature || 'Serious',
        evs: input.defender_evs || { hp: 0, atk: 0, def: 0, spa: 0, spd: 0, spe: 0 }
    });

    // 4. Build the Move
    const move = new Move(gen, input.move_name);

    // --- NEW: THE STATUS MOVE CATCH ---
    // Check if the move is a non-damaging status move BEFORE running the math
    if (move.category === 'Status') {
        console.log(`Calculation Result: 0 damage. ${input.move_name} is a Status move and does not deal direct damage.`);
        process.exit(0); // Exit cleanly so Python can read the text!
    }

    // 5. Build the Field (VGC is Doubles)
    const field = new Field({
        gameType: 'Doubles',
        defenderSide: {
            isReflect: input.has_reflect || false,
            isLightScreen: input.has_light_screen || false
        }
    });

    // 6. Calculate and Print!
    try {
        const result = calculate(gen, attacker, defender, move, field);
        console.log(result.desc());
        
    } catch (calcError) {
        // --- NEW: THE IMMUNITY CATCH ---
        // If it's a damaging move but max damage is 0, it's a type immunity!
        if (calcError.message.includes("damage[damage.length - 1] === 0")) {
            console.log(`Calculation Result: 0 damage. ${input.defender_name} is completely immune to ${input.move_name}.`);
        } else {
            // If it's a completely different error, throw it so Python can catch it
            throw calcError; 
        }
    }

} catch (error) {
    console.error("SMOGON_ERROR:", error.message);
    process.exit(1);
}