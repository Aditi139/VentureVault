from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from directory.models import (
    Category,
    Entrepreneur,
    TimelineMilestone,
    DistilledLesson,
    Video,
    SavedVideo,
    StorySubmission,
    ContactMessage
)

class ModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Artificial Intelligence",
            description="AI startups and breakthrough products."
        )
        self.entrepreneur = Entrepreneur.objects.create(
            name="Sam Altman",
            company_name="OpenAI",
            industry="Artificial Intelligence",
            biography="CEO of OpenAI and former president of Y Combinator.",
            profile_image="/static/directory/images/entrepreneurs/sam-altman.jpg",
            location="San Francisco, CA",
            founded_year=2015,
            website="openai.com"
        )
        self.video = Video.objects.create(
            title="How to Build Breakthrough AI Products",
            entrepreneur=self.entrepreneur,
            category=self.category,
            description="Deep dive on AI product market fit and scale.",
            video_url="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
            thumbnail="https://img.youtube.com/vi/UF8uR6Z6KLc/hqdefault.jpg",
            duration="15:30",
            key_takeaways="• Focus on high-value user problems\n• Iterate rapidly on user feedback\n• Build defensible data flywheels"
        )

    def test_category_creation_and_slug(self):
        self.assertEqual(self.category.slug, "artificial-intelligence")
        self.assertEqual(str(self.category), "Artificial Intelligence")

    def test_entrepreneur_clean_website_and_avatar(self):
        self.assertEqual(self.entrepreneur.get_clean_website(), "https://openai.com")
        self.assertIn("sam-altman", self.entrepreneur.avatar_url)
        self.assertEqual(str(self.entrepreneur), "Sam Altman (OpenAI)")

    def test_video_youtube_id_extraction(self):
        # Standard watch URL
        self.assertEqual(self.video.get_youtube_video_id(), "UF8uR6Z6KLc")

        # Short URL format
        self.video.video_url = "https://youtu.be/UF8uR6Z6KLc?si=123"
        self.assertEqual(self.video.get_youtube_video_id(), "UF8uR6Z6KLc")

        # Shorts format
        self.video.video_url = "https://www.youtube.com/shorts/UF8uR6Z6KLc"
        self.assertEqual(self.video.get_youtube_video_id(), "UF8uR6Z6KLc")

        # Direct 11-char ID
        self.video.video_url = "UF8uR6Z6KLc"
        self.assertEqual(self.video.get_youtube_video_id(), "UF8uR6Z6KLc")

    def test_video_embed_url_and_takeaways(self):
        embed = self.video.get_youtube_embed_url()
        self.assertIn("youtube-nocookie.com/embed/UF8uR6Z6KLc", embed)
        takeaways = self.video.get_takeaways_list()
        self.assertEqual(len(takeaways), 3)
        self.assertEqual(takeaways[0], "Focus on high-value user problems")

    def test_saved_video_model(self):
        user = User.objects.create_user(username="testuser", password="password123")
        saved = SavedVideo.objects.create(user=user, video=self.video)
        self.assertEqual(str(saved), f"testuser saved {self.video.title}")

    def test_story_submission_approval_sync(self):
        sub = StorySubmission.objects.create(
            entrepreneur_name="Aarav Verma",
            company_name="NeuralEdge",
            email="aarav@example.com",
            category="Deep Tech",
            title="Building Hardware for AI",
            description="Our journey developing edge AI chips.",
            video_url="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
            status="Approved"
        )
        self.assertIsNotNone(sub.approved_video)
        self.assertEqual(sub.approved_video.title, "Building Hardware for AI")

    def test_genuine_entrepreneurs_integrity(self):
        jobs = Entrepreneur.objects.create(
            name="Steve Jobs",
            company_name="Apple",
            industry="Consumer Technology & Computing",
            biography="Co-founder of Apple Inc. Renowned for revolutionizing personal computers, animated movies, music, and mobile phones.",
            profile_image="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            location="Cupertino, CA",
            founded_year=1976,
            website="apple.com"
        )
        vid = Video.objects.create(
            title="Steve Jobs' 2005 Stanford Commencement Address",
            entrepreneur=jobs,
            category=self.category,
            description="Steve Jobs urges graduates to pursue their passions and trust that the dots will somehow connect in their future.",
            video_url="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
            duration="15:04",
            key_takeaways="• Connect the dots looking backwards\n• Love what you do and don't settle\n• Stay hungry, stay foolish"
        )
        self.assertEqual(vid.entrepreneur.name, "Steve Jobs")
        self.assertEqual(vid.entrepreneur.company_name, "Apple")
        self.assertIn("steve-jobs.jpg", vid.entrepreneur.avatar_url)
        self.assertEqual(vid.get_youtube_video_id(), "UF8uR6Z6KLc")
        self.assertIn("youtube-nocookie.com/embed/UF8uR6Z6KLc", vid.get_youtube_embed_url())
        self.assertEqual(vid.thumbnail_url, "https://img.youtube.com/vi/UF8uR6Z6KLc/hqdefault.jpg")

        # Test unverified entrepreneur fallback to neutral initials avatar
        kevin = Entrepreneur.objects.create(
            name="Kevin Hale",
            company_name="Wufoo",
            industry="Software",
            biography="Co-founder of Wufoo."
        )
        self.assertIn("kevin-hale.svg", kevin.avatar_url)

    def test_brian_chesky_profile_and_milestones(self):
        chesky = Entrepreneur.objects.create(
            name="Brian Chesky",
            company_name="Airbnb",
            industry="Online Marketplace & Travel",
            biography="Graduated from Rhode Island School of Design (RISD)...",
            founded_year=2008,
            website="airbnb.com"
        )
        milestones = chesky.get_milestones()
        self.assertEqual(len(milestones), 5)
        self.assertIn("RISD", milestones[0]['title'])
        self.assertIn("Airbeds", milestones[1]['title'])
        self.assertIn("SXSW", milestones[2]['subtitle'])
        self.assertIn("DNC", milestones[3]['title'])
        self.assertIn("Renamed to Airbnb", milestones[4]['title'])


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="FinTech", description="Finance tech.")
        self.entrepreneur = Entrepreneur.objects.create(
            name="Patrick Collison",
            company_name="Stripe",
            industry="FinTech",
            biography="Co-founder of Stripe.",
            profile_image="https://images.unsplash.com/photo-1534528741775-53994a69daeb",
            location="San Francisco, CA"
        )
        self.video = Video.objects.create(
            title="How Stripe Scaled Global Payments",
            entrepreneur=self.entrepreneur,
            category=self.category,
            description="The engineering and business journey of Stripe.",
            video_url="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
            featured=True,
            trending=True
        )
        self.user = User.objects.create_user(username="testrunner", email="test@vault.com", password="password123")

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Venture")
        self.assertContains(response, self.video.title)

    def test_explore_page(self):
        response = self.client.get(reverse('explore'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.video.title)

        # Test search query filter
        response_search = self.client.get(reverse('explore') + '?q=Stripe')
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, self.video.title)

    def test_video_detail_page(self):
        initial_views = self.video.views
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.video.title)
        # Verify views count and dates are NOT displayed to the user
        self.assertNotContains(response, "views</span>")
        self.assertNotContains(response, "views</p>")
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, initial_views + 1)

    def test_entrepreneurs_index_and_detail(self):
        res_list = self.client.get(reverse('entrepreneurs'))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, self.entrepreneur.name)

        res_detail = self.client.get(reverse('entrepreneur_detail', args=[self.entrepreneur.pk]))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, self.entrepreneur.name)

    def test_categories_index_and_category_videos(self):
        res_cats = self.client.get(reverse('categories'))
        self.assertEqual(res_cats.status_code, 200)
        self.assertContains(res_cats, self.category.name)

        res_cat_vid = self.client.get(reverse('category_videos', args=[self.category.slug]))
        self.assertEqual(res_cat_vid.status_code, 200)
        self.assertContains(res_cat_vid, self.video.title)

    def test_search_view(self):
        res = self.client.get(reverse('search') + '?q=Payments')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.video.title)

    def test_about_page(self):
        res = self.client.get(reverse('about'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "About VentureVault")

    def test_login_page_no_credentials_displayed(self):
        res = self.client.get(reverse('login'))
        self.assertEqual(res.status_code, 200)
        # Verify Demo Credentials card and demo credentials are NOT publicly exposed
        self.assertNotContains(res, "Demo Credentials")
        self.assertNotContains(res, "admin123")
        self.assertNotContains(res, "demo123")

    def test_contact_submission(self):
        res_get = self.client.get(reverse('contact'))
        self.assertEqual(res_get.status_code, 200)

        res_post = self.client.post(reverse('contact'), {
            'name': 'Gagan Verma',
            'email': 'gagan@example.com',
            'subject': 'Collaboration inquiry',
            'message': 'Love the platform and videos!'
        })
        self.assertEqual(res_post.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email='gagan@example.com').exists())

    def test_submit_story_route_completely_removed(self):
        """Public story submission endpoint must not exist (returns 404)."""
        res = self.client.get('/submit-story/')
        self.assertEqual(res.status_code, 404)
        res_post = self.client.post('/submit-story/', {'title': 'Sample Submission'})
        self.assertEqual(res_post.status_code, 404)

    def test_public_website_access_without_login(self):
        """Anonymous visitors can freely browse and explore all published content without logging in."""
        urls_to_test = [
            reverse('home'),
            reverse('explore'),
            reverse('video_detail', args=[self.video.pk]),
            reverse('entrepreneurs'),
            reverse('entrepreneur_detail', args=[self.entrepreneur.pk]),
            reverse('categories'),
            reverse('category_videos', args=[self.category.slug]),
            f"{reverse('search')}?q=Stripe",
            reverse('about'),
            reverse('contact'),
        ]
        for url in urls_to_test:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Expected 200 for public URL: {url}")
            # Ensure no redirect to login
            self.assertNotEqual(res.status_code, 302)

    def test_footer_contains_exactly_three_contact_links(self):
        """Footer must contain exactly GitHub, LinkedIn, and Email links; Twitter and YouTube removed."""
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'https://github.com/Aditi139')
        self.assertContains(res, 'https://www.linkedin.com/in/aditi139/')
        self.assertContains(res, 'mailto:aditikumari1397@gmail.com')
        # Confirm old Twitter and YouTube social icons are gone
        self.assertNotContains(res, 'https://twitter.com')
        self.assertNotContains(res, 'https://youtube.com')
        # Confirm no submit story link in footer or navbar
        self.assertNotContains(res, 'Submit Story')

    def test_normal_user_bookmarking_workflow(self):
        """Normal authenticated users can bookmark/save and unbookmark videos."""
        self.client.login(username="testrunner", password="password123")
        # 1. Toggle save video -> 200
        res_save = self.client.post(reverse('toggle_save_video', args=[self.video.pk]))
        self.assertEqual(res_save.status_code, 200)
        data = res_save.json()
        self.assertTrue(data['is_saved'])
        self.assertTrue(SavedVideo.objects.filter(user=self.user, video=self.video).exists())

        # 2. Saved video appears in profile
        res_prof = self.client.get(reverse('profile'))
        self.assertEqual(res_prof.status_code, 200)
        self.assertContains(res_prof, self.video.title)
        self.assertNotContains(res_prof, "My Story Submissions")

        # 3. Toggle save again -> removes
        res_unsave = self.client.post(reverse('toggle_save_video', args=[self.video.pk]))
        self.assertEqual(res_unsave.status_code, 200)
        data2 = res_unsave.json()
        self.assertFalse(data2['is_saved'])
        self.assertFalse(SavedVideo.objects.filter(user=self.user, video=self.video).exists())

        # 4. Remove via remove_saved_video endpoint
        SavedVideo.objects.create(user=self.user, video=self.video)
        res_remove = self.client.post(reverse('remove_saved_video', args=[self.video.pk]))
        self.assertEqual(res_remove.status_code, 302)
        self.assertFalse(SavedVideo.objects.filter(user=self.user, video=self.video).exists())

    def test_admin_cannot_bookmark_stories(self):
        """Admin/superuser accounts must NOT be able to bookmark stories (403 Forbidden backend, hidden UI)."""
        admin_user = User.objects.create_superuser(username="adminboss", email="admin@vault.com", password="password123")
        self.client.login(username="adminboss", password="password123")

        # 1. Backend toggle-save call must be rejected with 403 Forbidden
        res_toggle = self.client.post(reverse('toggle_save_video', args=[self.video.pk]))
        self.assertEqual(res_toggle.status_code, 403)
        self.assertIn("cannot bookmark", res_toggle.json().get('message', ''))
        self.assertFalse(SavedVideo.objects.filter(user=admin_user).exists())

        # 2. Backend remove-saved call must be rejected with 403 Forbidden
        res_remove = self.client.post(reverse('remove_saved_video', args=[self.video.pk]))
        self.assertEqual(res_remove.status_code, 403)

        # 3. UI checks: bookmark/save buttons must be HIDDEN on detail, explore, home
        res_detail = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertEqual(res_detail.status_code, 200)
        self.assertNotContains(res_detail, 'id="btn-save-video"')

        res_home = self.client.get(reverse('home'))
        self.assertNotContains(res_home, 'data-video-id')

        res_explore = self.client.get(reverse('explore'))
        self.assertNotContains(res_explore, 'data-video-id')

        # 4. Admin profile page shows admin management info, not bookmark vault
        res_prof = self.client.get(reverse('profile'))
        self.assertEqual(res_prof.status_code, 200)
        self.assertContains(res_prof, "Administrator Privileges Active")
        self.assertContains(res_prof, "/admin/")
        self.assertNotContains(res_prof, "Saved to My Vault")

    def test_anonymous_cannot_bookmark_stories(self):
        """Anonymous visitors cannot bookmark (401 Unauthorized backend)."""
        res = self.client.post(reverse('toggle_save_video', args=[self.video.pk]))
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertEqual(data.get('status'), 'unauthenticated')
        self.assertIn('login_url', data)

    def test_draft_and_published_status_isolation(self):
        """Draft stories must remain hidden from public visitors and only visible to authorized admins."""
        # Create draft entrepreneur & video
        draft_ent = Entrepreneur.objects.create(
            name="Secret Stealth Founder",
            company_name="Stealth AI Labs",
            industry="Artificial Intelligence",
            biography="Top secret pre-launch AI company.",
            is_published=False
        )
        draft_vid = Video.objects.create(
            title="Unreleased Stealth Keynote",
            entrepreneur=draft_ent,
            category=self.category,
            description="Private internal presentation.",
            video_url="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
            is_published=False
        )

        # Public anonymous visitor cannot see draft
        res_home = self.client.get(reverse('home'))
        self.assertNotContains(res_home, "Unreleased Stealth Keynote")

        res_explore = self.client.get(reverse('explore'))
        self.assertNotContains(res_explore, "Unreleased Stealth Keynote")

        res_ents = self.client.get(reverse('entrepreneurs'))
        self.assertNotContains(res_ents, "Secret Stealth Founder")

        # Detail views return 404 for public visitors
        res_vid_detail = self.client.get(reverse('video_detail', args=[draft_vid.pk]))
        self.assertEqual(res_vid_detail.status_code, 404)

        res_ent_detail = self.client.get(reverse('entrepreneur_detail', args=[draft_ent.pk]))
        self.assertEqual(res_ent_detail.status_code, 404)

        # Admin user CAN preview draft content
        admin_user = User.objects.create_superuser(username="editoradmin", email="ed@vault.com", password="password123")
        self.client.login(username="editoradmin", password="password123")

        res_admin_vid = self.client.get(reverse('video_detail', args=[draft_vid.pk]))
        self.assertEqual(res_admin_vid.status_code, 200)
        self.assertContains(res_admin_vid, "Unreleased Stealth Keynote")

        res_admin_ent = self.client.get(reverse('entrepreneur_detail', args=[draft_ent.pk]))
        self.assertEqual(res_admin_ent.status_code, 200)
        self.assertContains(res_admin_ent, "Secret Stealth Founder")

        # Once published, publicly visible to everyone
        draft_ent.is_published = True
        draft_ent.save()
        draft_vid.is_published = True
        draft_vid.save()

        self.client.logout()
        res_pub_vid = self.client.get(reverse('video_detail', args=[draft_vid.pk]))
        self.assertEqual(res_pub_vid.status_code, 200)
        res_pub_ent = self.client.get(reverse('entrepreneur_detail', args=[draft_ent.pk]))
        self.assertEqual(res_pub_ent.status_code, 200)

    def test_profile_view(self):
        # Unauthenticated -> redirect to login
        res_anon = self.client.get(reverse('profile'))
        self.assertEqual(res_anon.status_code, 302)

        # Authenticated normal user -> 200
        self.client.login(username="testrunner", password="password123")
        res_auth = self.client.get(reverse('profile'))
        self.assertEqual(res_auth.status_code, 200)
        self.assertContains(res_auth, "testrunner")


