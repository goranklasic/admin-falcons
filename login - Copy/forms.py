# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:47:59 2025

@author: goranklasic
"""

from django import forms
from login.models import Coach, CoachCertificate, Team, Parents, PML, Player

class CoachForm(forms.ModelForm):
    coach_photo = forms.FileField(label='Coach Photo', required=False)

    class Meta:
        model = Coach
        exclude = ['coaches_id']
        fields = [
            'coaches_name', 'coaches_address', 'coaches_dob', 'coaches_email',
            'coach_bi_number', 'safe_guarding_level_1', 'safe_guarding_level_1_date',
            'safe_guarding_level_2', 'safe_guarding_level_2_date',
            'safe_guarding_level_3', 'safe_guarding_level_3_date',
            'garda_vetting', 'garda_vetting_date',
            'basketball_coaching_level_0', 'basketball_coaching_level_0_date',
            'basketball_coaching_level_1', 'basketball_coaching_level_1_date',
            'basketball_coaching_level_2', 'basketball_coaching_level_2_date',
            'first_aid', 'first_aid_date',
        ]
        widgets = {
            'coaches_address': forms.Textarea(attrs={'rows': 3}),
            'coaches_dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'mm/dd/yyyy'}),
            'safe_guarding_level_1_date': forms.DateInput(attrs={'type': 'date'}),
            'safe_guarding_level_2_date': forms.DateInput(attrs={'type': 'date'}),
            'safe_guarding_level_3_date': forms.DateInput(attrs={'type': 'date'}),
            'garda_vetting_date': forms.DateInput(attrs={'type': 'date'}),
            'basketball_coaching_level_0_date': forms.DateInput(attrs={'type': 'date'}),
            'basketball_coaching_level_1_date': forms.DateInput(attrs={'type': 'date'}),
            'basketball_coaching_level_2_date': forms.DateInput(attrs={'type': 'date'}),
            'first_aid_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        for field_name, value in cleaned.items():
            if isinstance(value, str):
                cleaned[field_name] = value.strip()
        return cleaned


class CertificateForm(forms.ModelForm):
    cert_type = forms.CharField(label='Certification Type', required=False)
    date_issued = forms.DateField(label='Date Issued', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    valid_until = forms.DateField(label='Valid Until', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    notes = forms.CharField(label='Notes', required=False, widget=forms.Textarea(attrs={'rows': 2}))
    file_path = forms.FileField(label='Certificate PDF', required=False)

    class Meta:
        model = CoachCertificate
        fields = ['cert_type', 'date_issued', 'valid_until', 'notes', 'file_path']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        for field_name, value in cleaned.items():
            if isinstance(value, str):
                cleaned[field_name] = value.strip()
        return cleaned


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        exclude = ['teams_id']
        fields = ['teams_name', 'teams_description', 'teams_membership', 'coaches_id1', 'coaches_id2']
        labels = {
            'teams_name': 'Team Name',
            'teams_description': 'Description',
            'teams_membership': 'Membership (€)',
            'coaches_id1': 'Main Coach',
            'coaches_id2': 'Assistant Coach',
        }
        widgets = {
            'teams_description': forms.Textarea(attrs={'rows': 2}),
            'teams_membership': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean(self):
        cleaned = super().clean()
        for field_name, value in cleaned.items():
            if isinstance(value, str):
                cleaned[field_name] = value.strip()
        return cleaned


class ParentsForm(forms.ModelForm):
    parents_dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date of Birth"
    )

    # Member dropdowns
    parents_member_1 = forms.ModelChoiceField(
        queryset=PML.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Member 1"
    )
    parents_member_1_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label="Description 1"
    )

    parents_member_2 = forms.ModelChoiceField(
        queryset=PML.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Member 2"
    )
    parents_member_2_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label="Description 2"
    )

    parents_member_3 = forms.ModelChoiceField(
        queryset=PML.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Member 3"
    )
    parents_member_3_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label="Description 3"
    )

    class Meta:
        model = Parents
        fields = [
            'parents_name',
            'parents_dob',
            'parents_email',
            'parents_mobile_number',
            'parents_member_1', 'parents_member_1_description',
            'parents_member_2', 'parents_member_2_description',
            'parents_member_3', 'parents_member_3_description'
        ]
        widgets = {
            'parents_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parents_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parents_mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned = super().clean()
        for field_name, value in cleaned.items():
            if isinstance(value, str):
                cleaned[field_name] = value.strip()
        return cleaned


class PlayerForm(forms.ModelForm):
    player_dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    player_membership_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        required=False
    )
    player_active = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False)
    player_transfer_out = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False, initial=0)
    player_committee_member = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False, initial=0)
    photo_cons = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False)
    participation_member_training = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False)
    participation_member_play_matches = forms.ChoiceField(choices=[(1, 'YES'), (0, 'NO')], required=False)
    player_photo = forms.FileField(required=False)

    # ✅ TypedChoiceFields match IntegerField model fields
    PML_CHOICES = [(p.pml_id, p.pml_name) for p in PML.objects.all()]
    EMPTY = [(None, 'Not involved')]

    player_member_1 = forms.TypedChoiceField(
        choices=EMPTY + PML_CHOICES,
        coerce=int,
        required=False,
        label="Member 1"
    )
    player_member_2 = forms.TypedChoiceField(
        choices=EMPTY + PML_CHOICES,
        coerce=int,
        required=False,
        label="Member 2"
    )
    player_member_3 = forms.TypedChoiceField(
        choices=EMPTY + PML_CHOICES,
        coerce=int,
        required=False,
        label="Member 3"
    )

    # Additional fields
    player_bi_number = forms.IntegerField(required=False)
    player_team = forms.CharField(required=False)
    player_team_id = forms.IntegerField(required=False)
    player_role = forms.CharField(required=False)
    player_role_id = forms.IntegerField(required=False)
    sent_membership = forms.IntegerField(required=False)
    gender_specify = forms.CharField(required=False)
    player_other_roles = forms.CharField(required=False)
    participation_member_other_activities = forms.CharField(required=False)
    photo_link = forms.CharField(required=False)

    class Meta:
        model = Player
        exclude = ['player_id']
        fields = '__all__'
        widgets = {
           'player_address': forms.Textarea(attrs={'rows': 3}),
           'player_medical_conditions': forms.Textarea(attrs={'rows': 2}),
           'participation_member_other_activities': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.fields['gender'].required = False

    def clean(self):
        cleaned = super().clean()
        for field_name, value in cleaned.items():
            if isinstance(value, str):
                cleaned[field_name] = value.strip()
        return cleaned