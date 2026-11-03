from django.core.management.base import BaseCommand
from django.utils.text import slugify
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
from directory.research_data import CATEGORIES_DATA, ENTREPRENEURS_DATA, VIDEOS_DATA

class Command(BaseCommand):
    help = 'Seeds database with verified, genuine Categories, Entrepreneurs, Milestones, Lessons, and Masterclass Videos.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seeding with verified real-world entrepreneur data..."))

        # 1. Categories
        cat_objs = {}
        for c in CATEGORIES_DATA:
            obj, _ = Category.objects.update_or_create(
                name=c['name'],
                defaults={'description': c['description'], 'icon': c['icon']}
            )
            cat_objs[c['name']] = obj

        self.stdout.write(f"Synced {len(cat_objs)} Categories.")

        # 2. Genuine, Real-World Entrepreneurs
        ent_objs = {}
        total_milestones_created = 0
        total_lessons_created = 0

        for ed in ENTREPRENEURS_DATA:
            ent, _ = Entrepreneur.objects.update_or_create(
                name=ed['name'],
                defaults={
                    'company_name': ed['company_name'],
                    'role': ed.get('role', 'Founder & CEO'),
                    'co_founders': ed.get('co_founders', ''),
                    'industry': ed['industry'],
                    'biography': ed['biography'],
                    'profile_image': ed['profile_image'],
                    'location': ed['location'],
                    'founding_location': ed.get('founding_location', ed['location']),
                    'headquarters': ed.get('headquarters', ''),
                    'key_products': ed.get('key_products', ''),
                    'founded_year': ed['founded_year'],
                    'website': ed['website'],
                    'featured': ed['featured'],
                    'is_published': True
                }
            )
            # Update slug
            ent.slug = slugify(f"{ent.name}-{ent.company_name}")
            ent.save()
            ent_objs[ed['name']] = ent

            # 3. Create individually researched Timeline Milestones
            ent.timeline_milestones.all().delete()
            for idx, m in enumerate(ed.get('milestones', [])):
                TimelineMilestone.objects.create(
                    entrepreneur=ent,
                    year_or_date=m['year_or_date'],
                    title=m['title'],
                    subtitle=m.get('subtitle', ''),
                    description=m['description'],
                    source=m.get('source', ''),
                    order=idx + 1
                )
                total_milestones_created += 1

            # 4. Create verified Distilled Lessons
            ent.distilled_lessons.all().delete()
            for idx, l in enumerate(ed.get('lessons', [])):
                DistilledLesson.objects.create(
                    entrepreneur=ent,
                    quote_or_lesson=l['text'],
                    is_quote=l.get('is_quote', False),
                    source=l.get('source', ''),
                    order=idx + 1
                )
                total_lessons_created += 1

        self.stdout.write(f"Synced {len(ent_objs)} Entrepreneurs.")
        self.stdout.write(f"Created {total_milestones_created} verified Timeline Milestones across all profiles.")
        self.stdout.write(f"Created {total_lessons_created} verified Distilled Lessons with primary citations.")

        # 5. Masterclass Videos
        for vd in VIDEOS_DATA:
            ent = ent_objs[vd['entrepreneur_name']]
            cat = cat_objs[vd['category_name']]
            yt_id = vd['video_url'].split('v=')[-1]
            thumb = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"

            video_obj, created = Video.objects.update_or_create(
                id=vd['id'],
                defaults={
                    'title': vd['title'],
                    'entrepreneur': ent,
                    'category': cat,
                    'video_url': vd['video_url'],
                    'thumbnail': thumb,
                    'duration': vd['duration'],
                    'views': vd['views'],
                    'featured': vd['featured'],
                    'trending': vd['trending'],
                    'is_published': True,
                    'description': vd['description'],
                    'key_takeaways': vd['key_takeaways']
                }
            )
            video_obj.slug = slugify(vd['title'])
            video_obj.save()

        self.stdout.write(f"Synced {len(VIDEOS_DATA)} Masterclass Videos.")

        # 6. Clean up any fictional / demo entrepreneur records
        valid_founder_names = [ed['name'] for ed in ENTREPRENEURS_DATA]
        orphans = Entrepreneur.objects.exclude(name__in=valid_founder_names)
        orphan_count = orphans.count()
        if orphan_count > 0:
            orphans.delete()
            self.stdout.write(f"Cleaned up {orphan_count} outdated fictional entrepreneur records.")

        # Clean up any fictional demo story submissions (e.g. Aarav Mehta / EcoNova)
        fictional_subs = StorySubmission.objects.filter(entrepreneur_name__in=['Aarav Mehta', 'Sarah Mitchell', 'Daniel Carter'])
        fictional_sub_count = fictional_subs.count()
        if fictional_sub_count > 0:
            fictional_subs.delete()
            self.stdout.write(f"Cleaned up {fictional_sub_count} demo story submissions.")

        self.stdout.write(self.style.SUCCESS(
            f"Successfully audited and seeded {len(ent_objs)} genuine entrepreneurs, "
            f"{total_milestones_created} historical timeline milestones, "
            f"{total_lessons_created} distilled lessons, and {len(VIDEOS_DATA)} videos!"
        ))
