# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:18:19 2025
@author: goranklasic
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.db.models import Max
from django.template.loader import render_to_string
from functools import wraps
from weasyprint import HTML, CSS
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os
from django.db.models import Q
import PyPDF2
from io import BytesIO
from django.core.paginator import Paginator
from django.db.models import Sum
from login.models import Login, Coach, ContactList, Team, CoachCertificate, Parents, PML, ParentsLink, Player, SportsLink, ClubLink, OtherSports, OtherClubs, Role, Gender, Payments, PT
from .forms import CoachForm, CertificateForm, TeamForm, ParentsForm, PlayerForm
from login.processor import process_player_record


# 🔐 Auth Wrapper
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# 🔐 Login
def login_view(request):
    error_message = ""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        try:
            user = Login.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['coaches_name'] = user.coaches_name
            return redirect('dashboard')
        except Login.DoesNotExist:
            error_message = "Invalid username or password."
    return render(request, 'login.html', {'error_message': error_message})

# 🔐 Logout
def logout_view(request):
    request.session.flush()
    return redirect('login')

# 🏠 Dashboard
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard_home.html', {
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# 🧑‍🏫 Coach List
@login_required
def coach_list_view(request):
    query = request.GET.get('q')
    coaches = Coach.objects.filter(coaches_name__icontains=query.strip()).order_by('coaches_name') if query else Coach.objects.all().order_by('coaches_name')
    return render(request, 'dashboard/coach_list.html', {
        'coaches': coaches,
        'filter_query': query or '',
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# ✏️ Coach Edit + Cert Upload
@login_required
def edit_coach_view(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    form = CoachForm(instance=coach)  # 👈 Add this before checking request.method

    # 🧼 Trim CharFields before loading form
    char_fields = ['coaches_name', 'coaches_address', 'coaches_email', 'coach_bi_number', 'photo_link']
    for field in char_fields:
        value = getattr(coach, field, None)
        if isinstance(value, str):
            setattr(coach, field, value.strip())

    certificates = CoachCertificate.objects.filter(coach=coach).order_by('cert_type')
    certificate_form = CertificateForm()

    if request.method == 'POST' and 'cert_upload' not in request.POST:
        original_photo = coach.photo_link
        form = CoachForm(request.POST, request.FILES, instance=coach)

        if form.is_valid():
            updated_coach = form.save(commit=False)

            # ✅ Inject active_status manually from POST
            active_val = request.POST.get('active_status')
            if active_val in ['0', '1']:
                updated_coach.active_status = int(active_val)

            # Clean char fields again on save
            for field in char_fields:
                value = getattr(updated_coach, field, None)
                if isinstance(value, str):
                    setattr(updated_coach, field, value.strip())

            # ✅ Optional image upload
            if 'coach_photo' in request.FILES:
                photo_file = request.FILES['coach_photo']
                photo_folder = os.path.join(
                    settings.BASE_DIR, 'login', 'static', 'uploads', 'coaches', str(coach.coaches_id)
                )
                os.makedirs(photo_folder, exist_ok=True)
                fs = FileSystemStorage(location=photo_folder)
                fs.save(photo_file.name, photo_file)
                updated_coach.photo_link = f'/static/uploads/coaches/{coach.coaches_id}/{photo_file.name}'
            else:
                updated_coach.photo_link = original_photo

            updated_coach.save()
            messages.success(request, "Coach details updated successfully.")
            return redirect('coach_edit', pk=coach.pk)
        else:
            messages.error(request, "Could not save coach — please check for errors.")

    elif request.method == 'POST' and 'cert_upload' in request.POST:
        certificate_form = CertificateForm(request.POST, request.FILES)

        if 'file_path' not in request.FILES:
            messages.warning(request, "Please select a certificate file before uploading.")
        elif certificate_form.is_valid():
            new_cert = certificate_form.save(commit=False)
            new_cert.coach = coach
            cert_file = request.FILES['file_path']
            cert_folder = os.path.join(
                settings.BASE_DIR, 'login', 'static', 'uploads', 'coaches', str(coach.coaches_id)
            )
            os.makedirs(cert_folder, exist_ok=True)
            fs = FileSystemStorage(location=cert_folder)
            fs.save(cert_file.name, cert_file)
            new_cert.file_path = f'/static/uploads/coaches/{coach.coaches_id}/{cert_file.name}'
            new_cert.save()
            messages.success(request, "Certificate uploaded successfully.")
            return redirect('coach_edit', pk=coach.pk)
        else:
            messages.error(request, "Could not upload certificate — please check for errors.")

    else:
        form = CoachForm(instance=coach)

    return render(request, 'dashboard/edit_coach.html', {
        'form': form,
        'coach': coach,
        'certificates': certificates,
        'certificate_form': certificate_form,
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# 🖨️ Print All Coaches PDF
@login_required
def print_coaches_view(request):
    active_coaches = Coach.objects.filter(active_status=1).order_by('coaches_name')
    paginator = Paginator(active_coaches, 5)
    pages = [paginator.page(i) for i in paginator.page_range]

    html_string = render_to_string('dashboard/coaches_pdf.html', {'pages': pages})
    css_path = os.path.join(settings.BASE_DIR, 'static/css/print.css')

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(filename=css_path)]
    )

    return HttpResponse(pdf_file, content_type='application/pdf')


# 🖨️ Print Single Coach + Certs PDF
@login_required
def print_single_coach_view(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    certificates = CoachCertificate.objects.filter(coach=coach).order_by('cert_type')
    html_string = render_to_string('dashboard/print_coach.html', {
        'coach': coach,
        'certificates': certificates
    })
    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))
    profile_pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )

    merger = PyPDF2.PdfMerger()
    merger.append(BytesIO(profile_pdf))

    for cert in certificates:
        if cert.file_path and cert.file_path.lower().endswith('.pdf'):
            relative_path = cert.file_path.replace('/static/', '')
            cert_path = os.path.join(settings.BASE_DIR, 'login', 'static', relative_path)
            if os.path.exists(cert_path):
                with open(cert_path, 'rb') as f:
                    merger.append(f)

    output_stream = BytesIO()
    merger.write(output_stream)
    merger.close()
    return HttpResponse(output_stream.getvalue(), content_type='application/pdf')

# 🗂️ Contact List
@login_required
def contact_list_view(request):
    contacts = ContactList.objects.all().order_by('playername')
    return render(request, 'dashboard/contact_list.html', {
        'contacts': contacts,
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# ✏️ Contact Edit
@login_required
def contact_edit_view(request, pk):
    contact = get_object_or_404(ContactList, pk=pk)
    teams = Team.objects.all().order_by('teams_name')
    if request.method == 'POST':
        contact.playername = request.POST.get('playername')
        contact.dob = request.POST.get('dob')
        contact.teams_name = request.POST.get('teams_name')
        contact.contactemail = request.POST.get('contactemail')
        contact.phonenumber = request.POST.get('phonenumber')
        contact.memo = request.POST.get('memo')
        contact.save()
        return redirect('contact_list_view')
    return render(request, 'dashboard/contact_edit.html', {
        'contact': contact,
        'teams': teams,
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# 🖨️ Print All Contacts
@login_required
def contact_print_view(request):
    contacts = ContactList.objects.all().order_by('playername')
    html_string = render_to_string('dashboard/contact_print.html', {'contacts': contacts})
    css_path = os.path.join(settings.BASE_DIR, 'static/css/print.css')
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[CSS(filename=css_path)])
    return HttpResponse(pdf_file, content_type='application/pdf')

# 🖨️ Print Single Contact
@login_required
def print_single_contact_view(request, pk):
    contact = get_object_or_404(ContactList, pk=pk)
    html_string = render_to_string('dashboard/print_single_contact.html', {'contact': contact})
    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )
    return HttpResponse(pdf_file, content_type='application/pdf')

# 🗑️ Delete Certificate
@login_required
def delete_certificate_view(request, cert_id):
    if request.method == 'POST':
        cert = get_object_or_404(CoachCertificate, pk=cert_id)
        coach_id = cert.coach.pk
        if cert.file_path:
            relative_path = cert.file_path.replace('/static/', '')
            cert_path = os.path.join(settings.BASE_DIR, 'login', 'static', relative_path)
            if os.path.isfile(cert_path):
                try:
                    os.remove(cert_path)
                    messages.success(request, f"File deleted: {os.path.basename(cert_path)}")
                except Exception as e:
                    messages.warning(request, f"File couldn't be removed: {e}")
            else:
                messages.info(request, "File not found. Possibly already deleted.")
        cert.delete()
        messages.success(request, "Certificate deleted successfully.")
        return redirect('coach_edit', pk=coach_id)
    messages.error(request, "Invalid request method.")
    return redirect('dashboard')

# 👥 Team List
@login_required
def team_list_view(request):
    query = request.GET.get('q')

    if query:
        teams = Team.objects.filter(teams_name__icontains=query.strip()).order_by('teams_name')
    else:
        teams = Team.objects.all().order_by('teams_name')
    return render(request, 'dashboard/team_list.html', {
        'teams': teams,
        'filter_query': query or '',
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# 🛠️ Team Edit
@login_required
def team_edit_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    form = TeamForm(request.POST or None, instance=team)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('team_list')
    return render(request, 'dashboard/team_edit.html', {
        'form': form,
        'coaches_name': request.session.get('coaches_name', 'Coach')
    })

# 🖨️ Print All Teams
@login_required
def team_print_all_view(request):
    teams = Team.objects.all().order_by('teams_name')
    html_string = render_to_string('dashboard/team_print_all.html', {'teams': teams})

    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )

    return HttpResponse(pdf_file, content_type='application/pdf')

# 🖨️ Print Single Team
@login_required
def team_print_one_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    html_string = render_to_string('dashboard/team_print_one.html', {'team': team})

    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )

    return HttpResponse(pdf_file, content_type='application/pdf')


def get_next_coach_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(coaches_id) FROM coaches")
        result = cursor.fetchone()
        return (result[0] or 0) + 1

@login_required
def add_coach_view(request):
    if request.method == 'POST':
        form = CoachForm(request.POST)
        if form.is_valid():
            coach = form.save(commit=False)
            coach.coaches_id = get_next_coach_id()
            coach.save()
            return redirect('coach_list')
    else:
        form = CoachForm()
    
    return render(request, 'dashboard/add_coach.html', {
        'form': form,
        'messages': [],  # optional if you're using Django messages
    })


def get_next_team_id():
    max_id = Team.objects.aggregate(Max('teams_id'))['teams_id__max']
    return (max_id or 0) + 1

@login_required
def add_team_view(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.teams_id = get_next_team_id()
            team.save()  # coach name syncing happens via Team.save()
            return redirect('team_list')
    else:
        form = TeamForm()

    return render(request, 'dashboard/add_team.html', {'form': form})


@login_required
def add_parent_view(request):
    form = ParentsForm(request.POST or None)

    if form.is_valid():
        parent = form.save(commit=False)

        # 🔢 Manually assign parents_id (since it's not auto-incrementing)
        max_id = Parents.objects.aggregate(Max('parents_id'))['parents_id__max'] or 0
        parent.parents_id = max_id + 1

        # 🧼 Strip whitespace from member names (via related PML records)
        parent.member_1 = parent.parents_member_1.pml_name.strip() if parent.parents_member_1 and parent.parents_member_1.pml_name else ''
        parent.member_2 = parent.parents_member_2.pml_name.strip() if parent.parents_member_2 and parent.parents_member_2.pml_name else ''
        parent.member_3 = parent.parents_member_3.pml_name.strip() if parent.parents_member_3 and parent.parents_member_3.pml_name else ''

        # 🧽 Clean model before saving
        parent.full_clean()
        parent.save()
        return redirect('parents_list')

    return render(request, 'dashboard/add_parent.html', {'form': form})

@login_required
def parents_list_view(request):
    search_query = request.GET.get('search', '')
    
    # Filter logic
    parents_qs = Parents.objects.all()
    if search_query:
        parents_qs = parents_qs.filter(parents_name__icontains=search_query)

    # ✅ Correct ordering using the actual PK field
    parents_qs = parents_qs.order_by('parents_id')  # Not 'id'

    # Pagination
    paginator = Paginator(parents_qs, 20)
    page_number = request.GET.get('page')
    parents_page = paginator.get_page(page_number)

    return render(request, 'dashboard/parents_list.html', {
        'parents': parents_page,
        'search_query': search_query
    })


@login_required
def edit_parent_view(request, pk):
    parent = get_object_or_404(Parents, pk=pk)

    # Strip whitespace before loading into form
    for field in [
        'parents_name', 'parents_email', 'parents_mobile_number',
        'member_1', 'member_2', 'member_3',
        'parents_member_1_description', 'parents_member_2_description', 'parents_member_3_description'
    ]:
        val = getattr(parent, field, None)
        if isinstance(val, str):
            setattr(parent, field, val.strip())

    # All available member roles
    all_pml = PML.objects.all()

    if request.method == 'POST':
        form = ParentsForm(request.POST, instance=parent)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.member_1 = updated.parents_member_1.pml_name.strip() if updated.parents_member_1 else ''
            updated.member_2 = updated.parents_member_2.pml_name.strip() if updated.parents_member_2 else ''
            updated.member_3 = updated.parents_member_3.pml_name.strip() if updated.parents_member_3 else ''
            updated.full_clean()
            updated.save()
            return redirect('parents_list')
    else:
        form = ParentsForm(instance=parent)

    linked_players = Player.objects.filter(
        player_id__in=ParentsLink.objects.filter(parents_id=parent.parents_id).values('player_id')
    )

    return render(request, 'dashboard/edit_parent.html', {
        'form': form,
        'linked_players': linked_players,
        'all_pml': all_pml
    })

@login_required
def print_parent_view(request, pk):
    parent = get_object_or_404(Parents, pk=pk)
    linked_players = Player.objects.filter(
        player_id__in=ParentsLink.objects.filter(parents_id=parent.parents_id).values('player_id')
    )

    html_string = render_to_string('dashboard/print_parent.html', {
        'parent': parent,
        'linked_players': linked_players
    })

    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))

    pdf_output = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )

    return HttpResponse(pdf_output, content_type='application/pdf')

@login_required
def print_all_parents_view(request):
    all_parents = Parents.objects.all()
    parent_data = []

    for parent in all_parents:
        players = Player.objects.filter(
            player_id__in=ParentsLink.objects.filter(parents_id=parent.parents_id).values('player_id')
        )
        parent_data.append({'parent': parent, 'players': players})

    html_string = render_to_string('dashboard/print_all_parents.html', {
        'parent_data': parent_data
    })

    # Load CSS styles
    bootstrap_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'))
    print_css = CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/print.css'))

    # Generate PDF
    pdf_output = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[bootstrap_css, print_css]
    )

    return HttpResponse(pdf_output, content_type='application/pdf')

