from src.preprocess.naming import strip_component_suffix


def test_strip_component_suffix_boundaries():
    # Case 1: "Readout" contains "Re" (keyword), but should not be stripped
    assert strip_component_suffix("PF6FQ_Q0_Readout_Im_Y11") == "PF6FQ_Q0_Readout"

    # Case 2: "Re" is a distinct token, should be stripped
    assert strip_component_suffix("PF6FQ_Q0_Re_Im_Y11") == "PF6FQ_Q0"

    # Case 3: "Flux" vs "FluxDep" (Overlapping keywords)
    # Both are keywords.
    assert strip_component_suffix("Q0_Flux") == "Q0"
    assert strip_component_suffix("Q0_FluxDep") == "Q0"

    # Case 4: "S11" vs "S11Param" (Prefix match but not keyword)
    assert strip_component_suffix("Q0_S11") == "Q0"
    # Assuming S11Param is NOT a keyword
    assert strip_component_suffix("Q0_S11Param") == "Q0_S11Param"

    # Case 5: Underscore vs Dash delimiters
    assert strip_component_suffix("Q0-S11") == "Q0"
    assert strip_component_suffix("Q0_S11") == "Q0"

    # Case 6: Case insensitivity (Code logic converts to upper for check)
    assert strip_component_suffix("Q0_s11") == "Q0"


if __name__ == "__main__":
    test_strip_component_suffix_boundaries()
    print("All boundary tests passed!")
