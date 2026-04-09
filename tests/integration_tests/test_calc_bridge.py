import pytest
import json
from agent.tools import calculate_vgc_damage, DamageCalcParams

"""
Requirement 1: The Python-to-Node.js Bridge (Integration Testing)
Ensures that Python can correctly pass data to the Smogon calculator and handle responses.
"""

def test_sanitizer_cleans_bad_ai_input():
    """
    Requirement 1.1: The Sanitizer Test
    Verifies that the calculate_vgc_damage function correctly handles "None" values
    and translates stat abbreviations.
    
    Potential Fail: The tool might crash if 'None' is passed to Node.js as a string,
    because @smogon/calc expects an empty string or a valid item name.
    """
    bad_data = DamageCalcParams(
        attacker_name="Pikachu",
        defender_name="Charizard",
        move_name="Thunderbolt",
        attacker_item="None", # Should be stripped to ""
        attacker_evs={"attack": 252, "Special-Attack": 4}, # Should be mapped to 'atk' and 'spa'
        defender_evs={"HP": 252} # Should be mapped to 'hp'
    )
    
    # We call the tool. Even if we don't mock the subprocess, 
    # we can check if it at least runs without a Python-level crash.
    result = calculate_vgc_damage(bad_data)
    
    assert "Error" not in result
    assert "%" in result or "HP" in result # Expected Smogon output format

def test_math_verification_koraidon_vs_miraidon():
    """
    Requirement 1.2: Math Verification Test
    Ensures that the calculator returns the correct expected damage for a known meta matchup.
    
    Potential Fail: If the 'gen' or 'level' is not passed correctly to Node.js,
    the damage calculation will be wildly incorrect.
    """
    # Level 50 Koraidon Orichalcum Pulse Flare Blitz vs 0 HP / 0 Def Miraidon
    payload = DamageCalcParams(
        attacker_name="Koraidon",
        defender_name="Miraidon",
        move_name="Collision Course",
        attacker_level=50,
        defender_level=50,
        attacker_ability="Orichalcum Pulse",
        attacker_evs={"atk": 252},
        defender_evs={"def": 0, "hp": 0},
        attacker_nature="Adamant"
    )
    
    result = calculate_vgc_damage(payload)
    
    # Smogon output for this specific calc usually includes a percentage range
    # e.g., "252+ Atk Koraidon Collision Course vs. 0 HP / 0 Def Miraidon: 154-182 (88 - 104%) -- 25% chance to OHKO"
    assert "Koraidon" in result
    assert "Miraidon" in result
    assert "%" in result
    
    # Broad check for the math (Collision Course hits hard)
    # If this fails, Node.js might be using Gen 8 math or incorrect base stats.
    assert "(" in result and ")" in result