@login_required
def get_next_player_id():
    max_id = Player.objects.aggregate(Max('player_id'))['player_id__max']
    return (max_id or 0) + 1

@login_required
def player_list_view(request):
    name_filter = request.GET.get('name', '').strip()
    team_filter = request.GET.get('team', '').strip()
    show_all = request.GET.get('all') == '1'
    players = Player.objects.all() if show_all else Player.objects.filter(player_active=1)

    if name_filter:
        players = players.filter(player_name__icontains=name_filter)
    if team_filter:
        players = players.filter(player_team__icontains=team_filter)

    paginator = Paginator(players.order_by('player_name'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/player_list.html', {
        'players': page_obj,
        'name_filter': name_filter,
        'team_filter': team_filter
    })

@login_required
def add_player_view(request):
    all_roles = Role.objects.all()
    all_teams = Team.objects.all()
    all_genders = Gender.objects.all()

    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            new_player = form.save(commit=False)

            # 🔢 Assign new player_id manually
            max_id = Player.objects.aggregate(Max('player_id'))['player_id__max'] or 0
            new_player.player_id = max_id + 1

            # 🧠 Gender Selection
            gender_id = request.POST.get('gender_id')
            gender = Gender.objects.filter(pk=gender_id).first()
            if gender:
                new_player.gender_id = gender.gender_id
            new_player.gender_specify = request.POST.get('gender_specify', '')

            # 🧠 Team Selection
            team_id = request.POST.get('team')
            team = Team.objects.filter(pk=team_id).first()
            if team:
                new_player.player_team_id = team.teams_id
                new_player.player_team = team.teams_name
                if new_player.player_membership_amount in [None, 0]:
                    new_player.player_membership_amount = team.teams_membership

            # 🧠 Role Selection
            role_id = request.POST.get('role')
            role = Role.objects.filter(pk=role_id).first()
            if role:
                new_player.player_role_id = role.role_id
                new_player.player_role = role.role_name

            # 🧼 Optional CharFields
            new_player.player_other_roles = request.POST.get('player_other_roles', '')
            new_player.participation_member_other_activities = request.POST.get('participation_member_other_activities', '')

            # 🧠 Member dropdowns: convert '' to None
            member_1 = request.POST.get('player_member_1')
            member_2 = request.POST.get('player_member_2')
            member_3 = request.POST.get('player_member_3')
            new_player.player_member_1 = int(member_1) if member_1 else None
            new_player.player_member_2 = int(member_2) if member_2 else None
            new_player.player_member_3 = int(member_3) if member_3 else None

            # ✅ Safe defaults
            new_player.sent_membership = 0
            new_player.player_transfer_out = 0
            new_player.player_committee_member = 0
            new_player.created = timezone.now()

            new_player.save()
            messages.success(request, "New player added successfully.")
            return redirect('player_list')
        else:
            messages.error(request, "Please correct the errors before submitting.")
    else:
        form = PlayerForm()

    return render(request, 'dashboard/add_player.html', {
        'form': form,
        'all_roles': all_roles,
        'all_teams': all_teams,
        'all_genders': all_genders
    })



