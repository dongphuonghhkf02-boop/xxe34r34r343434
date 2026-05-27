"""
Backend API Testing for TAMIS АГРО - Blog + Products Features
Tests all blog CRUD endpoints, products catalog APIs, admin auth, and image uploads.
"""
import requests
import sys
import io
from datetime import datetime

BASE_URL = "https://auto-deploy-script-1.preview.emergentagent.com/api"

class BlogAPITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.test_post_id = None
        self.test_post_slug = None
        self.test_post_id_2 = None

    def log(self, msg: str, level: str = "info"):
        prefix = {
            "info": "ℹ️ ",
            "success": "✅",
            "error": "❌",
            "test": "🔍"
        }.get(level, "")
        print(f"{prefix} {msg}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data=None, headers=None, token=None, files=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        req_headers = {}
        if headers:
            req_headers.update(headers)
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        if not files and data is not None:
            req_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"Testing {name}...", "test")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=req_headers, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=req_headers, timeout=15)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=req_headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers, timeout=15)
            else:
                self.log(f"Unsupported method {method}", "error")
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"Passed - Status: {response.status_code}", "success")
            else:
                self.log(f"Failed - Expected {expected_status}, got {response.status_code}", "error")
                try:
                    self.log(f"Response: {response.json()}", "error")
                except:
                    self.log(f"Response text: {response.text[:300]}", "error")

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            self.log(f"Failed - Error: {str(e)}", "error")
            return False, {}

    # ===== AUTH =====
    def test_admin_login(self):
        """Test POST /api/auth/login with admin credentials"""
        success, response = self.run_test(
            "Admin login (admin@tamis.ua / admin1234)",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@tamis.ua", "password": "admin1234"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            user = response.get('user', {})
            self.log(f"Admin token obtained - role: {user.get('role')}", "info")
            if user.get('role') != 'admin':
                self.log("ERROR: User does not have admin role!", "error")
                return False
        return success

    # ===== PUBLIC BLOG ENDPOINTS =====
    def test_blog_posts_list(self):
        """Test GET /api/blog/posts (public list)"""
        success, response = self.run_test(
            "GET /api/blog/posts (public list)",
            "GET",
            "blog/posts",
            200,
            params={"limit": 10}
        )
        if success:
            items = response.get('items', [])
            total = response.get('total', 0)
            self.log(f"Found {len(items)} posts (total: {total})", "info")
            # Verify content_html is stripped in list view
            if items and 'content_html' in items[0]:
                self.log("WARNING: content_html should be stripped in list view", "error")
            # Verify reading_minutes is present
            if items and 'reading_minutes' not in items[0]:
                self.log("ERROR: reading_minutes missing in list response", "error")
                return False
        return success

    def test_blog_posts_filter_category(self):
        """Test GET /api/blog/posts?category=Інокулянти"""
        success, response = self.run_test(
            "GET /api/blog/posts?category=Інокулянти",
            "GET",
            "blog/posts",
            200,
            params={"category": "Інокулянти", "limit": 10}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} posts in category 'Інокулянти'", "info")
            # Verify all items have the correct category
            for item in items:
                if item.get('category') != 'Інокулянти':
                    self.log(f"ERROR: Post {item.get('slug')} has wrong category: {item.get('category')}", "error")
                    return False
        return success

    def test_blog_posts_filter_tag(self):
        """Test GET /api/blog/posts?tag=соя"""
        success, response = self.run_test(
            "GET /api/blog/posts?tag=соя",
            "GET",
            "blog/posts",
            200,
            params={"tag": "соя", "limit": 10}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} posts with tag 'соя'", "info")
        return success

    def test_blog_posts_search(self):
        """Test GET /api/blog/posts?q=азот"""
        success, response = self.run_test(
            "GET /api/blog/posts?q=азот",
            "GET",
            "blog/posts",
            200,
            params={"q": "азот", "limit": 10}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Search 'азот' found {len(items)} posts", "info")
        return success

    def test_blog_posts_sort_newest(self):
        """Test GET /api/blog/posts?sort=newest"""
        success, response = self.run_test(
            "GET /api/blog/posts?sort=newest",
            "GET",
            "blog/posts",
            200,
            params={"sort": "newest", "limit": 5}
        )
        return success

    def test_blog_posts_sort_oldest(self):
        """Test GET /api/blog/posts?sort=oldest"""
        success, response = self.run_test(
            "GET /api/blog/posts?sort=oldest",
            "GET",
            "blog/posts",
            200,
            params={"sort": "oldest", "limit": 5}
        )
        return success

    def test_blog_posts_sort_popular(self):
        """Test GET /api/blog/posts?sort=popular"""
        success, response = self.run_test(
            "GET /api/blog/posts?sort=popular",
            "GET",
            "blog/posts",
            200,
            params={"sort": "popular", "limit": 5}
        )
        return success

    def test_blog_post_detail(self):
        """Test GET /api/blog/posts/{slug} (detail + views bump)"""
        # First get a post slug from the list
        _, list_response = self.run_test(
            "GET /api/blog/posts (to get a slug)",
            "GET",
            "blog/posts",
            200,
            params={"limit": 1}
        )
        items = list_response.get('items', [])
        if not items:
            self.log("No posts found to test detail endpoint", "error")
            return False
        
        slug = items[0].get('slug')
        initial_views = items[0].get('views', 0)
        
        success, response = self.run_test(
            f"GET /api/blog/posts/{slug} (detail)",
            "GET",
            f"blog/posts/{slug}",
            200
        )
        if success:
            # Verify content_html is present in detail view
            if 'content_html' not in response:
                self.log("ERROR: content_html missing in detail response", "error")
                return False
            # Verify views were bumped
            new_views = response.get('views', 0)
            if new_views <= initial_views:
                self.log(f"WARNING: Views not bumped (was {initial_views}, now {new_views})", "error")
            else:
                self.log(f"Views bumped: {initial_views} → {new_views}", "info")
            # Store slug for related test
            self.test_post_slug = slug
        return success

    def test_blog_post_detail_404(self):
        """Test GET /api/blog/posts/nonexistent-slug (should 404)"""
        success, _ = self.run_test(
            "GET /api/blog/posts/nonexistent-slug (404)",
            "GET",
            "blog/posts/nonexistent-slug-12345",
            404
        )
        return success

    def test_blog_post_related(self):
        """Test GET /api/blog/posts/{slug}/related"""
        if not self.test_post_slug:
            self.log("Skipping - no test post slug available", "error")
            return False
        
        success, response = self.run_test(
            f"GET /api/blog/posts/{self.test_post_slug}/related",
            "GET",
            f"blog/posts/{self.test_post_slug}/related",
            200,
            params={"limit": 3}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} related posts", "info")
            # Verify content_html is stripped
            if items and 'content_html' in items[0]:
                self.log("WARNING: content_html should be stripped in related posts", "error")
        return success

    def test_blog_categories(self):
        """Test GET /api/blog/categories"""
        success, response = self.run_test(
            "GET /api/blog/categories",
            "GET",
            "blog/categories",
            200
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} categories", "info")
            for cat in items[:3]:
                self.log(f"  - {cat.get('name')}: {cat.get('count')} posts", "info")
        return success

    def test_blog_tags(self):
        """Test GET /api/blog/tags"""
        success, response = self.run_test(
            "GET /api/blog/tags",
            "GET",
            "blog/tags",
            200
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} tags (top 50)", "info")
            for tag in items[:3]:
                self.log(f"  - {tag.get('name')}: {tag.get('count')} uses", "info")
        return success

    # ===== ADMIN BLOG ENDPOINTS =====
    def test_admin_blog_list_no_auth(self):
        """Test GET /api/admin/blog/posts without auth (should 401)"""
        success, _ = self.run_test(
            "GET /api/admin/blog/posts (no auth → 401)",
            "GET",
            "admin/blog/posts",
            401
        )
        return success

    def test_admin_blog_list(self):
        """Test GET /api/admin/blog/posts (with admin auth)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        success, response = self.run_test(
            "GET /api/admin/blog/posts (admin)",
            "GET",
            "admin/blog/posts",
            200,
            token=self.admin_token
        )
        if success:
            items = response.get('items', [])
            total = response.get('total', 0)
            self.log(f"Admin sees {len(items)} posts (total: {total})", "info")
            # Count drafts
            drafts = [p for p in items if p.get('status') == 'draft']
            self.log(f"  - {len(drafts)} drafts, {len(items) - len(drafts)} published", "info")
        return success

    def test_admin_blog_create(self):
        """Test POST /api/admin/blog/posts (create post)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "POST /api/admin/blog/posts (create)",
            "POST",
            "admin/blog/posts",
            200,
            data={
                "title": f"Test Post {timestamp}",
                "excerpt": "This is a test post created by automated testing",
                "content_html": "<p>This is the <strong>content</strong> of the test post. It has multiple words to test reading_minutes calculation.</p><p>Second paragraph with more content to ensure we have enough words for a meaningful reading time estimate.</p>",
                "category": "Тестування",
                "tags": ["test", "automation"],
                "hot": False,
                "status": "draft"
            },
            token=self.admin_token
        )
        if success:
            self.test_post_id = response.get('id')
            self.test_post_slug = response.get('slug')
            self.log(f"Created post: id={self.test_post_id}, slug={self.test_post_slug}", "info")
            # Verify reading_minutes is computed
            reading_minutes = response.get('reading_minutes', 0)
            if reading_minutes < 1:
                self.log("ERROR: reading_minutes should be at least 1", "error")
                return False
            self.log(f"Reading minutes: {reading_minutes}", "info")
        return success

    def test_admin_blog_create_duplicate_title(self):
        """Test POST /api/admin/blog/posts with same title (slug uniqueness)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        title = f"Duplicate Title Test {timestamp}"
        
        # Create first post
        success1, response1 = self.run_test(
            "POST /api/admin/blog/posts (first with title)",
            "POST",
            "admin/blog/posts",
            200,
            data={
                "title": title,
                "excerpt": "First post",
                "content_html": "<p>First post content</p>",
                "category": "Тестування",
                "status": "draft"
            },
            token=self.admin_token
        )
        if not success1:
            return False
        
        slug1 = response1.get('slug')
        post_id_1 = response1.get('id')
        
        # Create second post with same title
        success2, response2 = self.run_test(
            "POST /api/admin/blog/posts (second with same title)",
            "POST",
            "admin/blog/posts",
            200,
            data={
                "title": title,
                "excerpt": "Second post",
                "content_html": "<p>Second post content</p>",
                "category": "Тестування",
                "status": "draft"
            },
            token=self.admin_token
        )
        if not success2:
            return False
        
        slug2 = response2.get('slug')
        post_id_2 = response2.get('id')
        self.test_post_id_2 = post_id_2
        
        # Verify slugs are different
        if slug1 == slug2:
            self.log(f"ERROR: Slugs should be unique! Both are: {slug1}", "error")
            return False
        else:
            self.log(f"Slug uniqueness verified: '{slug1}' vs '{slug2}'", "info")
        
        return True

    def test_admin_blog_patch_title(self):
        """Test PATCH /api/admin/blog/posts/{id} (change title)"""
        if not self.admin_token or not self.test_post_id:
            self.log("Skipping - no admin token or test post", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/blog/posts/{id} (change title)",
            "PATCH",
            f"admin/blog/posts/{self.test_post_id}",
            200,
            data={"title": "Updated Test Post Title"},
            token=self.admin_token
        )
        if success:
            new_title = response.get('title')
            self.log(f"Title updated to: {new_title}", "info")
        return success

    def test_admin_blog_patch_status_to_published(self):
        """Test PATCH /api/admin/blog/posts/{id} (draft → published, verify published_at)"""
        if not self.admin_token or not self.test_post_id:
            self.log("Skipping - no admin token or test post", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/blog/posts/{id} (status: draft → published)",
            "PATCH",
            f"admin/blog/posts/{self.test_post_id}",
            200,
            data={"status": "published"},
            token=self.admin_token
        )
        if success:
            status = response.get('status')
            published_at = response.get('published_at')
            self.log(f"Status: {status}, published_at: {published_at}", "info")
            if status != 'published':
                self.log("ERROR: Status should be 'published'", "error")
                return False
            if not published_at:
                self.log("ERROR: published_at should be set when publishing", "error")
                return False
        return success

    def test_admin_blog_patch_toggle_hot(self):
        """Test PATCH /api/admin/blog/posts/{id} (toggle hot)"""
        if not self.admin_token or not self.test_post_id:
            self.log("Skipping - no admin token or test post", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/blog/posts/{id} (toggle hot=true)",
            "PATCH",
            f"admin/blog/posts/{self.test_post_id}",
            200,
            data={"hot": True},
            token=self.admin_token
        )
        if success:
            hot = response.get('hot')
            self.log(f"Hot flag: {hot}", "info")
            if not hot:
                self.log("ERROR: Hot should be True", "error")
                return False
        return success

    def test_admin_blog_patch_tags(self):
        """Test PATCH /api/admin/blog/posts/{id} (update tags)"""
        if not self.admin_token or not self.test_post_id:
            self.log("Skipping - no admin token or test post", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/blog/posts/{id} (update tags)",
            "PATCH",
            f"admin/blog/posts/{self.test_post_id}",
            200,
            data={"tags": ["updated", "tags", "test"]},
            token=self.admin_token
        )
        if success:
            tags = response.get('tags', [])
            self.log(f"Tags updated: {tags}", "info")
        return success

    def test_admin_blog_upload_image(self):
        """Test POST /api/admin/blog/upload-image (multipart file upload)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        # Create a small PNG image (1x1 red pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('test.png', io.BytesIO(png_data), 'image/png')}
        
        success, response = self.run_test(
            "POST /api/admin/blog/upload-image (PNG)",
            "POST",
            "admin/blog/upload-image",
            200,
            files=files,
            token=self.admin_token
        )
        if success:
            url = response.get('url', '')
            filename = response.get('filename', '')
            self.log(f"Uploaded: {filename}, URL: {url}", "info")
            # Verify URL starts with /api/uploads/blog/
            if not url.startswith('/api/uploads/blog/'):
                self.log(f"ERROR: URL should start with /api/uploads/blog/, got: {url}", "error")
                return False
            # Verify file is publicly fetchable
            full_url = f"https://repo-deploy-56.preview.emergentagent.com{url}"
            try:
                fetch_response = requests.get(full_url, timeout=10)
                if fetch_response.status_code == 200:
                    self.log(f"File is publicly accessible at {url}", "info")
                else:
                    self.log(f"WARNING: File not accessible (status {fetch_response.status_code})", "error")
            except Exception as e:
                self.log(f"WARNING: Could not verify file accessibility: {e}", "error")
        return success

    def test_admin_blog_delete(self):
        """Test DELETE /api/admin/blog/posts/{id}"""
        if not self.admin_token or not self.test_post_id_2:
            self.log("Skipping - no admin token or test post", "error")
            return False
        
        success, response = self.run_test(
            f"DELETE /api/admin/blog/posts/{self.test_post_id_2}",
            "DELETE",
            f"admin/blog/posts/{self.test_post_id_2}",
            200,
            token=self.admin_token
        )
        if success:
            deleted = response.get('deleted', False)
            self.log(f"Deleted: {deleted}", "info")
            # Verify post is gone
            verify_success, _ = self.run_test(
                f"GET /api/admin/blog/posts/{self.test_post_id_2} (verify deleted)",
                "GET",
                f"admin/blog/posts/{self.test_post_id_2}",
                404,
                token=self.admin_token
            )
            if not verify_success:
                self.log("ERROR: Post should return 404 after deletion", "error")
                return False
        return success

    def test_admin_blog_delete_no_auth(self):
        """Test DELETE /api/admin/blog/posts/{id} without auth (should 401/403)"""
        if not self.test_post_id:
            self.log("Skipping - no test post", "error")
            return False
        
        success, _ = self.run_test(
            "DELETE /api/admin/blog/posts/{id} (no auth → 401)",
            "DELETE",
            f"admin/blog/posts/{self.test_post_id}",
            401
        )
        return success

    # ===== CONTACT MESSAGES =====
    def test_contact_message_create(self):
        """Test POST /api/contact-messages (with consent)"""
        success, response = self.run_test(
            "POST /api/contact-messages (valid)",
            "POST",
            "contact-messages",
            201,
            data={
                "name": "Test User",
                "email": "test@example.com",
                "message": "This is a test message from automated testing",
                "consent": True
            }
        )
        if success:
            msg_id = response.get('id')
            self.log(f"Contact message created: {msg_id}", "info")
        return success

    def test_contact_message_no_consent(self):
        """Test POST /api/contact-messages without consent (should 400)"""
        success, _ = self.run_test(
            "POST /api/contact-messages (no consent → 400)",
            "POST",
            "contact-messages",
            400,
            data={
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message",
                "consent": False
            }
        )
        return success

    def test_contact_message_invalid_email(self):
        """Test POST /api/contact-messages with invalid email (should 422)"""
        success, _ = self.run_test(
            "POST /api/contact-messages (invalid email → 422)",
            "POST",
            "contact-messages",
            422,
            data={
                "name": "Test User",
                "email": "not-an-email",
                "message": "Test message",
                "consent": True
            }
        )
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("\n" + "="*70)
        print("🚀 TAMIS АГРО Backend API Testing - Blog Feature")
        print("="*70 + "\n")

        # Auth
        print("\n🔐 ADMIN AUTH")
        print("-" * 70)
        if not self.test_admin_login():
            print("\n❌ Admin login failed - cannot proceed with admin tests")
            return 1

        # Public blog endpoints
        print("\n📰 PUBLIC BLOG ENDPOINTS")
        print("-" * 70)
        self.test_blog_posts_list()
        self.test_blog_posts_filter_category()
        self.test_blog_posts_filter_tag()
        self.test_blog_posts_search()
        self.test_blog_posts_sort_newest()
        self.test_blog_posts_sort_oldest()
        self.test_blog_posts_sort_popular()
        self.test_blog_post_detail()
        self.test_blog_post_detail_404()
        self.test_blog_post_related()
        self.test_blog_categories()
        self.test_blog_tags()

        # Admin blog endpoints
        print("\n🔒 ADMIN BLOG ENDPOINTS")
        print("-" * 70)
        self.test_admin_blog_list_no_auth()
        self.test_admin_blog_list()
        self.test_admin_blog_create()
        self.test_admin_blog_create_duplicate_title()
        self.test_admin_blog_patch_title()
        self.test_admin_blog_patch_status_to_published()
        self.test_admin_blog_patch_toggle_hot()
        self.test_admin_blog_patch_tags()
        self.test_admin_blog_upload_image()
        self.test_admin_blog_delete()
        self.test_admin_blog_delete_no_auth()

        # Contact messages
        print("\n📧 CONTACT MESSAGES")
        print("-" * 70)
        self.test_contact_message_create()
        self.test_contact_message_no_consent()
        self.test_contact_message_invalid_email()

        # Summary
        print("\n" + "="*70)
        print(f"📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*70 + "\n")

        return 0 if self.tests_passed == self.tests_run else 1

class ProductsAPITester:
    """Test suite for Products module APIs"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.test_product_id = None
        self.test_product_slug = None
        self.test_category_id = None

    def log(self, msg: str, level: str = "info"):
        prefix = {
            "info": "ℹ️ ",
            "success": "✅",
            "error": "❌",
            "test": "🔍"
        }.get(level, "")
        print(f"{prefix} {msg}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data=None, headers=None, token=None, files=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        req_headers = {}
        if headers:
            req_headers.update(headers)
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        if not files and data is not None:
            req_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"Testing {name}...", "test")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=req_headers, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=req_headers, timeout=15)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=req_headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers, timeout=15)
            else:
                self.log(f"Unsupported method {method}", "error")
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"Passed - Status: {response.status_code}", "success")
            else:
                self.log(f"Failed - Expected {expected_status}, got {response.status_code}", "error")
                try:
                    self.log(f"Response: {response.json()}", "error")
                except:
                    self.log(f"Response text: {response.text[:300]}", "error")

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            self.log(f"Failed - Error: {str(e)}", "error")
            return False, {}

    # ===== AUTH =====
    def test_admin_login(self):
        """Test POST /api/auth/login with admin credentials"""
        success, response = self.run_test(
            "Admin login (admin@tamis.ua / admin1234)",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@tamis.ua", "password": "admin1234"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            user = response.get('user', {})
            self.log(f"Admin token obtained - role: {user.get('role')}", "info")
            if user.get('role') != 'admin':
                self.log("ERROR: User does not have admin role!", "error")
                return False
        return success

    # ===== PUBLIC PRODUCTS ENDPOINTS =====
    def test_products_list(self):
        """Test GET /api/products (public list)"""
        success, response = self.run_test(
            "GET /api/products (public list)",
            "GET",
            "products",
            200,
            params={"limit": 20}
        )
        if success:
            items = response.get('items', [])
            total = response.get('total', 0)
            self.log(f"Found {len(items)} products (total: {total})", "info")
            if items:
                # Store first product for detail test
                self.test_product_slug = items[0].get('slug')
                # Verify required fields
                p = items[0]
                required = ['id', 'slug', 'name', 'category', 'price', 'in_stock']
                for field in required:
                    if field not in p:
                        self.log(f"ERROR: Missing field '{field}' in product", "error")
                        return False
        return success

    def test_products_filter_category(self):
        """Test GET /api/products?category=biopesticide"""
        success, response = self.run_test(
            "GET /api/products?category=biopesticide",
            "GET",
            "products",
            200,
            params={"category": "biopesticide", "limit": 20}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} products in category 'biopesticide'", "info")
        return success

    def test_products_filter_stock(self):
        """Test GET /api/products?stock=in"""
        success, response = self.run_test(
            "GET /api/products?stock=in",
            "GET",
            "products",
            200,
            params={"stock": "in", "limit": 20}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} in-stock products", "info")
            # Verify all are in stock
            for p in items:
                if not p.get('in_stock'):
                    self.log(f"ERROR: Product {p.get('slug')} should be in stock", "error")
                    return False
        return success

    def test_products_search(self):
        """Test GET /api/products?q=text"""
        success, response = self.run_test(
            "GET /api/products?q=bio",
            "GET",
            "products",
            200,
            params={"q": "bio", "limit": 20}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Search 'bio' found {len(items)} products", "info")
        return success

    def test_products_sort_asc(self):
        """Test GET /api/products?sort=asc"""
        success, response = self.run_test(
            "GET /api/products?sort=asc",
            "GET",
            "products",
            200,
            params={"sort": "asc", "limit": 5}
        )
        if success:
            items = response.get('items', [])
            if len(items) >= 2:
                # Verify ascending price order
                prices = [p.get('price', 0) for p in items]
                if prices != sorted(prices):
                    self.log(f"WARNING: Prices not in ascending order: {prices}", "error")
        return success

    def test_products_sort_desc(self):
        """Test GET /api/products?sort=desc"""
        success, response = self.run_test(
            "GET /api/products?sort=desc",
            "GET",
            "products",
            200,
            params={"sort": "desc", "limit": 5}
        )
        return success

    def test_products_sort_new(self):
        """Test GET /api/products?sort=new"""
        success, response = self.run_test(
            "GET /api/products?sort=new",
            "GET",
            "products",
            200,
            params={"sort": "new", "limit": 5}
        )
        return success

    def test_products_sort_az(self):
        """Test GET /api/products?sort=az"""
        success, response = self.run_test(
            "GET /api/products?sort=az",
            "GET",
            "products",
            200,
            params={"sort": "az", "limit": 5}
        )
        return success

    def test_products_categories(self):
        """Test GET /api/products/categories"""
        success, response = self.run_test(
            "GET /api/products/categories",
            "GET",
            "products/categories",
            200
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} active categories", "info")
            for cat in items[:3]:
                self.log(f"  - {cat.get('label')} ({cat.get('slug')}): {cat.get('count', 0)} products", "info")
        return success

    def test_products_search_autocomplete(self):
        """Test GET /api/products/search?q=ven"""
        success, response = self.run_test(
            "GET /api/products/search?q=ven",
            "GET",
            "products/search",
            200,
            params={"q": "ven", "limit": 6}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Autocomplete 'ven' found {len(items)} products", "info")
        return success

    def test_products_detail(self):
        """Test GET /api/products/{slug}"""
        if not self.test_product_slug:
            self.log("Skipping - no test product slug", "error")
            return False
        
        success, response = self.run_test(
            f"GET /api/products/{self.test_product_slug}",
            "GET",
            f"products/{self.test_product_slug}",
            200
        )
        if success:
            # Verify full product structure
            required_tabs = ['dosage', 'composition', 'compatibility', 'specs']
            for tab in required_tabs:
                if tab not in response:
                    self.log(f"ERROR: Missing tab '{tab}' in product detail", "error")
                    return False
            self.log(f"Product detail includes all tabs: {', '.join(required_tabs)}", "info")
            
            # Verify description block structure
            if 'description' not in response:
                self.log("ERROR: Missing 'description' block in product detail", "error")
                return False
            desc = response['description']
            required_desc_fields = ['hero_image', 'title_line1', 'title_line2', 'title_subline', 'chips', 'problem', 'solution']
            for field in required_desc_fields:
                if field not in desc:
                    self.log(f"ERROR: Missing field '{field}' in description block", "error")
                    return False
            
            # Verify chips structure
            if not isinstance(desc['chips'], list):
                self.log("ERROR: description.chips should be a list", "error")
                return False
            self.log(f"Description block has {len(desc['chips'])} chips", "info")
            
            # Verify problem/solution structure
            problem = desc.get('problem', {})
            solution = desc.get('solution', {})
            if not problem.get('title') or not problem.get('intro_html'):
                self.log("ERROR: description.problem missing title or intro_html", "error")
                return False
            if not solution.get('title') or not solution.get('intro_html'):
                self.log("ERROR: description.solution missing title or intro_html", "error")
                return False
            self.log(f"Description block structure verified (problem + solution)", "info")
        return success

    def test_products_detail_404(self):
        """Test GET /api/products/nonexistent-slug (should 404)"""
        success, _ = self.run_test(
            "GET /api/products/nonexistent-slug (404)",
            "GET",
            "products/nonexistent-product-12345",
            404
        )
        return success

    def test_products_venator_full_description(self):
        """Test GET /api/products/venator - verify full description with chips and problem/solution"""
        success, response = self.run_test(
            "GET /api/products/venator (full description)",
            "GET",
            "products/venator",
            200
        )
        if success:
            # Verify description block exists
            if 'description' not in response:
                self.log("ERROR: Missing 'description' block in venator product", "error")
                return False
            
            desc = response['description']
            
            # Verify chips array has 3 items
            chips = desc.get('chips', [])
            if len(chips) != 3:
                self.log(f"ERROR: Expected 3 chips, got {len(chips)}", "error")
                return False
            self.log(f"Venator has {len(chips)} chips as expected", "info")
            
            # Verify each chip has required fields
            for i, chip in enumerate(chips):
                required_chip_fields = ['icon', 'title', 'body', 'variant']
                for field in required_chip_fields:
                    if field not in chip:
                        self.log(f"ERROR: Chip {i} missing field '{field}'", "error")
                        return False
            
            # Verify problem.intro_html is non-empty
            problem = desc.get('problem', {})
            intro_html = problem.get('intro_html', '')
            if not intro_html or len(intro_html.strip()) == 0:
                self.log("ERROR: description.problem.intro_html is empty", "error")
                return False
            self.log(f"Problem intro_html length: {len(intro_html)} chars", "info")
            
            # Verify solution.intro_html is non-empty
            solution = desc.get('solution', {})
            solution_intro = solution.get('intro_html', '')
            if not solution_intro or len(solution_intro.strip()) == 0:
                self.log("ERROR: description.solution.intro_html is empty", "error")
                return False
            self.log(f"Solution intro_html length: {len(solution_intro)} chars", "info")
            
            self.log("Venator product has complete description structure", "success")
        return success

    def test_products_related(self):
        """Test GET /api/products/{slug}/related"""
        if not self.test_product_slug:
            self.log("Skipping - no test product slug", "error")
            return False
        
        success, response = self.run_test(
            f"GET /api/products/{self.test_product_slug}/related",
            "GET",
            f"products/{self.test_product_slug}/related",
            200,
            params={"limit": 4}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} related products", "info")
        return success

    # ===== ADMIN PRODUCTS ENDPOINTS =====
    def test_admin_products_list_no_auth(self):
        """Test GET /api/admin/products without auth (should 401)"""
        success, _ = self.run_test(
            "GET /api/admin/products (no auth → 401)",
            "GET",
            "admin/products",
            401
        )
        return success

    def test_admin_products_list(self):
        """Test GET /api/admin/products (with admin auth)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        success, response = self.run_test(
            "GET /api/admin/products (admin)",
            "GET",
            "admin/products",
            200,
            token=self.admin_token
        )
        if success:
            items = response.get('items', [])
            total = response.get('total', 0)
            self.log(f"Admin sees {len(items)} products (total: {total})", "info")
            # Count drafts
            drafts = [p for p in items if p.get('status') == 'draft']
            self.log(f"  - {len(drafts)} drafts, {len(items) - len(drafts)} published", "info")
        return success

    def test_admin_products_create(self):
        """Test POST /api/admin/products (create product)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "POST /api/admin/products (create)",
            "POST",
            "admin/products",
            200,
            data={
                "name": f"Test Product {timestamp}",
                "short_desc": "Test product for automated testing",
                "category": "inoculant",
                "price": 299.99,
                "packing": "1, 5, 10 л",
                "norm": "1.5–2 л/га",
                "default_volume": "5 Л",
                "in_stock": True,
                "status": "draft"
            },
            token=self.admin_token
        )
        if success:
            self.test_product_id = response.get('id')
            self.test_product_slug = response.get('slug')
            self.log(f"Created product: id={self.test_product_id}, slug={self.test_product_slug}", "info")
        return success

    def test_admin_products_patch(self):
        """Test PATCH /api/admin/products/{id} (update product)"""
        if not self.admin_token or not self.test_product_id:
            self.log("Skipping - no admin token or test product", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/products/{id} (update price)",
            "PATCH",
            f"admin/products/{self.test_product_id}",
            200,
            data={"price": 349.99, "is_hit": True},
            token=self.admin_token
        )
        if success:
            new_price = response.get('price')
            is_hit = response.get('is_hit')
            self.log(f"Price updated to: {new_price}, is_hit: {is_hit}", "info")
        return success

    def test_admin_products_patch_tabs(self):
        """Test PATCH /api/admin/products/{id} (update nested tabs)"""
        if not self.admin_token or not self.test_product_id:
            self.log("Skipping - no admin token or test product", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/products/{id} (update dosage tab)",
            "PATCH",
            f"admin/products/{self.test_product_id}",
            200,
            data={
                "dosage": {
                    "title": "Дозування",
                    "intro": "Рекомендовані норми застосування",
                    "items": [
                        {"text": "Соя: 1.5–2 л/га"},
                        {"text": "Пшениця: 1–1.5 л/га"}
                    ],
                    "note": "Застосовувати перед посівом"
                }
            },
            token=self.admin_token
        )
        if success:
            dosage = response.get('dosage', {})
            items_count = len(dosage.get('items', []))
            self.log(f"Dosage tab updated with {items_count} items", "info")
        return success

    def test_admin_products_patch_description_partial(self):
        """Test PATCH /api/admin/products/{id} (partial description update - only title_line1)"""
        if not self.admin_token or not self.test_product_id:
            self.log("Skipping - no admin token or test product", "error")
            return False
        
        # First get the current product to verify description exists
        success_get, current = self.run_test(
            "GET /api/admin/products/{id} (before partial description update)",
            "GET",
            f"admin/products/{self.test_product_id}",
            200,
            token=self.admin_token
        )
        if not success_get:
            self.log("ERROR: Could not fetch product before update", "error")
            return False
        
        original_desc = current.get('description', {})
        original_title_line2 = original_desc.get('title_line2', '')
        original_chips = original_desc.get('chips', [])
        original_problem = original_desc.get('problem', {})
        
        # Now do a partial update - only change title_line1
        success, response = self.run_test(
            "PATCH /api/admin/products/{id} (partial description - only title_line1)",
            "PATCH",
            f"admin/products/{self.test_product_id}",
            200,
            data={
                "description": {
                    "title_line1": "Оновлений заголовок"
                }
            },
            token=self.admin_token
        )
        if success:
            new_desc = response.get('description', {})
            new_title_line1 = new_desc.get('title_line1', '')
            new_title_line2 = new_desc.get('title_line2', '')
            new_chips = new_desc.get('chips', [])
            new_problem = new_desc.get('problem', {})
            
            # Verify title_line1 was updated
            if new_title_line1 != "Оновлений заголовок":
                self.log(f"ERROR: title_line1 not updated, got: {new_title_line1}", "error")
                return False
            self.log(f"title_line1 updated successfully: {new_title_line1}", "info")
            
            # Verify other fields were preserved
            if new_title_line2 != original_title_line2:
                self.log(f"ERROR: title_line2 should be preserved, was '{original_title_line2}', now '{new_title_line2}'", "error")
                return False
            if len(new_chips) != len(original_chips):
                self.log(f"ERROR: chips array should be preserved, was {len(original_chips)}, now {len(new_chips)}", "error")
                return False
            if new_problem.get('intro_html') != original_problem.get('intro_html'):
                self.log("ERROR: problem.intro_html should be preserved", "error")
                return False
            
            self.log("Partial description update preserved other fields correctly", "success")
        return success

    def test_admin_products_upload_image(self):
        """Test POST /api/admin/products/upload-image (multipart file upload)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        # Create a small PNG image (1x1 red pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('test-product.png', io.BytesIO(png_data), 'image/png')}
        
        success, response = self.run_test(
            "POST /api/admin/products/upload-image (PNG)",
            "POST",
            "admin/products/upload-image",
            200,
            files=files,
            token=self.admin_token
        )
        if success:
            url = response.get('url', '')
            filename = response.get('filename', '')
            self.log(f"Uploaded: {filename}, URL: {url}", "info")
            # Verify URL starts with /api/uploads/products/
            if not url.startswith('/api/uploads/products/'):
                self.log(f"ERROR: URL should start with /api/uploads/products/, got: {url}", "error")
                return False
        return success

    def test_admin_products_delete(self):
        """Test DELETE /api/admin/products/{id}"""
        if not self.admin_token or not self.test_product_id:
            self.log("Skipping - no admin token or test product", "error")
            return False
        
        success, response = self.run_test(
            f"DELETE /api/admin/products/{self.test_product_id}",
            "DELETE",
            f"admin/products/{self.test_product_id}",
            200,
            token=self.admin_token
        )
        if success:
            deleted = response.get('deleted', False)
            self.log(f"Deleted: {deleted}", "info")
        return success

    # ===== ADMIN CATEGORIES ENDPOINTS =====
    def test_admin_categories_list(self):
        """Test GET /api/admin/product-categories"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        success, response = self.run_test(
            "GET /api/admin/product-categories",
            "GET",
            "admin/product-categories",
            200,
            token=self.admin_token
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} categories", "info")
        return success

    def test_admin_categories_create(self):
        """Test POST /api/admin/product-categories"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "POST /api/admin/product-categories (create)",
            "POST",
            "admin/product-categories",
            200,
            data={
                "slug": f"test-cat-{timestamp}",
                "label": f"Test Category {timestamp}",
                "sort_order": 999,
                "active": True
            },
            token=self.admin_token
        )
        if success:
            self.test_category_id = response.get('id')
            self.log(f"Created category: id={self.test_category_id}", "info")
        return success

    def test_admin_categories_patch(self):
        """Test PATCH /api/admin/product-categories/{id}"""
        if not self.admin_token or not self.test_category_id:
            self.log("Skipping - no admin token or test category", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/product-categories/{id}",
            "PATCH",
            f"admin/product-categories/{self.test_category_id}",
            200,
            data={"label": "Updated Test Category", "active": False},
            token=self.admin_token
        )
        if success:
            new_label = response.get('label')
            active = response.get('active')
            self.log(f"Category updated: label={new_label}, active={active}", "info")
        return success

    def test_admin_categories_delete(self):
        """Test DELETE /api/admin/product-categories/{id}"""
        if not self.admin_token or not self.test_category_id:
            self.log("Skipping - no admin token or test category", "error")
            return False
        
        success, response = self.run_test(
            f"DELETE /api/admin/product-categories/{self.test_category_id}",
            "DELETE",
            f"admin/product-categories/{self.test_category_id}",
            200,
            token=self.admin_token
        )
        if success:
            deleted = response.get('deleted', False)
            self.log(f"Deleted: {deleted}", "info")
        return success

    def test_admin_categories_reorder(self):
        """Test POST /api/admin/product-categories/reorder"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        # First get current categories
        _, list_response = self.run_test(
            "GET /api/admin/product-categories (for reorder)",
            "GET",
            "admin/product-categories",
            200,
            token=self.admin_token
        )
        items = list_response.get('items', [])
        if len(items) < 2:
            self.log("Not enough categories to test reorder", "info")
            return True
        
        # Reverse the order
        ids = [cat['id'] for cat in items]
        reversed_ids = list(reversed(ids))
        
        success, response = self.run_test(
            "POST /api/admin/product-categories/reorder",
            "POST",
            "admin/product-categories/reorder",
            200,
            data={"ids": reversed_ids},
            token=self.admin_token
        )
        if success:
            count = response.get('count', 0)
            self.log(f"Reordered {count} categories", "info")
        return success

    def run_all_tests(self):
        """Run all products API tests"""
        print("\n" + "="*70)
        print("🚀 TAMIS АГРО Backend API Testing - Products Module")
        print("="*70 + "\n")

        # Auth
        print("\n🔐 ADMIN AUTH")
        print("-" * 70)
        if not self.test_admin_login():
            print("\n❌ Admin login failed - cannot proceed with admin tests")
            return 1

        # Public products endpoints
        print("\n🛒 PUBLIC PRODUCTS ENDPOINTS")
        print("-" * 70)
        self.test_products_list()
        self.test_products_filter_category()
        self.test_products_filter_stock()
        self.test_products_search()
        self.test_products_sort_asc()
        self.test_products_sort_desc()
        self.test_products_sort_new()
        self.test_products_sort_az()
        self.test_products_categories()
        self.test_products_search_autocomplete()
        self.test_products_detail()
        self.test_products_detail_404()
        self.test_products_venator_full_description()
        self.test_products_related()

        # Admin products endpoints
        print("\n🔒 ADMIN PRODUCTS ENDPOINTS")
        print("-" * 70)
        self.test_admin_products_list_no_auth()
        self.test_admin_products_list()
        self.test_admin_products_create()
        self.test_admin_products_patch()
        self.test_admin_products_patch_tabs()
        self.test_admin_products_patch_description_partial()
        self.test_admin_products_upload_image()
        self.test_admin_products_delete()

        # Admin categories endpoints
        print("\n📁 ADMIN CATEGORIES ENDPOINTS")
        print("-" * 70)
        self.test_admin_categories_list()
        self.test_admin_categories_create()
        self.test_admin_categories_patch()
        self.test_admin_categories_reorder()
        self.test_admin_categories_delete()

        # Summary
        print("\n" + "="*70)
        print(f"📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*70 + "\n")

        return 0 if self.tests_passed == self.tests_run else 1


class OtherEndpointsTester:
    """Test suite for other endpoints (callback, cart, np, faq, cultures, partners, addresses)"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None

    def log(self, msg: str, level: str = "info"):
        prefix = {
            "info": "ℹ️ ",
            "success": "✅",
            "error": "❌",
            "test": "🔍"
        }.get(level, "")
        print(f"{prefix} {msg}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data=None, headers=None, token=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        req_headers = {}
        if headers:
            req_headers.update(headers)
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        if data is not None:
            req_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"Testing {name}...", "test")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers, timeout=15)
            else:
                self.log(f"Unsupported method {method}", "error")
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"Passed - Status: {response.status_code}", "success")
            else:
                self.log(f"Failed - Expected {expected_status}, got {response.status_code}", "error")
                try:
                    self.log(f"Response: {response.json()}", "error")
                except:
                    self.log(f"Response text: {response.text[:300]}", "error")

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            self.log(f"Failed - Error: {str(e)}", "error")
            return False, {}

    def test_admin_login(self):
        """Test POST /api/auth/login with admin credentials"""
        success, response = self.run_test(
            "Admin login (admin@tamis.ua / admin1234)",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@tamis.ua", "password": "admin1234"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
        return success

    def test_callback_create(self):
        """Test POST /api/callbacks (create callback request)"""
        success, response = self.run_test(
            "POST /api/callbacks",
            "POST",
            "callbacks",
            201,
            data={
                "name": "Test User",
                "phone": "+380501234567",
                "consent": True
            }
        )
        if success:
            self.log(f"Callback created: {response.get('id')}", "info")
        return success

    def test_faq_list(self):
        """Test GET /api/faq"""
        success, response = self.run_test(
            "GET /api/faq",
            "GET",
            "faq",
            200
        )
        if success:
            # Response is a list directly
            if isinstance(response, list):
                self.log(f"Found {len(response)} FAQ items", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_cultures_list(self):
        """Test GET /api/cultures"""
        success, response = self.run_test(
            "GET /api/cultures",
            "GET",
            "cultures",
            200
        )
        if success:
            # Response is a list directly
            if isinstance(response, list):
                self.log(f"Found {len(response)} cultures", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_trusted_partners_list(self):
        """Test GET /api/trusted-partners"""
        success, response = self.run_test(
            "GET /api/trusted-partners",
            "GET",
            "trusted-partners",
            200
        )
        if success:
            # Response is a list directly
            if isinstance(response, list):
                self.log(f"Found {len(response)} trusted partners", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_np_cities_search(self):
        """Test GET /api/np/cities?q=Київ"""
        success, response = self.run_test(
            "GET /api/np/cities?q=Київ",
            "GET",
            "np/cities",
            200,
            params={"q": "Київ"}
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} cities matching 'Київ'", "info")
        return success

    def test_cart_create(self):
        """Test GET /api/cart/{session_id} (get cart)"""
        success, response = self.run_test(
            "GET /api/cart/test-session-123",
            "GET",
            "cart/test-session-123",
            200
        )
        if success:
            self.log(f"Cart retrieved", "info")
        return success

    def test_addresses_list(self):
        """Test GET /api/addresses/{session_id}"""
        success, response = self.run_test(
            "GET /api/addresses/test-session-123",
            "GET",
            "addresses/test-session-123",
            200
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} addresses", "info")
        return success

    def run_all_tests(self):
        """Run all other endpoints tests"""
        print("\n" + "="*70)
        print("🚀 TAMIS АГРО Backend API Testing - Other Endpoints")
        print("="*70 + "\n")

        # Auth
        print("\n🔐 ADMIN AUTH")
        print("-" * 70)
        self.test_admin_login()

        # Other endpoints
        print("\n🔧 OTHER ENDPOINTS (smoke tests)")
        print("-" * 70)
        self.test_callback_create()
        self.test_faq_list()
        self.test_cultures_list()
        self.test_trusted_partners_list()
        self.test_np_cities_search()
        self.test_cart_create()
        self.test_addresses_list()

        # Summary
        print("\n" + "="*70)
        print(f"📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*70 + "\n")

        return 0 if self.tests_passed == self.tests_run else 1



class ReviewsAPITester:
    """Test suite for Reviews module APIs"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.test_review_id = None

    def log(self, msg: str, level: str = "info"):
        prefix = {
            "info": "ℹ️ ",
            "success": "✅",
            "error": "❌",
            "test": "🔍"
        }.get(level, "")
        print(f"{prefix} {msg}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data=None, headers=None, token=None, files=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        req_headers = {}
        if headers:
            req_headers.update(headers)
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        if not files and data is not None:
            req_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"Testing {name}...", "test")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=req_headers, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=req_headers, timeout=15)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=req_headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=req_headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers, timeout=15)
            else:
                self.log(f"Unsupported method {method}", "error")
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"Passed - Status: {response.status_code}", "success")
            else:
                self.log(f"Failed - Expected {expected_status}, got {response.status_code}", "error")
                try:
                    self.log(f"Response: {response.json()}", "error")
                except:
                    self.log(f"Response text: {response.text[:300]}", "error")

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            self.log(f"Failed - Error: {str(e)}", "error")
            return False, {}

    # ===== AUTH =====
    def test_admin_login(self):
        """Test POST /api/auth/login with admin credentials"""
        success, response = self.run_test(
            "Admin login (admin@tamis.ua / admin1234)",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@tamis.ua", "password": "admin1234"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            user = response.get('user', {})
            self.log(f"Admin token obtained - role: {user.get('role')}", "info")
            if user.get('role') != 'admin':
                self.log("ERROR: User does not have admin role!", "error")
                return False
        return success

    # ===== PUBLIC REVIEWS ENDPOINTS =====
    def test_reviews_list(self):
        """Test GET /api/reviews (returns published reviews, default seed = 5 highlighted)"""
        success, response = self.run_test(
            "GET /api/reviews (public list)",
            "GET",
            "reviews",
            200,
            params={"limit": 100}
        )
        if success:
            if isinstance(response, list):
                items = response
                self.log(f"Found {len(items)} published reviews", "info")
                # Verify at least 5 reviews (default seed)
                if len(items) < 5:
                    self.log(f"ERROR: Expected at least 5 reviews (default seed), got {len(items)}", "error")
                    return False
                # Count highlighted reviews
                highlighted = [r for r in items if r.get('highlighted')]
                self.log(f"  - {len(highlighted)} highlighted reviews", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_reviews_filter_product_slug_venator(self):
        """Test GET /api/reviews?product_slug=venator (returns >=3 reviews tied to Венатор)"""
        success, response = self.run_test(
            "GET /api/reviews?product_slug=venator",
            "GET",
            "reviews",
            200,
            params={"product_slug": "venator", "limit": 100}
        )
        if success:
            if isinstance(response, list):
                items = response
                self.log(f"Found {len(items)} reviews for product 'venator'", "info")
                # Verify at least 3 reviews for venator
                if len(items) < 3:
                    self.log(f"ERROR: Expected at least 3 reviews for venator, got {len(items)}", "error")
                    return False
                # Verify all have product_slug=venator
                for r in items:
                    if r.get('product_slug') != 'venator':
                        self.log(f"ERROR: Review {r.get('id')} has wrong product_slug: {r.get('product_slug')}", "error")
                        return False
                # Verify product_name is cached as 'Венатор'
                if items and items[0].get('product_name'):
                    self.log(f"  - Product name cached: {items[0].get('product_name')}", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_reviews_filter_highlighted(self):
        """Test GET /api/reviews?highlighted=true (returns only 5 highlighted)"""
        success, response = self.run_test(
            "GET /api/reviews?highlighted=true",
            "GET",
            "reviews",
            200,
            params={"highlighted": "true", "limit": 100}
        )
        if success:
            if isinstance(response, list):
                items = response
                self.log(f"Found {len(items)} highlighted reviews", "info")
                # Verify exactly 5 highlighted reviews (default seed)
                if len(items) != 5:
                    self.log(f"WARNING: Expected 5 highlighted reviews (default seed), got {len(items)}", "error")
                # Verify all are highlighted
                for r in items:
                    if not r.get('highlighted'):
                        self.log(f"ERROR: Review {r.get('id')} should be highlighted", "error")
                        return False
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_products_categories_includes_adjuvant(self):
        """Test GET /api/products/categories includes 6 categories including 'adjuvant' with label 'Допоміжні речовини'"""
        success, response = self.run_test(
            "GET /api/products/categories (verify adjuvant category)",
            "GET",
            "products/categories",
            200
        )
        if success:
            items = response.get('items', [])
            self.log(f"Found {len(items)} active categories", "info")
            # Verify at least 6 categories
            if len(items) < 6:
                self.log(f"ERROR: Expected at least 6 categories, got {len(items)}", "error")
                return False
            # Find adjuvant category
            adjuvant = next((c for c in items if c.get('slug') == 'adjuvant'), None)
            if not adjuvant:
                self.log("ERROR: Category 'adjuvant' not found", "error")
                return False
            # Verify label
            if adjuvant.get('label') != 'Допоміжні речовини':
                self.log(f"ERROR: Expected label 'Допоміжні речовини', got '{adjuvant.get('label')}'", "error")
                return False
            self.log(f"  - Found adjuvant category: {adjuvant.get('label')}", "info")
        return success

    # ===== ADMIN REVIEWS ENDPOINTS =====
    def test_admin_reviews_list_no_auth(self):
        """Test GET /api/admin/reviews without auth (should 401)"""
        success, _ = self.run_test(
            "GET /api/admin/reviews (no auth → 401)",
            "GET",
            "admin/reviews",
            401
        )
        return success

    def test_admin_reviews_list(self):
        """Test GET /api/admin/reviews (with admin auth)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        success, response = self.run_test(
            "GET /api/admin/reviews (admin)",
            "GET",
            "admin/reviews",
            200,
            token=self.admin_token
        )
        if success:
            if isinstance(response, list):
                items = response
                self.log(f"Admin sees {len(items)} reviews (all statuses)", "info")
                # Count published/unpublished
                published = [r for r in items if r.get('published')]
                self.log(f"  - {len(published)} published, {len(items) - len(published)} unpublished", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_admin_reviews_create(self):
        """Test POST /api/admin/reviews (create review with product_slug='venator')"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "POST /api/admin/reviews (create with product_slug='venator')",
            "POST",
            "admin/reviews",
            200,
            data={
                "author_name": f"Test Reviewer {timestamp}",
                "author_role": "Test Farm",
                "author_photo": "/image4@2x.webp",
                "category": "Родентициди",
                "body": "This is a test review created by automated testing for Venator product.",
                "rating": 5,
                "display_date": "Грудень 2024",
                "product_slug": "venator",
                "published": True,
                "highlighted": False
            },
            token=self.admin_token
        )
        if success:
            self.test_review_id = response.get('id')
            product_name = response.get('product_name')
            self.log(f"Created review: id={self.test_review_id}", "info")
            # Verify product_name is cached as 'Венатор'
            if product_name != 'Венатор':
                self.log(f"ERROR: Expected product_name='Венатор', got '{product_name}'", "error")
                return False
            self.log(f"  - Product name cached correctly: {product_name}", "info")
        return success

    def test_admin_reviews_patch(self):
        """Test PATCH /api/admin/reviews/{id} (update fields)"""
        if not self.admin_token or not self.test_review_id:
            self.log("Skipping - no admin token or test review", "error")
            return False
        
        success, response = self.run_test(
            "PATCH /api/admin/reviews/{id} (update rating)",
            "PATCH",
            f"admin/reviews/{self.test_review_id}",
            200,
            data={"rating": 4, "highlighted": True},
            token=self.admin_token
        )
        if success:
            new_rating = response.get('rating')
            highlighted = response.get('highlighted')
            self.log(f"Rating updated to: {new_rating}, highlighted: {highlighted}", "info")
        return success

    def test_admin_reviews_reorder(self):
        """Test PUT /api/admin/reviews/reorder (reorder reviews)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        # First get current reviews
        _, list_response = self.run_test(
            "GET /api/admin/reviews (for reorder)",
            "GET",
            "admin/reviews",
            200,
            token=self.admin_token
        )
        if isinstance(list_response, list):
            items = list_response
        else:
            self.log("ERROR: Expected list response", "error")
            return False
        
        if len(items) < 2:
            self.log("Not enough reviews to test reorder", "info")
            return True
        
        # Reverse the order
        ids = [r['id'] for r in items]
        reversed_ids = list(reversed(ids))
        
        success, response = self.run_test(
            "PUT /api/admin/reviews/reorder",
            "PUT",
            "admin/reviews/reorder",
            200,
            data={"ids": reversed_ids},
            token=self.admin_token
        )
        if success:
            if isinstance(response, list):
                self.log(f"Reordered {len(response)} reviews", "info")
            else:
                self.log("ERROR: Expected list response", "error")
                return False
        return success

    def test_admin_reviews_upload_image(self):
        """Test POST /api/admin/reviews/upload-image (accepts image, returns URL starting with /api/uploads/reviews/)"""
        if not self.admin_token:
            self.log("Skipping - no admin token", "error")
            return False
        
        # Create a small PNG image (1x1 red pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('test-review.png', io.BytesIO(png_data), 'image/png')}
        
        success, response = self.run_test(
            "POST /api/admin/reviews/upload-image (PNG)",
            "POST",
            "admin/reviews/upload-image",
            200,
            files=files,
            token=self.admin_token
        )
        if success:
            url = response.get('url', '')
            filename = response.get('filename', '')
            self.log(f"Uploaded: {filename}, URL: {url}", "info")
            # Verify URL starts with /api/uploads/reviews/
            if not url.startswith('/api/uploads/reviews/'):
                self.log(f"ERROR: URL should start with /api/uploads/reviews/, got: {url}", "error")
                return False
        return success

    def test_admin_reviews_delete(self):
        """Test DELETE /api/admin/reviews/{id}"""
        if not self.admin_token or not self.test_review_id:
            self.log("Skipping - no admin token or test review", "error")
            return False
        
        success, response = self.run_test(
            f"DELETE /api/admin/reviews/{self.test_review_id}",
            "DELETE",
            f"admin/reviews/{self.test_review_id}",
            200,
            token=self.admin_token
        )
        if success:
            deleted = response.get('deleted', 0)
            self.log(f"Deleted: {deleted} review(s)", "info")
        return success

    def run_all_tests(self):
        """Run all reviews API tests"""
        print("\n" + "="*70)
        print("🚀 TAMIS АГРО Backend API Testing - Reviews Module")
        print("="*70 + "\n")

        # Auth
        print("\n🔐 ADMIN AUTH")
        print("-" * 70)
        if not self.test_admin_login():
            print("\n❌ Admin login failed - cannot proceed with admin tests")
            return 1

        # Public reviews endpoints
        print("\n⭐ PUBLIC REVIEWS ENDPOINTS")
        print("-" * 70)
        self.test_reviews_list()
        self.test_reviews_filter_product_slug_venator()
        self.test_reviews_filter_highlighted()
        self.test_products_categories_includes_adjuvant()

        # Admin reviews endpoints
        print("\n🔒 ADMIN REVIEWS ENDPOINTS")
        print("-" * 70)
        self.test_admin_reviews_list_no_auth()
        self.test_admin_reviews_list()
        self.test_admin_reviews_create()
        self.test_admin_reviews_patch()
        self.test_admin_reviews_reorder()
        self.test_admin_reviews_upload_image()
        self.test_admin_reviews_delete()

        # Summary
        print("\n" + "="*70)
        print(f"📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*70 + "\n")

        return 0 if self.tests_passed == self.tests_run else 1


def main():
    print("\n" + "="*80)
    print("🧪 TAMIS АГРО - COMPREHENSIVE BACKEND API TESTING")
    print("="*80)
    
    # Test Reviews Module (NEW FEATURE)
    reviews_tester = ReviewsAPITester()
    reviews_result = reviews_tester.run_all_tests()
    
    # Overall summary
    total_tests = reviews_tester.tests_run
    total_passed = reviews_tester.tests_passed
    
    print("\n" + "="*80)
    print("🎯 OVERALL SUMMARY")
    print("="*80)
    print(f"Reviews Module: {reviews_tester.tests_passed}/{reviews_tester.tests_run} passed")
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print("="*80 + "\n")
    
    return 0 if total_passed == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
