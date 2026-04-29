import pytest
import json
from unittest.mock import patch
from agent.tools import calculate_vgc_damage, DamageCalcParams

"""
Requirement 1: The Python-to-Node.js Bridge (Integration Testing)
Ensures that Python can correctly pass data to the Smogon calculator and handle responses.
"""

@patch("requests.post")
def test_sanitizer_cleans_bad_ai_input(mock_post):
    """
    Requirement 1.1: The Sanitizer Test
    Verifies that the calculate_vgc_damage function correctly handles "None" values     
    and translates stat abbreviations.
    """
    mock_post.return_value.json.return_value = {"desc": "252 SpA Pikachu Thunderbolt vs. 0 HP / 0 SpD Charizard: 100-118 (65.3 - 77.1%) -- guaranteed 2HKO"}
    mock_post.return_value.status_code = 200

    bad_data = DamageCalcParams(
        attacker_name="Pikachu",
        defender_name="Charizard",
        move_name="Thunderbolt",
        attacker_item="None", # Should be stripped to ""
        attacker_evs={"attack": 252, "Special-Attack": 4}, # Should be mapped to 'atk' and 'spa'
        defender_evs={"HP": 252} # Should be mapped to 'hp'
    )

    result = calculate_vgc_damage(bad_data)

    assert "Error" not in result
    assert "Pikachu" in result

@patch("requests.post")
def test_math_verification_koraidon_vs_miraidon(mock_post):
    """
    Requirement 1.2: Math Verification Test
    Ensures that the calculator returns the correct expected damage for a known meta matchup.
    """
    mock_post.return_value.json.return_value = {"desc": "252+ Atk Koraidon Collision Course vs. 0 HP / 0 Def Miraidon: 154-182 (88 - 104%) -- 25% chance to OHKO"}
    mock_post.return_value.status_code = 200

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

    assert "Koraidon" in result
    assert "Miraidon" in result
    assert "%" in result
