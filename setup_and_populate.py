"""
Script to setup and populate the database with initial data for development.
"""

import os

from PeculiarPlaces import create_app, db
from PeculiarPlaces import utils as u


def main():
    """Main function to populate the database."""
    db_path = "development.db"
    if os.path.exists(db_path):
        print(f"Removing existing database {db_path}")
        os.remove(db_path)

    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created.")

        # Create users
        u1 = u.create_user()
        u2 = u.create_user()
        print(f"Created users: {u1.id}, {u2.id}")

        # Create places
        p1 = u.create_place(
            u1.id,
            "Cafe A",
            60.1699,
            24.9384,
            description="Nice cafe",
            category="Cafe",
            address="St 1",
            postal_code="00100",
            city="Helsinki",
            application="web",
        )

        p2 = u.create_place(
            u2.id,
            "Park B",
            60.1710,
            24.9410,
            description="Green park",
            category="Park",
            address="Park St",
            postal_code="00200",
            city="Helsinki",
            application="mobile",
        )

        print(
            f"Created places: {p1.id} trust={p1.trust_score} (user {p1.user_id}), "
            f"{p2.id} trust={p2.trust_score} (user {p2.user_id})"
        )

        # Create reviews
        r1 = u.create_review(u2.id, p1.id, 5, text="Great coffee!")
        r2 = u.create_review(u1.id, p2.id, 4, text="Lovely park.")
        print(f"Created reviews: {r1.id}, {r2.id}")

        # Create image
        img1 = u.create_image(
            u1.id, p1.id, "static/images/cafe.jpg", description="Cafe interior"
        )
        print(
            f"Created image: {img1.id} path={img1.image_path} trust={img1.trust_score}"
        )

        # Create reports
        rep1 = u.create_report_place(u2.id, p1.id, u.ReportType.INAPPROPRIATE)
        rep2 = u.create_report_review(u1.id, r1.id, u.ReportType.INCORRECT)
        rep3 = u.create_report_image(u2.id, img1.id, u.ReportType.APPROPRIATE)
        rep4 = u.create_report_place(u1.id, p2.id, u.ReportType.APPROPRIATE)
        print(
            f"Created reports: place {rep1.id}, review {rep2.id}, image {rep3.id}, place {rep4.id}"
        )

        # Query and show stored data
        places = u.get_all_places()
        reviews_p1 = u.get_reviews_by_place(p1.id)
        images_p1 = u.get_images_by_place(p1.id)

        print("\nPlaces in DB:")
        for p in places:
            print(f"- id={p.id} name={p.name} trust={p.trust_score}")

        print("\nReviews for place 1:")
        for rv in reviews_p1:
            print(
                f"- id={rv.id} user={rv.user_id} rating={rv.rating} trust={rv.trust_score}"
            )

        print("\nImages for place 1:")
        for im in images_p1:
            print(f"- id={im.id} path={im.image_path} trust={im.trust_score}")


if __name__ == "__main__":
    main()
