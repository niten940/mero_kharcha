"""
Keyword-based auto-categorization rules for Mero Kharcha.

Covers both plain-English titles (manually entered expenses) and real Nepali
bank/wallet transaction description codes from eSewa, Khalti, and Sajilo eBanking.
Matching is case-insensitive substring search — no ML, per project scope.
"""

CATEGORY_KEYWORDS = {
    "Transport": [
        "uber", "pathao", "taxi", "bus", "petrol", "fuel", "parking",
        "indreni", "microbus", "tempo",
    ],
    "Food & Groceries": [
        "bhat-bhateni", "supermarket", "grocery", "vegetable", "kirana",
        "laxmi kirana", "pasa", "pasal", "store", "sana pasal",
        "bikesh store", "soft green", "swotha",
    ],
    "Dining": [
        "restaurant", "cafe", "coffee", "bakery", "pizza", "momo",
        "bhanchha ghar", "mahapal", "foodmandu", "bhoj",
    ],
    "Rent": [
        "rent", "landlord", "lease", "bhada", "kotha",
    ],
    "Utilities": [
        "electricity", "nea", "water bill", "internet", "wifi",
        "ntc", "worldlink", "vianet", "subisu", "dish home",
        "wtax", "tax", "drcard installment", "card fee", "installment fee",
    ],
    "Entertainment": [
        "movie", "netflix", "spotify", "cinema", "youtube premium",
        "daraz", "gaming",
    ],
    "Health": [
        "pharmacy", "hospital", "clinic", "medicine", "doctor",
        "aushadhi", "nursing",
    ],
    "Education": [
        "tuition", "college", "book", "course", "exam fee",
        "school", "university", "library",
    ],
    "Shopping": [
        "daraz", "mall", "clothing", "shoes", "sasto deal",
        "sastodeal", "hamrobazar",
    ],
    "Digital Wallet": [
        "esewa", "khalti", "ime pay", "imepay", "prabhu pay",
        "mobile", "mobi", "mobile/",
    ],
    "Bank Transfer": [
        "transferred to", "fund transferred", "transfer to",
        "tbpf", "ips", "cips", "connectips", "nps",
        "nabil", "nmb", "kumari", "sanima", "mega bank",
        "laxmi bank", "global ime", "sbi", "nic asia",
        "payment,", "wd:", "snm",
    ],
    "Income": [
        "transferred from", "money transferred from", "received from",
        "salary", "deposit", "int.pd", "interest paid",
        "cashback", "refund", "load", "topup",
    ],
    "Fees & Charges": [
        "charge", "fee", "commission", "drcard", "card installment",
        "wtax", "withholding",
    ],
}


def suggest_category(title: str, description: str = "") -> str | None:
    """
    Suggest a category by matching keywords against a transaction title and description.

    Matching is case-insensitive. Returns the first category whose keyword list
    contains a substring match. Returns None if no keyword matched.

    Args:
        title (str): The transaction title or bank description code.
        description (str): Optional additional description text.

    Returns:
        str | None: Matched category name, or None if no match found.
    """
    text = f"{title} {description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return None