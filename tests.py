from unittest import TestCase
from app import app, db
from models import Cupcake

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

# Cupcake data for testing
CUPCAKE_DATA = {
    "flavor": "TestFlavor",
    "size": "TestSize",
    "rating": 5,
    "image": "http://test.com/cupcake.jpg"
}

CUPCAKE_DATA_2 = {
    "flavor": "TestFlavor2",
    "size": "TestSize2",
    "rating": 10,
    "image": "http://test.com/cupcake2.jpg"
}

class CupcakeViewsTestCase(TestCase):
    """Tests for views of API."""

    def setUp(self):
        """Initialize the database and make demo data."""
        db.create_all()

        # Make sure the Cupcake table is empty before each test
        Cupcake.query.delete()

        cupcake = Cupcake(**CUPCAKE_DATA)
        db.session.add(cupcake)
        db.session.commit()

        self.cupcake = cupcake

    def tearDown(self):
        """Clean up the database."""
        db.session.remove()
        db.drop_all()

    def test_list_cupcakes(self):
        """Test the endpoint that lists all cupcakes."""
        with app.test_client() as client:
            resp = client.get("/api/cupcakes")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "cupcakes": [
                    {
                        "id": self.cupcake.id,
                        "flavor": "TestFlavor",
                        "size": "TestSize",
                        "rating": 5,
                        "image": "http://test.com/cupcake.jpg"
                    }
                ]
            })

    def test_get_cupcake(self):
        """Test the endpoint that retrieves a specific cupcake."""
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": self.cupcake.id,
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_create_cupcake(self):
        """Test the endpoint that creates a new cupcake."""
        with app.test_client() as client:
            url = "/api/cupcakes"
            resp = client.post(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json

            # Don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            # Check that the new cupcake is in the database
            self.assertEqual(Cupcake.query.count(), 2)

    def test_patch_cupcake(self):
        """Test the endpoint that updates a cupcake."""
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            updated_data = {
                "flavor": "UpdatedFlavor",
                "rating": 8,
                "size": "UpdatedSize",
                "image": "http://test.com/updated.jpg"
            }

            resp = client.patch(url, json=updated_data)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": self.cupcake.id,
                    "flavor": "UpdatedFlavor",
                    "size": "UpdatedSize",
                    "rating": 8,
                    "image": "http://test.com/updated.jpg"
                }
            })

            # Check that the cupcake in the database is updated
            updated_cupcake = Cupcake.query.get(self.cupcake.id)
            self.assertEqual(updated_cupcake.flavor, "UpdatedFlavor")
            self.assertEqual(updated_cupcake.size, "UpdatedSize")
            self.assertEqual(updated_cupcake.rating, 8)
            self.assertEqual(updated_cupcake.image, "http://test.com/updated.jpg")

    def test_delete_cupcake(self):
        """Test the endpoint that deletes a cupcake."""
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {"message": "Deleted"})

            # Check that the cupcake is no longer in the database
            deleted_cupcake = Cupcake.query.get(self.cupcake.id)
            self.assertIsNone(deleted_cupcake)