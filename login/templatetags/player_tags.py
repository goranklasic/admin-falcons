from django import template
from login.models import OtherSports, OtherClubs, Parents

register = template.Library()

@register.filter
def get_sport_name(sport_id):
    sport = OtherSports.objects.filter(sports_id=sport_id).first()
    return sport.sports_name if sport else "—"

@register.filter
def get_sport_desc(sport_id):
    sport = OtherSports.objects.filter(sports_id=sport_id).first()
    return sport.sports_description if sport else "—"

@register.filter
def get_club_name(club_id):
    club = OtherClubs.objects.filter(clubs_id=club_id).first()
    return club.clubs_name if club else "—"

@register.filter
def get_club_desc(club_id):
    club = OtherClubs.objects.filter(clubs_id=club_id).first()
    return club.clubs_description if club else "—"

@register.filter
def get_parent_name(parent_id):
    parent = Parents.objects.filter(parents_id=parent_id).first()
    return parent.parents_name if parent else "—"

@register.filter
def get_parent_email(parent_id):
    parent = Parents.objects.filter(parents_id=parent_id).first()
    return parent.parents_email if parent else "—"

@register.filter
def get_parent_mobile(parent_id):
    parent = Parents.objects.filter(parents_id=parent_id).first()
    return parent.parents_mobile_number if parent else "—"

@register.filter
def get_pt_type(pt_id):
    from login.models import PT
    pt = PT.objects.filter(payments_type_id=pt_id).first()
    return pt.payments_type_name if pt else "—"