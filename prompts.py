def convert_description_to_prompt(text: str, model: str) -> str:
    if model == "anime":
        return f"anime style, nsfw, {text}"
    elif model == "realism":
        return f"realistic photo, nsfw, {text}"
    else:
        return text