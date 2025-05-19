# helpers/prompt_builder.py

# Optional map from style → author name
AUTHOR_MAP = {
    "One Piece":       "Eiichiro Oda",
    "Jujutsu Kaisen":  "Gege Akutami",
    "Naruto":          "Masashi Kishimoto",
}

def build_battle_prompt(your_name: str,
                        your_traits: str,
                        friend_name: str,
                        friend_traits: str,
                        style: str | None = None,
                        background_effects: str | None = None) -> str:
    """
    Construct a prompt that:
      1) Forces exactly two full-body characters
      2) Includes optional user-supplied background/effects
      3) Optionally injects anime style by franchise
    """
    # 1) Core two-person enforcement
    prompt = (
        "((Exactly two characters, both full-body)): "
        f"{your_name} (left, {your_traits}) vs "
        f"{friend_name} (right, {friend_traits}); "
        "no other people or limbs"
    )
    
    # 2) Optional background/effects
    if background_effects:
        prompt += f". {background_effects}"
    
    # 3) Optional style injection
    if style:
        author = AUTHOR_MAP.get(style)
        if author:
            prompt += f". Rendered in the style of {style} (by {author})"
        else:
            prompt += f". Rendered in the style of {style}"
    
    return prompt
