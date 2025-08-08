# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:47:59 2025

@author: goranklasic
"""

from django.db import models

class Login(models.Model):
    login_key = models.AutoField(primary_key=True)
    id = models.IntegerField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    coaches_id = models.IntegerField()
    coaches_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'login'

    def __str__(self):
        return self.coaches_name

YES_NO_CHOICES = [
    (1, 'YES'),
    (0, 'NO'),
]

class Coach(models.Model):
    coaches_id = models.IntegerField(primary_key=True)
    coaches_name = models.CharField(max_length=255)
    coaches_address = models.TextField(blank=True)
    coaches_dob = models.DateField()
    coaches_email = models.EmailField()
    coach_bi_number = models.CharField(max_length=10, blank=True, null=True)
    active_status = models.SmallIntegerField(choices=YES_NO_CHOICES, default=1)

    safe_guarding_level_1 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    safe_guarding_level_1_date = models.DateField(null=True, blank=True)
    safe_guarding_level_2 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    safe_guarding_level_2_date = models.DateField(null=True, blank=True)
    safe_guarding_level_3 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    safe_guarding_level_3_date = models.DateField(null=True, blank=True)

    garda_vetting = models.SmallIntegerField(choices=YES_NO_CHOICES)
    garda_vetting_date = models.DateField(null=True, blank=True)

    basketball_coaching_level_0 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    basketball_coaching_level_0_date = models.DateField(null=True, blank=True)
    basketball_coaching_level_1 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    basketball_coaching_level_1_date = models.DateField(null=True, blank=True)
    basketball_coaching_level_2 = models.SmallIntegerField(choices=YES_NO_CHOICES)
    basketball_coaching_level_2_date = models.DateField(null=True, blank=True)

    first_aid = models.SmallIntegerField(choices=YES_NO_CHOICES)
    first_aid_date = models.DateField(null=True, blank=True)
    photo_link = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'coaches'

    def __str__(self):
        return self.coaches_name

class Team(models.Model):
    teams_id = models.IntegerField(primary_key=True)
    teams_name = models.CharField(max_length=20)
    teams_description = models.CharField(max_length=50, blank=True, null=True)
    teams_membership = models.DecimalField(max_digits=15, decimal_places=2)

    coaches_id1 = models.ForeignKey(
        Coach, on_delete=models.PROTECT,
        related_name='main_teams',
        db_column='coaches_id1'
    )
    coaches_id2 = models.ForeignKey(
        Coach, on_delete=models.PROTECT,
        related_name='assistant_teams',
        db_column='coaches_id2'
    )

    # ✅ New coach name fields to sync with FK
    coaches_name1 = models.CharField(max_length=50)
    coaches_name2 = models.CharField(max_length=50)

    class Meta:
        db_table = 'teams'
        managed = False

    def __str__(self):
        return self.teams_name

    def save(self, *args, **kwargs):
        # Sync coach names before saving
        if self.coaches_id1:
            self.coaches_name1 = self.coaches_id1.coaches_name
        if self.coaches_id2:
            self.coaches_name2 = self.coaches_id2.coaches_name
        super().save(*args, **kwargs)

class ContactList(models.Model):
    playername = models.CharField(max_length=100)
    dob = models.DateField()
    teams_name = models.CharField(max_length=100)
    contactemail = models.EmailField()
    phonenumber = models.CharField(max_length=20)
    memo = models.TextField(blank=True)

    class Meta:
        db_table = 'contactlist'

    def __str__(self):
        return f"{self.playername} ({self.teams_name})"

class CoachCertificate(models.Model):
    certificate_id = models.AutoField(primary_key=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, db_column='coach_id')
    cert_type = models.CharField(max_length=100)
    file_path = models.TextField()
    date_issued = models.DateField()
    valid_until = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'coach_certificates'
        managed = False

    def __str__(self):
        return f'{self.cert_type} for {self.coach.coaches_name}'


class PML(models.Model):
    pml_id = models.AutoField(primary_key=True)  # ⬅️ Auto-incrementing ID
    pml_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'pml'

    def __str__(self):
        return self.pml_name

class Parents(models.Model):
    parents_id = models.IntegerField(primary_key=True)
    parents_name = models.CharField(max_length=50)
    parents_dob = models.DateField()
    parents_email = models.EmailField()
    parents_mobile_number = models.CharField(max_length=20)
    parents_address = models.CharField(50)

    parents_member_1 = models.ForeignKey(PML, on_delete=models.SET_NULL, null=True, blank=True, db_column='parents_member_1', related_name='member_1_parents')
    parents_member_2 = models.ForeignKey(PML, on_delete=models.SET_NULL, null=True, blank=True, db_column='parents_member_2', related_name='member_2_parents')
    parents_member_3 = models.ForeignKey(PML, on_delete=models.SET_NULL, null=True, blank=True, db_column='parents_member_3', related_name='member_3_parents')

    member_1 = models.CharField(max_length=255, blank=True, null=True)
    member_2 = models.CharField(max_length=255, blank=True, null=True)
    member_3 = models.CharField(max_length=255, blank=True, null=True)

    parents_member_1_description = models.CharField(max_length=255, blank=True, null=True)
    parents_member_2_description = models.CharField(max_length=255, blank=True, null=True)
    parents_member_3_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parents'

    def clean(self):
        if self.parents_name:
            self.parents_name = self.parents_name.strip()
        if self.parents_email:
            self.parents_email = self.parents_email.strip()
        if self.parents_mobile_number:
            self.parents_mobile_number = self.parents_mobile_number.strip()
        if self.member_1:
            self.member_1 = self.member_1.strip()
        if self.member_2:
            self.member_2 = self.member_2.strip()
        if self.member_3:
            self.member_3 = self.member_3.strip()
        if self.parents_member_1_description:
            self.parents_member_1_description = self.parents_member_1_description.strip()
        if self.parents_member_2_description:
            self.parents_member_2_description = self.parents_member_2_description.strip()
        if self.parents_member_3_description:
            self.parents_member_3_description = self.parents_member_3_description.strip()

class Gender(models.Model):
    gender_id = models.IntegerField(primary_key=True)
    gender_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'gender'
        managed = False

    def __str__(self):
        return self.gender_name


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(max_length=50)
    player_bi_number = models.IntegerField()
    player_team = models.CharField(max_length=20)
    player_team_id = models.IntegerField()
    player_role = models.CharField(max_length=50)
    player_role_id = models.IntegerField()
    player_other_roles = models.CharField(max_length=50, blank=True, null=True)
    player_address = models.CharField(max_length=100, blank=True, null=True)
    player_dob = models.DateField(blank=True, null=True)
    player_email = models.CharField(max_length=50)
    player_primary_mobile_number = models.CharField(max_length=20)
    player_contact_name1 = models.CharField(max_length=50, blank=True, null=True)
    player_secundary_mobile_number = models.CharField(max_length=20, blank=True, null=True)
    player_contact_name2 = models.CharField(max_length=50, blank=True, null=True)
    #gender_id = models.IntegerField()
    gender = models.ForeignKey(
    Gender, on_delete=models.SET_NULL,
    null=True, db_column='gender_id',
    related_name='players'
    )
    gender_specify = models.CharField(max_length=50, blank=True, null=True)
    player_medical_conditions = models.CharField(max_length=50, blank=True, null=True)
    participation_member_training = models.SmallIntegerField(blank=True, null=True)
    participation_member_play_matches = models.SmallIntegerField(blank=True, null=True)
    participation_member_other_activities = models.CharField(max_length=50, blank=True, null=True)
    photo_link = models.CharField(max_length=200, blank=True, null=True)
    player_membership_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    player_active = models.SmallIntegerField()
    player_transfer_out = models.SmallIntegerField(blank=True, null=True, default=0)
    player_jersey = models.IntegerField(blank=True, null=True)
    sent_membership = models.SmallIntegerField(default=0)
    created = models.DateTimeField(blank=True, null=True)
    player_committee_member = models.SmallIntegerField(blank=True, null=True, default=0)
    player_member_1 = models.IntegerField(blank=True, null=True)
    player_member_2 = models.IntegerField(blank=True, null=True)
    player_member_3 = models.IntegerField(blank=True, null=True)
    photo_cons = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'player'
        managed = False

    def __str__(self):
        return self.player_name

    def clean(self):
        for field_name in [
            'player_name', 'player_address', 'player_email',
            'player_primary_mobile_number', 'player_contact_name1',
            'player_contact_name2', 'gender_specify',
            'player_medical_conditions', 'participation_member_other_activities'
        ]:
            value = getattr(self, field_name, None)
            if isinstance(value, str):
                setattr(self, field_name, value.strip())

class ParentsLink(models.Model):
    id = models.IntegerField(primary_key=True)
    player_id = models.IntegerField()
    parents_id = models.IntegerField()

    class Meta:
        db_table = 'parents_link'
        managed = False

class SportsLink(models.Model):
    id = models.IntegerField(primary_key=True)  # Manual ID
    player_id = models.IntegerField()
    sports_id = models.IntegerField()

    class Meta:
        db_table = 'sports_link'
        managed = False

class ClubLink(models.Model):
    id = models.IntegerField(primary_key=True)
    player_id = models.IntegerField()
    clubs_id = models.IntegerField()

    class Meta:
        db_table = 'club_link'
        managed = False

class OtherSports(models.Model):
    sports_id = models.IntegerField(primary_key=True)
    sports_name = models.CharField(max_length=20)
    sports_description = models.CharField(max_length=100)

    class Meta:
        db_table = 'other_sports'
        managed = False

    def __str__(self):
        return self.sports_name

class OtherClubs(models.Model):
    clubs_id = models.IntegerField(primary_key=True)
    clubs_name = models.CharField(max_length=20)
    clubs_description = models.CharField(max_length=100)

    class Meta:
        db_table = 'other_clubs'
        managed = False

    def __str__(self):
        return self.clubs_name

class Role(models.Model):
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'role'
        managed = False

    def __str__(self):
        return self.role_name


class PT(models.Model):
    payments_type_id = models.IntegerField(primary_key=True)
    payments_type_name = models.CharField(max_length=50)
    icon_no = models.SmallIntegerField()

    class Meta:
        db_table = 'pt'
        managed = False

    def __str__(self):
        return self.payments_type_name


class Payments(models.Model):
    payments_id = models.IntegerField(primary_key=True)
    player_id = models.IntegerField()
    payments_date = models.DateTimeField()
    payments_description = models.CharField(max_length=100)
    payments_type = models.IntegerField()
    payments_amount = models.DecimalField(max_digits=15, decimal_places=2)
    web = models.SmallIntegerField(blank=True, null=True)
    discount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'payments'
        managed = False

    def __str__(self):
        return f"Payment #{self.payments_id} - {self.payments_amount} EUR"