@login_required
def edit_player_view(request, pk):
    player = get_object_or_404(Player, pk=pk)

    # 🔧 Strip whitespace before loading the form
    for field in [
        'player_name', 'player_address', 'player_email',
        'player_primary_mobile_number', 'player_contact_name1',
        'player_contact_name2', 'gender_specify',
        'player_medical_conditions', 'participation_member_other_activities',
        'player_other_roles', 'photo_link'
    ]:
        val = getattr(player, field, None)
        if isinstance(val, str):
            setattr(player, field, val.strip())

    form = PlayerForm(request.POST or None, request.FILES or None, instance=player)
    original_photo = player.photo_link

    # Lookup tables
    all_roles = Role.objects.all()
    all_teams = Team.objects.all()
    all_genders = Gender.objects.all()
    all_pml = PML.objects.all()
    all_parents = Parents.objects.all()
    all_sports = OtherSports.objects.all()
    all_clubs = OtherClubs.objects.all()

    # Linked data
    linked_parent_links = ParentsLink.objects.filter(player_id=player.player_id)
    linked_sport_links = SportsLink.objects.filter(player_id=player.player_id)
    linked_club_links = ClubLink.objects.filter(player_id=player.player_id)
    linked_payments = Payments.objects.filter(player_id=player.player_id).order_by('-payments_date')

    # 💰 Total payments sum
    total_amount = linked_payments.aggregate(Sum('payments_amount'))['payments_amount__sum'] or 0

    if request.method == 'POST' and 'save_player' in request.POST:
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            updated_player = form.save(commit=False)

            # 👤 Gender Info (FIX)
            gender_id = request.POST.get('gender_id')
            updated_player.gender = Gender.objects.filter(pk=gender_id).first() if gender_id else None

            # Team Info
            team_id = request.POST.get('team')
            team = Team.objects.filter(pk=team_id).first()
            if team:
                updated_player.player_team_id = team.teams_id
                updated_player.player_team = team.teams_name
                if updated_player.player_membership_amount in [None, 0]:
                    updated_player.player_membership_amount = team.teams_membership

            # Role Info
            role_id = request.POST.get('role')
            role = Role.objects.filter(pk=role_id).first()
            if role:
                updated_player.player_role_id = role.role_id
                updated_player.player_role = role.role_name

            # Extra Form Fields
            updated_player.gender_specify = request.POST.get('gender_specify', '')
            updated_player.player_other_roles = request.POST.get('player_other_roles', '')
            updated_player.participation_member_other_activities = request.POST.get('participation_member_other_activities', '')
            updated_player.sent_membership = updated_player.sent_membership or 0

            # Member Dropdowns
            updated_player.player_member_1 = request.POST.get('player_member_1') or None
            updated_player.player_member_2 = request.POST.get('player_member_2') or None
            updated_player.player_member_3 = request.POST.get('player_member_3') or None

            # Photo Upload
            if 'player_photo' in request.FILES:
                photo_file = request.FILES['player_photo']
                photo_path = os.path.join(settings.BASE_DIR, 'login', 'static', 'uploads', 'players', str(player.player_id))
                os.makedirs(photo_path, exist_ok=True)
                fs = FileSystemStorage(location=photo_path)
                fs.save(photo_file.name, photo_file)
                updated_player.photo_link = f'/static/uploads/players/{player.player_id}/{photo_file.name}'
            else:
                updated_player.photo_link = original_photo

            updated_player.save()
            messages.success(request, "Player details updated successfully.")
            return redirect('player_list')
        else:
            messages.error(request, "Player form could not be saved. Please correct the highlighted fields.")
            print(form.errors.as_data())

    elif request.method == 'POST':
        # Linked tables (parents, clubs, sports)
        if 'add_parent' in request.POST:
            new_id = request.POST.get('new_parent_id')
            if new_id:
                max_id = ParentsLink.objects.aggregate(Max('id'))['id__max'] or 0
                ParentsLink.objects.create(id=max_id + 1, player_id=player.player_id, parents_id=int(new_id))
            return redirect('edit_player', pk=pk)

        elif 'delete_parent' in request.POST:
            link_id = request.POST.get('parent_link_id')
            ParentsLink.objects.filter(id=link_id).delete()
            return redirect('edit_player', pk=pk)

        elif 'add_sport' in request.POST:
            sport_id = request.POST.get('new_sport_id')
            if sport_id:
                max_id = SportsLink.objects.aggregate(Max('id'))['id__max'] or 0
                SportsLink.objects.create(id=max_id + 1, player_id=player.player_id, sports_id=int(sport_id))
            return redirect('edit_player', pk=pk)

        elif 'delete_sport' in request.POST:
            link_id = request.POST.get('sport_link_id')
            SportsLink.objects.filter(id=link_id).delete()
            return redirect('edit_player', pk=pk)

        elif 'add_club' in request.POST:
            club_id = request.POST.get('new_club_id')
            if club_id:
                max_id = ClubLink.objects.aggregate(Max('id'))['id__max'] or 0
                ClubLink.objects.create(id=max_id + 1, player_id=player.player_id, clubs_id=int(club_id))
            return redirect('edit_player', pk=pk)

        elif 'delete_club' in request.POST:
            link_id = request.POST.get('club_link_id')
            ClubLink.objects.filter(id=link_id).delete()
            return redirect('edit_player', pk=pk)

    return render(request, 'dashboard/edit_player.html', {
        'form': form,
        'player': player,
        'linked_parent_links': linked_parent_links,
        'linked_sport_links': linked_sport_links,
        'linked_club_links': linked_club_links,
        'linked_payments': linked_payments,
        'total_amount': total_amount,
        'all_teams': all_teams,
        'all_roles': all_roles,
        'all_genders': all_genders,
        'all_pml': all_pml,
        'all_parents': all_parents,
        'all_sports': all_sports,
        'all_clubs': all_clubs,
    })

