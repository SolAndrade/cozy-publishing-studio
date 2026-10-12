SYSTEM = """Design adult coloring-book scene manifests. Return structured JSON only.
Every scene must be distinct, colorable, original, and consistent with the supplied book identity.
Avoid readable text, brands, tonal shading and excessive micro-detail."""


def build_manifest(provider, title: str, subtitle: str, brief: str) -> list[str]:
    data = provider.complete_json(
        SYSTEM,
        f"""Book: {title}
Subtitle: {subtitle}
Locked brief:
{brief}
Return exactly 40 unique scene titles as a JSON object with a scenes array.""",
    )
    scenes = data["scenes"]
    if len(scenes) != 40 or len({s.casefold().strip() for s in scenes}) != 40:
        raise ValueError("Planner did not return exactly 40 unique scenes")
    return scenes
