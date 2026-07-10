"""Seed the database with sample HCPs and interactions for a realistic demo.

Run:  python -m app.seed
This creates tables and inserts sample data WITHOUT calling the LLM (fast, offline),
so search/report tools have data to work with out of the box.
"""

from datetime import date, timedelta

from app.db import Base, engine, SessionLocal
from app.models import HCP, Interaction, FollowUp

SAMPLE_HCPS = [
    ("Dr. Anita Sharma", "Cardiology", "Apollo Hospital"),
    ("Dr. Rajesh Menon", "Endocrinology", "Fortis Healthcare"),
    ("Dr. Priya Nair", "Oncology", "Tata Memorial"),
    ("Dr. Vikram Rao", "Neurology", "AIIMS Delhi"),
    ("Dr. Sunita Patel", "General Medicine", "Max Healthcare"),
]

# (hcp_index, days_ago, channel, product, notes, summary, sentiment, topics)
SAMPLE_INTERACTIONS = [
    (0, 3, "in-person", "Xarelto", "Discussed Xarelto for AF patients; Dr. Sharma keen on new dosing data. Left samples.",
     "In-person meeting with Dr. Sharma on Xarelto for atrial fibrillation; positive interest in new dosing data. Samples provided.",
     "positive", ["Xarelto", "atrial fibrillation", "dosing data", "samples"]),
    (1, 7, "call", "Januvia", "Phone call re Januvia; concerns about insurance coverage for patients.",
     "Call with Dr. Menon regarding Januvia; raised concerns about patient insurance coverage.",
     "neutral", ["Januvia", "insurance", "coverage concerns"]),
    (2, 12, "virtual", "Keytruda", "Virtual meeting on Keytruda trial results; Dr. Nair impressed with survival data.",
     "Virtual discussion with Dr. Nair on Keytruda trial outcomes; strong positive response to survival data.",
     "positive", ["Keytruda", "clinical trial", "survival data"]),
    (3, 20, "in-person", "Aimovig", "Discussed Aimovig for migraine; Dr. Rao skeptical about cost-benefit.",
     "In-person meeting with Dr. Rao on Aimovig for migraine; expressed skepticism about cost-benefit.",
     "negative", ["Aimovig", "migraine", "cost-benefit"]),
    (0, 25, "call", "Xarelto", "Follow-up call with Dr. Sharma; wants a lunch-and-learn for her team.",
     "Follow-up call with Dr. Sharma; requested a lunch-and-learn session for her cardiology team.",
     "positive", ["Xarelto", "lunch-and-learn", "team education"]),
    (4, 5, "virtual", "Ozempic", "Intro call with Dr. Patel on Ozempic; general interest, asked for literature.",
     "Introductory virtual call with Dr. Patel on Ozempic; general interest, requested clinical literature.",
     "neutral", ["Ozempic", "introduction", "literature request"]),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(HCP).count() > 0:
            print("Data already present — skipping seed.")
            return

        hcps = []
        for name, specialty, org in SAMPLE_HCPS:
            h = HCP(name=name, specialty=specialty, organization=org)
            db.add(h)
            hcps.append(h)
        db.flush()

        for idx, days_ago, channel, product, notes, summary, sentiment, topics in SAMPLE_INTERACTIONS:
            db.add(
                Interaction(
                    hcp_id=hcps[idx].id,
                    rep_name="Vashu Singh",
                    date=date.today() - timedelta(days=days_ago),
                    channel=channel,
                    product_discussed=product,
                    raw_notes=notes,
                    llm_summary=summary,
                    extracted_entities={
                        "summary": summary,
                        "products": [product],
                        "key_topics": topics,
                        "sentiment": sentiment,
                    },
                    sentiment=sentiment,
                )
            )
        db.flush()

        # A couple of open follow-ups.
        db.add(FollowUp(hcp_id=hcps[0].id, due_date=date.today() + timedelta(days=4),
                        action="Organize lunch-and-learn for cardiology team.", status="pending"))
        db.add(FollowUp(hcp_id=hcps[4].id, due_date=date.today() + timedelta(days=2),
                        action="Send Ozempic clinical literature pack.", status="pending"))

        db.commit()
        print(f"Seeded {len(hcps)} HCPs, {len(SAMPLE_INTERACTIONS)} interactions, 2 follow-ups.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
