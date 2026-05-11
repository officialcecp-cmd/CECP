from django.core.management.base import BaseCommand
from landing.models import ClubMember, FacultyProfile
from django.db.models import Q

class Command(BaseCommand):
    help = 'Prepopulates high-fidelity academic data for Pankaj Singh Tomar and Saurabh Raj.'

    def handle(self, *args, **kwargs):
        # Data mapping
        faculty_data = {
            'Pankaj Singh Tomar': {
                'metrics': {
                    'students_mentored': 120,
                    'projects_guided': 35,
                    'research_papers_count': 24,
                    'workshops_conducted': 15,
                    'grants_received': 3,
                    'experience_years': 15,
                },
                'research_interests': "Embedded Systems, IoT Systems, VLSI Design, Advanced Electronics",
                'publications': "IEEE Paper on IoT Architecture 2021, ACM Journal on Embedded Systems 2020, International Conference on VLSI 2019",
                'core_technologies': "Microcontrollers, C++, VHDL, Verilog, Python, RTOS",
                'experience': "2018 - Present: HOD - ECE Department | 2012 - 2018: Senior Associate Professor | 2008 - 2012: Assistant Professor",
                'awards': "Best Faculty Award 2022, Excellence in Research 2020",
                'google_scholar_link': "https://scholar.google.com/",
                'orcid': "0000-0001-2345-6789",
                'role': 'faculty',
                'category': 'advisor'
            },
            'Saurabh Raj': {
                'metrics': {
                    'students_mentored': 85,
                    'projects_guided': 22,
                    'research_papers_count': 12,
                    'workshops_conducted': 8,
                    'grants_received': 1,
                    'experience_years': 8,
                },
                'research_interests': "AI & Machine Learning, Applied Electronics, Signal Processing",
                'publications': "IEEE Conference on Machine Learning 2023, Signal Processing Journal 2022",
                'core_technologies': "Python, MATLAB, TensorFlow, Embedded Linux, DSP",
                'experience': "2020 - Present: Faculty Coordinator CECP | 2016 - 2020: Assistant Professor ECE",
                'awards': "Innovation Award 2023",
                'google_scholar_link': "https://scholar.google.com/",
                'orcid': "0000-0002-9876-5432",
                'role': 'faculty',
                'category': 'advisor'
            }
        }

        # Locate existing members
        members = ClubMember.objects.filter(
            Q(display_name__icontains='Pankaj') | Q(display_name__icontains='Saurabh')
        )

        if not members.exists():
            self.stdout.write(self.style.WARNING("No existing faculty members found matching 'Pankaj' or 'Saurabh'."))
            return

        for member in members:
            if 'pankaj' in member.display_name.lower():
                key = 'Pankaj Singh Tomar'
            elif 'saurabh' in member.display_name.lower():
                key = 'Saurabh Raj'
            else:
                continue

            data = faculty_data[key]

            # 1. Update ClubMember fields
            member.core_technologies = data['core_technologies']
            member.experience = data['experience']
            member.role = data['role']
            member.category = data['category']
            member.display_role = "Faculty Coordinator"
            member.is_active = True
            member.save()

            # 2. Update/Create FacultyProfile
            profile, created = FacultyProfile.objects.get_or_create(user=member.user)
            
            metrics = data['metrics']
            profile.students_mentored = metrics['students_mentored']
            profile.projects_guided = metrics['projects_guided']
            profile.research_papers_count = metrics['research_papers_count']
            profile.workshops_conducted = metrics['workshops_conducted']
            profile.grants_received = metrics['grants_received']
            profile.experience_years = metrics['experience_years']

            profile.research_interests = data['research_interests']
            profile.publications = data['publications']
            profile.awards = data['awards']
            profile.google_scholar_link = data['google_scholar_link']
            profile.orcid = data['orcid']

            profile.save()

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} high-fidelity profile data for {key}"))
