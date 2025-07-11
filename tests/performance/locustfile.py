"""
Locust performance tests for Story Teller API

This module contains load testing scenarios for the Story Teller API using Locust.
Run with: poetry run locust --host=http://localhost:8080
"""

from locust import HttpUser, task, between
import json
import random
from datetime import datetime


class StoryReaderUser(HttpUser):
    """
    Simulates regular users who primarily read stories.
    This represents the majority of API users.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    weight = 3  # 3x more reader users than writers
    
    def on_start(self):
        """Called when a user starts"""
        self.story_ids = []
        # Try to get some existing story IDs
        self._get_existing_stories()
    
    def _get_existing_stories(self):
        """Get some existing story IDs for testing"""
        try:
            response = self.client.get("/api/v1/stories/?limit=20")
            if response.status_code == 200:
                stories = response.json()
                self.story_ids = [story["id"] for story in stories if "id" in story]
        except Exception:
            pass  # Ignore errors during setup
    
    @task(5)  # Weight: 5 (most frequent)
    def get_stories(self):
        """Test GET /api/v1/stories/ endpoint - basic listing"""
        self.client.get("/api/v1/stories/")
    
    @task(3)  # Weight: 3
    def get_stories_with_pagination(self):
        """Test GET with pagination parameters"""
        params = {
            "limit": random.randint(5, 20),
            "skip": random.randint(0, 10)
        }
        self.client.get("/api/v1/stories/", params=params)
    
    @task(2)  # Weight: 2
    def get_stories_with_filters(self):
        """Test GET with various filters"""
        genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Adventure", "Horror"]
        authors = ["John Doe", "Jane Smith", "Alice Wonder", "Bob Writer"]
        
        params = {
            "limit": random.randint(5, 15),
            "genre": random.choice(genres) if random.random() > 0.5 else None,
            "author": random.choice(authors) if random.random() > 0.7 else None,
            "published_only": random.choice([True, False])
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        self.client.get("/api/v1/stories/", params=params)
    
    @task(2)  # Weight: 2
    def get_specific_story(self):
        """Test GET /api/v1/stories/{story_id} endpoint"""
        if self.story_ids:
            story_id = random.choice(self.story_ids)
            self.client.get(f"/api/v1/stories/{story_id}")
        else:
            # Fallback to likely existing IDs
            story_id = random.randint(1, 10)
            response = self.client.get(f"/api/v1/stories/{story_id}")
            if response.status_code == 200:
                self.story_ids.append(story_id)
    
    @task(1)  # Weight: 1 (least frequent for readers)
    def get_published_stories_only(self):
        """Test filtering for published stories only"""
        params = {
            "published_only": True,
            "limit": random.randint(10, 20)
        }
        self.client.get("/api/v1/stories/", params=params)


class StoryWriterUser(HttpUser):
    """
    Simulates content creators who write and manage stories.
    Performs more write operations but less frequently.
    """
    wait_time = between(2, 5)  # Longer wait times for content creation
    weight = 1  # Fewer writer users
    
    def on_start(self):
        """Called when a user starts"""
        self.created_story_ids = []
        self.user_id = random.randint(1000, 9999)
    
    @task(3)  # Weight: 3
    def create_story(self):
        """Test POST /api/v1/stories/ endpoint"""
        genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Adventure", "Horror", "Drama"]
        
        story_data = {
            "title": f"Test Story {self.user_id}-{random.randint(1, 1000)}",
            "content": self._generate_story_content(),
            "author": f"LoadTest User {self.user_id}",
            "genre": random.choice(genres),
            "is_published": random.choice([True, False])
        }
        
        response = self.client.post(
            "/api/v1/stories/",
            json=story_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            story_data = response.json()
            story_id = story_data.get("id")
            if story_id:
                self.created_story_ids.append(story_id)
    
    @task(2)  # Weight: 2
    def update_story(self):
        """Test PUT /api/v1/stories/{story_id} endpoint"""
        if self.created_story_ids:
            story_id = random.choice(self.created_story_ids)
            update_data = {
                "title": f"Updated Story {self.user_id}-{random.randint(1, 1000)}",
                "content": self._generate_story_content(),
                "genre": random.choice(["Fantasy", "Sci-Fi", "Mystery", "Romance"])
            }
            self.client.put(f"/api/v1/stories/{story_id}", json=update_data)
    
    @task(2)  # Weight: 2
    def publish_story(self):
        """Test PATCH /api/v1/stories/{story_id}/publish endpoint"""
        if self.created_story_ids:
            story_id = random.choice(self.created_story_ids)
            self.client.patch(f"/api/v1/stories/{story_id}/publish")
    
    @task(1)  # Weight: 1
    def unpublish_story(self):
        """Test PATCH /api/v1/stories/{story_id}/unpublish endpoint"""
        if self.created_story_ids:
            story_id = random.choice(self.created_story_ids)
            self.client.patch(f"/api/v1/stories/{story_id}/unpublish")
    
    @task(1)  # Weight: 1
    def read_own_stories(self):
        """Writers also read their own stories"""
        params = {
            "author": f"LoadTest User {self.user_id}",
            "limit": 10
        }
        self.client.get("/api/v1/stories/", params=params)
    
    @task(1)  # Weight: 1 (cleanup)
    def delete_story(self):
        """Test DELETE /api/v1/stories/{story_id} endpoint"""
        if len(self.created_story_ids) > 5:  # Keep some stories, delete others
            story_id = self.created_story_ids.pop()
            self.client.delete(f"/api/v1/stories/{story_id}")
    
    def _generate_story_content(self):
        """Generate realistic story content for testing"""
        content_templates = [
            "Once upon a time in a distant land, there lived a {character} who discovered {discovery}. This epic tale unfolds as they journey through {location} to find {goal}.",
            "In the year {year}, humanity faced its greatest challenge when {event}. Our protagonist, a {character}, must use their {skill} to save {location}.",
            "Detective {name} was called to investigate a mysterious {crime} at {location}. The clues led to an unexpected {discovery} that changed everything.",
            "Love bloomed between {character1} and {character2} during a {season} in {location}. But their {obstacle} threatened to tear them apart forever."
        ]
        
        characters = ["brave knight", "clever wizard", "young detective", "space explorer", "time traveler"]
        discoveries = ["ancient artifact", "hidden portal", "secret message", "magical power", "alien technology"]
        locations = ["the enchanted forest", "a distant planet", "the bustling city", "an ancient castle", "the underground caves"]
        goals = ["the lost treasure", "world peace", "their true love", "the ultimate truth", "a way home"]
        years = [2050, 2100, 2200, 3000, 3500]
        events = ["an alien invasion", "a robot uprising", "climate disaster", "a pandemic", "first contact"]
        skills = ["intelligence", "courage", "magic", "technology", "wisdom"]
        names = ["Smith", "Jones", "Brown", "Wilson", "Johnson"]
        crimes = ["murder", "theft", "disappearance", "fraud", "kidnapping"]
        seasons = ["spring morning", "summer evening", "autumn afternoon", "winter night"]
        obstacles = ["family feud", "social differences", "war", "distance", "misunderstanding"]
        
        template = random.choice(content_templates)
        content = template.format(
            character=random.choice(characters),
            character1=random.choice(characters),
            character2=random.choice(characters),
            discovery=random.choice(discoveries),
            location=random.choice(locations),
            goal=random.choice(goals),
            year=random.choice(years),
            event=random.choice(events),
            skill=random.choice(skills),
            name=random.choice(names),
            crime=random.choice(crimes),
            season=random.choice(seasons),
            obstacle=random.choice(obstacles)
        )
        
        # Add some padding to make it longer
        padding = " This story explores themes of adventure, courage, and determination. The characters face numerous challenges and must overcome their fears to achieve their goals. Through their journey, they learn valuable lessons about friendship, love, and the power of believing in oneself."
        
        return content + padding


class AdminUser(HttpUser):
    """
    Simulates admin users who perform administrative tasks.
    Less frequent but performs more intensive operations.
    """
    wait_time = between(3, 8)  # Longer wait times for admin operations
    weight = 1  # Very few admin users
    
    def on_start(self):
        """Called when an admin user starts"""
        self.admin_created_stories = []
    
    @task(2)  # Weight: 2
    def bulk_story_operations(self):
        """Simulate bulk operations - creating multiple stories"""
        for i in range(random.randint(2, 5)):
            story_data = {
                "title": f"Admin Bulk Story {random.randint(1, 1000)}-{i}",
                "content": "This is an admin-created story for testing bulk operations and system load.",
                "author": "System Administrator",
                "genre": random.choice(["System", "Test", "Admin"]),
                "is_published": True
            }
            
            response = self.client.post("/api/v1/stories/", json=story_data)
            if response.status_code == 200:
                story_id = response.json().get("id")
                if story_id:
                    self.admin_created_stories.append(story_id)
    
    @task(2)  # Weight: 2
    def get_all_stories_admin_view(self):
        """Admin view - get large amounts of data"""
        params = {
            "limit": random.randint(50, 100),  # Larger limits for admin
            "skip": random.randint(0, 50)
        }
        self.client.get("/api/v1/stories/", params=params)
    
    @task(1)  # Weight: 1
    def mass_publish_stories(self):
        """Publish multiple stories in sequence"""
        if self.admin_created_stories:
            stories_to_publish = random.sample(
                self.admin_created_stories, 
                min(3, len(self.admin_created_stories))
            )
            for story_id in stories_to_publish:
                self.client.patch(f"/api/v1/stories/{story_id}/publish")
    
    @task(1)  # Weight: 1
    def cleanup_old_stories(self):
        """Admin cleanup - delete some test stories"""
        if len(self.admin_created_stories) > 10:
            stories_to_delete = random.sample(self.admin_created_stories, 3)
            for story_id in stories_to_delete:
                response = self.client.delete(f"/api/v1/stories/{story_id}")
                if response.status_code == 200:
                    self.admin_created_stories.remove(story_id)


class HealthCheckUser(HttpUser):
    """
    Simulates monitoring systems that regularly check API health.
    Very lightweight and frequent requests.
    """
    wait_time = between(5, 15)  # Regular intervals
    weight = 1  # Few monitoring instances
    
    @task(5)  # Weight: 5
    def health_check(self):
        """Test /health endpoint"""
        self.client.get("/health")
    
    @task(3)  # Weight: 3
    def root_endpoint(self):
        """Test / endpoint"""
        self.client.get("/")
    
    @task(1)  # Weight: 1
    def api_docs_check(self):
        """Check if API docs are accessible"""
        self.client.get("/docs")