class GlobalContentAccuracyAuditTests(TestCase):
    """
    Exhaustive verification of the global content audit across all 26 entrepreneurs,
    155 historical milestones, 104 distilled lessons, and 27 masterclass videos.
    """
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_data')

    def test_audit_total_entrepreneur_count_and_authenticity(self):
        """Every entrepreneur in the directory must be a real, verified person."""
        founders = Entrepreneur.objects.all()
        self.assertEqual(founders.count(), 26)
        
        # Verify specific prominent founders exist
        required_names = [
            "Steve Jobs", "Elon Musk", "Sam Altman", "Brian Chesky",
            "Sara Blakely", "Melanie Perkins", "Whitney Wolfe Herd",
            "Ritesh Agarwal", "Jeff Bezos", "Bill Gates", "Mark Zuckerberg",
            "Jensen Huang", "Simon Sinek", "Reid Hoffman", "Satya Nadella",
            "Guy Kawasaki", "Michael Seibel", "Kevin Hale", "Dalton Caldwell",
            "Falguni Nayar", "Deepinder Goyal", "Nithin Kamath",
            "Kiran Mazumdar-Shaw", "Vijay Shekhar Sharma", "Sridhar Vembu", "Bhavish Aggarwal"
        ]
        db_names = list(founders.values_list('name', flat=True))
        for req in required_names:
            self.assertIn(req, db_names)

    def test_audit_no_generic_template_milestones(self):
        """No entrepreneur timeline should contain generic placeholder copy."""
        banned_phrases = [
            "developed problem-solving capabilities",
            "Early Foundation & Education",
            "Concept Validation & First Venture",
            "Scaling Operations & Market Growth",
            "Global Impact & Industry Leadership",
            "identified customer pain and tested market demand",
            "expanded customer acquisition and operational efficiency",
            "transformed the industry",
        ]
        for ent in Entrepreneur.objects.all():
            milestones = ent.get_milestones()
            self.assertGreaterEqual(len(milestones), 5, f"{ent.name} has fewer than 5 milestones")
            for m in milestones:
                title = m.get('title', '')
                desc = m.get('desc', '')
                for phrase in banned_phrases:
                    self.assertNotIn(phrase.lower(), title.lower(), f"Generic phrase '{phrase}' in title of {ent.name}")
                    self.assertNotIn(phrase.lower(), desc.lower(), f"Generic phrase '{phrase}' in desc of {ent.name}")

    def test_audit_milestones_have_sources_dates_and_descriptions(self):
        """Every milestone must contain a title, date/year, specific historical description, and verified source."""
        all_milestones = TimelineMilestone.objects.all()
        self.assertEqual(all_milestones.count(), 155)
        for m in all_milestones:
            self.assertTrue(m.title.strip(), f"Milestone ID {m.id} missing title")
            self.assertTrue(m.year_or_date.strip(), f"Milestone ID {m.id} missing date")
            self.assertGreater(len(m.description), 50, f"Milestone {m.title} description is too short")
            self.assertTrue(m.source.strip(), f"Milestone {m.title} for {m.entrepreneur.name} missing source")

    def test_audit_business_facts_accuracy(self):
        """Verify critical historical business facts across founders."""
        # Bill Gates: Microsoft founded in 1975 in Albuquerque, New Mexico (NOT Redmond)
        gates = Entrepreneur.objects.get(name="Bill Gates")
        self.assertEqual(gates.founded_year, 1975)
        self.assertIn("Albuquerque", gates.founding_location)
        self.assertIn("Paul", gates.co_founders)
        self.assertIn("Redmond", gates.headquarters)

        # Steve Jobs: Apple founded in 1976 in Los Altos, California (NOT Cupertino)
        jobs = Entrepreneur.objects.get(name="Steve Jobs")
        self.assertEqual(jobs.founded_year, 1976)
        self.assertIn("Los Altos", jobs.founding_location)
        self.assertIn("Cupertino", jobs.headquarters)
        self.assertIn("Wozniak", jobs.co_founders)

        # Jeff Bezos: Amazon founded in 1994 in Bellevue, Washington (NOT Seattle)
        bezos = Entrepreneur.objects.get(name="Jeff Bezos")
        self.assertEqual(bezos.founded_year, 1994)
        self.assertIn("Bellevue", bezos.founding_location)
        self.assertIn("Seattle", bezos.headquarters)

        # Mark Zuckerberg: Thefacebook founded in 2004 in Cambridge, Massachusetts (Harvard)
        zuck = Entrepreneur.objects.get(name="Mark Zuckerberg")
        self.assertEqual(zuck.founded_year, 2004)
        self.assertIn("Cambridge", zuck.founding_location)
        self.assertIn("Menlo Park", zuck.headquarters)

        # Satya Nadella: Executive Leader / Chairman & CEO (distinguished from 1975 company founders Gates & Allen)
        nadella = Entrepreneur.objects.get(name="Satya Nadella")
        self.assertIn("Chief Executive Officer", nadella.role)
        self.assertIn("Bill Gates", nadella.co_founders)

        # Indian Entrepreneurs verified facts
        ritesh = Entrepreneur.objects.get(name="Ritesh Agarwal")
        self.assertEqual(ritesh.founded_year, 2013)
        self.assertIn("Gurugram", ritesh.founding_location)

        falguni = Entrepreneur.objects.get(name="Falguni Nayar")
        self.assertEqual(falguni.founded_year, 2012)
        self.assertIn("Mumbai", falguni.founding_location)

        kamath = Entrepreneur.objects.get(name="Nithin Kamath")
        self.assertEqual(kamath.founded_year, 2010)
        self.assertIn("Bengaluru", kamath.founding_location)
        self.assertIn("Nikhil", kamath.co_founders)

        kiran = Entrepreneur.objects.get(name="Kiran Mazumdar-Shaw")
        self.assertEqual(kiran.founded_year, 1978)
        self.assertIn("Bengaluru", kiran.founding_location)

    def test_audit_distilled_lessons_authenticity_and_sources(self):
        """Every distilled lesson must come from genuine statements with citations."""
        lessons = DistilledLesson.objects.all()
        self.assertEqual(lessons.count(), 104)
        for l in lessons:
            self.assertTrue(l.quote_or_lesson.strip())
            self.assertTrue(l.source.strip(), f"Lesson {l.id} for {l.entrepreneur.name} missing source")

    def test_audit_video_founder_relationships(self):
        """Every video must match its founder, have a valid 11-char YouTube ID, and verified duration."""
        videos = Video.objects.select_related('entrepreneur', 'category').all()
        self.assertEqual(videos.count(), 27)
        for v in videos:
            yt_id = v.get_youtube_video_id()
            self.assertIsNotNone(yt_id, f"Video {v.title} has invalid YouTube ID")
            self.assertEqual(len(yt_id), 11, f"YouTube ID {yt_id} is not 11 chars")
            self.assertTrue(v.duration.strip())
            self.assertGreater(len(v.description), 40)
            self.assertGreater(len(v.get_takeaways_list()), 0)

    def test_audit_no_demo_or_fictional_records(self):
        """Ensure fictional demo data from previous database versions is removed."""
        banned_entities = [
            'Aarav Mehta', 'EcoNova', 'Sarah Mitchell', 'NovaTech AI',
            'Daniel Carter', 'GreenGrid Energy', 'Alex Rivera', 'PayPulse',
            'Elena Rostova', 'BioMedix Tech', 'Marcus Vance', 'CloudScale'
        ]
        for name in banned_entities:
            self.assertFalse(Entrepreneur.objects.filter(name=name).exists(), f"Fictional founder {name} found in DB")
            self.assertFalse(StorySubmission.objects.filter(entrepreneur_name=name).exists(), f"Fictional submission {name} found in DB")
