from typing import Optional

from project.data import models


def create_rsvp_for_guest(guest: models.Person) -> tuple[models.RSVP, bool]:
    rsvp, created = models.RSVP.objects.get_or_create(guest=guest)
    return rsvp, created


def update_rsvp_basics(
    *,
    guest: models.Person,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    can_come_to_ceremony: bool = False,
    can_come_to_reception: bool = False,
    song_suggestion: Optional[str] = None,
    plus_one: bool = False,
    plus_one_firstname: Optional[str] = None,
    plus_one_lastname: Optional[str] = None,
    plus_one_email: Optional[str] = None,
    plus_one_phone: Optional[str] = None,
) -> models.RSVP:
    """
    Updates the basic RSVP information for a guest, including their contact details
    and their plus-one information.
    """
    # Update guest contact info
    if email is not None:
        guest.email = email
    if phone is not None:
        guest.phone = phone
    guest.save()

    rsvp, _ = create_rsvp_for_guest(guest)
    rsvp.can_come_to_ceremony = can_come_to_ceremony
    rsvp.can_come_to_reception = can_come_to_reception
    if song_suggestion is not None:
        rsvp.song_suggestion = song_suggestion

    if plus_one:
        if not rsvp.plus_one:
            plus_one_person = models.Person.objects.create(
                firstname=plus_one_firstname or "",
                lastname=plus_one_lastname or "",
                email=plus_one_email or "",
                phone=plus_one_phone or "",
                type=models.Person.Type.STANDARD,
                allowed_plus_one=False,
                invited_to_ceremony=guest.invited_to_ceremony,
                invited_to_reception=guest.invited_to_reception,
                allowed_to_stay_onsite=guest.allowed_to_stay_onsite,
                allowed_to_stay_in_yurt=guest.allowed_to_stay_in_yurt,
                allowed_to_stay_night_after_reception=guest.allowed_to_stay_night_after_reception,
            )

            rsvp.plus_one = plus_one_person  # type: ignore[assignment]

            # Ensure the plus-one also has an RSVP record
            models.RSVP.objects.get_or_create(
                guest=plus_one_person,
                defaults={
                    "can_come_to_ceremony": can_come_to_ceremony,
                    "can_come_to_reception": can_come_to_reception,
                },
            )
        else:
            # Update existing plus one details
            rsvp.plus_one.firstname = plus_one_firstname or rsvp.plus_one.firstname
            rsvp.plus_one.lastname = plus_one_lastname or rsvp.plus_one.lastname
            rsvp.plus_one.email = plus_one_email or rsvp.plus_one.email
            rsvp.plus_one.phone = plus_one_phone or rsvp.plus_one.phone
            rsvp.plus_one.save()
    else:
        # If plus_one is False, remove existing plus one if it exists
        if rsvp.plus_one:
            plus_one_person = rsvp.plus_one
            rsvp.plus_one = None
            rsvp.save()
            # Clean up the plus one's RSVP and Person record
            models.RSVP.objects.filter(guest=plus_one_person).delete()
            plus_one_person.delete()

    rsvp.save()
    return rsvp


def update_rsvp_dietary(
    *,
    rsvp: models.RSVP,
    dietary_categories: list[str],
    dietary_other_detail: str = "",
    plus_one_dietary_categories: Optional[list[str]] = None,
    plus_one_dietary_other_detail: str = "",
) -> models.RSVP:
    """
    Updates dietary requirements for a guest and optionally their plus-one.
    """

    def _get_foods(categories: list[str], other_detail: str) -> list[models.Food]:
        foods = []
        for category in categories:
            # Note: This logic assumes Food objects are unique by category and detail.
            # Depending on requirements, you might want to adjust how Food objects are managed.
            detail = other_detail if category == models.Food.Category.OTHER else ""
            food, _ = models.Food.objects.get_or_create(
                category=category,
                detail=detail,
            )
            foods.append(food)
        return foods

    # Update guest's dietary requirements
    rsvp.dietary_requirements.set(_get_foods(dietary_categories, dietary_other_detail))
    rsvp.save()

    # Update plus-one's dietary requirements if they exist
    if rsvp.plus_one and plus_one_dietary_categories is not None:
        plus_one_rsvp, _ = models.RSVP.objects.get_or_create(
            guest=rsvp.plus_one,
            defaults={
                "can_come_to_ceremony": rsvp.can_come_to_ceremony,
                "can_come_to_reception": rsvp.can_come_to_reception,
            },
        )
        plus_one_rsvp.dietary_requirements.set(
            _get_foods(plus_one_dietary_categories, plus_one_dietary_other_detail)
        )
        plus_one_rsvp.save()

    return rsvp


def update_rsvp_accommodation(
    *,
    rsvp: models.RSVP,
    staying_preference: Optional[str] = None,
    staying_night_after_reception: Optional[bool] = None,
    morning_meal_day_after_reception: Optional[bool] = None,
    evening_meal_day_after_reception: Optional[bool] = None,
    day_after_reception_suggestion: Optional[str] = None,
) -> models.RSVP:
    """
    Updates accommodation and post-reception preferences for a guest.
    """
    if staying_preference is not None:
        rsvp.staying_preference = staying_preference
    if staying_night_after_reception is not None:
        rsvp.staying_night_after_reception = staying_night_after_reception
    if morning_meal_day_after_reception is not None:
        rsvp.morning_meal_day_after_reception = morning_meal_day_after_reception
    if evening_meal_day_after_reception is not None:
        rsvp.evening_meal_day_after_reception = evening_meal_day_after_reception
    if day_after_reception_suggestion is not None:
        rsvp.day_after_reception_suggestion = day_after_reception_suggestion

    rsvp.save()
    return rsvp
