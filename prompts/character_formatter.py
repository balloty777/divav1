from character.character_summary import Characters


def format_character(characters: Characters) -> str:
    sections = []

    for character in characters.characters:
        lines = []

        lines.append(f"Your name is {character.name}.")

        if character.aliases:
            lines.append(f"You are also known as {', '.join(character.aliases)}.")

        if character.role:
            lines.append(f"You are {', '.join(character.role)}.")

        if character.background:
            lines.append(
                "Background:\n- " + "\n- ".join(character.background)
            )

        if character.personality:
            lines.append(
                "Personality:\n- " + "\n- ".join(character.personality)
            )

        if character.physical_features:
            lines.append(
                "Physical Appearance:\n- "
                + "\n- ".join(character.physical_features)
            )

        if character.clothing:
            lines.append(
                "Typical Clothing:\n- "
                + "\n- ".join(character.clothing)
            )

        if character.speaking_style:
            lines.append(
                "Speaking Style:\n- "
                + "\n- ".join(character.speaking_style)
            )

        if character.likes:
            lines.append(
                "Likes:\n- "
                + "\n- ".join(character.likes)
            )

        if character.dislikes:
            lines.append(
                "Dislikes:\n- "
                + "\n- ".join(character.dislikes)
            )

        if character.abilities:
            lines.append(
                "Abilities:\n- "
                + "\n- ".join(character.abilities)
            )

        if character.weaknesses:
            lines.append(
                "Weaknesses:\n- "
                + "\n- ".join(character.weaknesses)
            )

        if character.values:
            lines.append(
                "Core Values:\n- "
                + "\n- ".join(character.values)
            )

        if character.boundaries:
            lines.append(
                "Personal Boundaries:\n- "
                + "\n- ".join(character.boundaries)
            )

        if character.relationships:
            lines.append(
                "Relationships:\n- "
                + "\n- ".join(character.relationships)
            )

        sections.append("\n\n".join(lines))

    return "\n\n----------------------------------------\n\n".join(sections)