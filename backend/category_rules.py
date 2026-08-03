"""
Keyword-based auto-categorization rules. Simple substring matching against
transaction titles/descriptions — deliberately not ML-based, per project scope.
"""

CATEGORY_KEYWORDS = {
    "Transport": ["uber", "pathao", "taxi", "bus", "petrol", "fuel", "parking"],
    "Food & Groceries": [
        "bhat-bhateni",
        "supermarket",
        "grocery",
        "vegetable",
        "kirana",
    ],
    "Dining": ["restaurant", "cafe", "coffee", "bakery", "pizza", "momo"],
    "Rent": ["rent", "landlord", "lease"],
    "Utilities": [
        "electricity",
        "nea",
        "water bill",
        "internet",
        "wifi",
        "ntc",
        "worldlink",
    ],
    "Entertainment": ["movie", "netflix", "spotify", "cinema", "youtube premium"],
    "Health": ["pharmacy", "hospital", "clinic", "medicine", "doctor"],
    "Education": ["tuition", "college", "book", "course", "exam fee"],
    "Shopping": ["daraz", "mall", "clothing", "shoes"],
}


def suggest_category(title: str, description: str = "") -> str | None:
    """
    Suggest a category by matching keywords against a transaction's title and description.

    Args:
        title (str): The transaction title.
        description (str): The transaction description, optional.

    Returns:
        str | None: The first matching category name, or None if no keyword matched.
    """
    text = f"{title} {description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return None
