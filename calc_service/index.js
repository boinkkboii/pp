const express = require('express');
const { calculate, Pokemon, Move, Field } = require('@smogon/calc');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3001;
const GEN = 9; // Scarlet & Violet

app.post('/calculate', (req, res) => {
    const input = req.body;
    
    try {
        const attacker = new Pokemon(GEN, input.attacker_name, {
            item: input.attacker_item || '',
            ability: input.attacker_ability || '',
            status: input.attacker_status || '',
            nature: input.attacker_nature || 'Serious',
            evs: input.attacker_evs || {},
            ivs: input.attacker_ivs || {},
            boosts: input.attacker_boosts || {},
            level: input.attacker_level || 50,
            teraType: input.attacker_tera || undefined
        });

        const defender = new Pokemon(GEN, input.defender_name, {
            item: input.defender_item || '',
            ability: input.defender_ability || '',
            status: input.defender_status || '',
            nature: input.defender_nature || 'Serious',
            evs: input.defender_evs || {},
            ivs: input.defender_ivs || {},
            boosts: input.defender_boosts || {},
            level: input.defender_level || 50,
            teraType: input.defender_tera || undefined
        });

        const move = new Move(GEN, input.move_name);
        const field = new Field({
            gameType: input.game_type || 'Doubles',
            terrain: input.terrain || undefined,
            weather: input.weather || undefined
        });

        const result = calculate(GEN, attacker, defender, move, field);
        
        res.json({
            desc: result.desc(),
            damage: result.damage,
            range: result.range()
        });
    } catch (error) {
        console.error('Calculation error:', error);
        res.status(400).json({ error: error.message });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`Damage Calculation service running on port ${PORT}`);
});
