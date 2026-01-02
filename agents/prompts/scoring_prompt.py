"""Scoring prompt for compatibility assessment."""

SCORING_PROMPT_TEMPLATE = """Based on your conversation with {partner_name}, please assess your compatibility as a potential life partner.

Consider:
- Personality alignment: Do your traits complement or conflict?
- Shared interests: Do you have common skills, tools, or goals?
- Communication quality: Did the conversation flow naturally?
- Long-term potential: Could you build a life together?

Provide your assessment in this EXACT format:

REASONING: [Write 2-3 sentences explaining your assessment. Be specific about what attracted you or concerned you about {partner_name}.]

SCORE: [Provide a number from 0-100, where:
  0-30 = Incompatible (significant conflicts or lack of connection)
  31-60 = Moderate compatibility (some positive aspects, some concerns)
  61-85 = Good compatibility (strong connection with minor reservations)
  86-100 = Excellent compatibility (highly compatible, excited about partnership)
]

Remember to stay true to your personality and be honest in your assessment."""


def generate_scoring_prompt(partner_name: str) -> str:
    """Generate scoring prompt for a specific partner.

    Args:
        partner_name: Name of the partner to assess.

    Returns:
        Formatted scoring prompt string.
    """
    return SCORING_PROMPT_TEMPLATE.format(partner_name=partner_name)
