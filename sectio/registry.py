from sectio.geometry import (
    create_i_section_geometry, 
    create_rhs_geometry, 
    create_angle_geometry,
    create_chs_geometry,
    create_shs_geometry,
    create_t_section_geometry,
    create_u_section_geometry,
    create_upn_section_geometry,
    create_ue_section_geometry,
    create_ipn_section_geometry
)

# --- 1. Define Standard Parameter Templates ---
# Most I and U sections share the same basic dimensions
STD_I = {"h": "h", "b": "b", "tf": "tf", "tw": "tw", "r_root": "r_root"}
TAPERED = {**STD_I, "r_toe": "r_toe"}
ANGLE = {"h": "h", "b": "b", "t": "t", "r_root": "r_root", "r_toe": "r_toe"}
HOLLOW = {"h": "h", "b": "b", "t": "t", "r_out": "r_out", "r_in": "r_in"}

# --- 2. Geometry Function Mapping ---
GEOM_MAP = {
    # Parallel I-Sections
    **dict.fromkeys(["sections_ipe", "sections_ipea", "sections_ipeaa", "sections_ipeo", 
                     "sections_hea", "sections_heaa", "sections_heb", "sections_hem", 
                     "sections_he", "sections_hd", "sections_hl"], create_i_section_geometry),
    
    # Tapered / Channels / Others
    "sections_ipn": create_ipn_section_geometry,
    "sections_upe": create_u_section_geometry,
    "sections_uap": create_u_section_geometry,
    "sections_upn": create_upn_section_geometry,
    "sections_ue":  create_ue_section_geometry,
    "sections_lu":  create_angle_geometry,
    "sections_le":  create_angle_geometry,
    "sections_rhs": create_rhs_geometry,
    "sections_shs": create_shs_geometry,
    "sections_chs": create_chs_geometry,
    "sections_t":   create_t_section_geometry
}

# --- 3. Parameter Mapping ---
PARAM_MAP = {
    # Parallel I & U Sections
    **dict.fromkeys(["sections_ipe", "sections_ipea", "sections_ipeaa", "sections_ipeo", 
                     "sections_hea", "sections_heaa", "sections_heb", "sections_hem", 
                     "sections_he", "sections_hd", "sections_hl", 
                     "sections_upe", "sections_uap"], STD_I),
    
    # Tapered Sections
    "sections_ipn": TAPERED,
    "sections_upn": TAPERED,
    "sections_ue":  TAPERED,
    
    # Angles
    "sections_lu": ANGLE,
    "sections_le": {"h": "b", "b": "b", "t": "t", "r_root": "r_root", "r_toe": "r_toe"},
    
    # Hollow & Specialized
    "sections_rhs": HOLLOW,
    "sections_shs": {"a": "h", "t": "t", "r_out": "r_out", "r_in": "r_in"},
    "sections_chs": {"d": "D", "t": "T"},
    "sections_t":   {**TAPERED, "r_web": "r_web"}
}