@login_required
def generate_player_form(request, player_id):
    player = get_object_or_404(Player, pk=player_id)

    gender_name = player.gender.gender_name.strip() if player.gender else ''

    # Grab first linked parent via ParentsLink relationship
    linked = ParentsLink.objects.filter(player_id=player.player_id).select_related(None).first()
    parent = Parents.objects.filter(parents_id=linked.parents_id).first() if linked else None

    # Prepare tuple for processor
    player_tuple = (
        player.player_id,
        player.player_name,
        player.gender.gender_name if player.gender else '',
        player.player_address,
        player.player_dob,
        player.player_email,
        None,  # previous_teams_name (unused)
        player.player_medical_conditions,
        player.participation_member_training,
        player.participation_member_play_matches,
        player.photo_cons,
        player.player_role,
        player.player_primary_mobile_number,
        player.player_contact_name1,
        player.player_secundary_mobile_number,
        player.player_contact_name2,
        parent.parents_name if parent else '',
        parent.parents_address if parent else '',
        parent.parents_dob if parent else '',
        parent.parents_mobile_number if parent else '',
    )

    result = process_player_record(player_tuple)
    return FileResponse(open(result['pdf_path'], 'rb'), content_type='application/pdf')


@login_required
def print_player_view(request, pk):
    player = get_object_or_404(Player, pk=pk)
    html_string = render_to_string('dashboard/print_player.html', {'player': player})
    css_path = os.path.join(settings.BASE_DIR, 'static/css/print.css')
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(filename=css_path)])
    return HttpResponse(pdf_file, content_type='application/pdf')

@login_required
def print_all_players_view(request):
    name_filter = request.GET.get('name', '').strip()
    team_filter = request.GET.get('team', '').strip()
    players = Player.objects.filter(player_active=1)

    if name_filter:
        players = players.filter(player_name__icontains=name_filter)
    if team_filter:
        players = players.filter(player_team__icontains=team_filter)

    html_string = render_to_string('dashboard/print_all_players.html', {'players': players})
    css_path = os.path.join(settings.BASE_DIR, 'static/css/print.css')
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(filename=css_path)])
    return HttpResponse(pdf_file, content_type='application/pdf')
