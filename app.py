import re
from dataclasses import dataclass

DISCLAIMER = "I can provide guidance, but I cannot replace an in-person examination"
TIMELINE_Q = "When did this first start, and has it been getting better, worse, or staying the same?"
PRIORITY_Q = "What concerns you most about this?"
REMOTE_LIMIT = "This is beyond what I can safely assess remotely"

EMERGENCY_TRIGGERS = [
    r"\bchest pain\b",
    r"\bchest pressure\b",
    r"\bpressure in (my|the) chest\b",
    r"\btrouble breathing\b",
    r"\bdifficulty breathing\b",
    r"\bcan'?t breathe\b",
    r"\bshortness of breath\b",
    r"\bblue lips\b",
    r"\bfainted\b|\bpassed out\b|\bfainting\b",
    r"\bface droop\b|\bslurred speech\b|\bcan'?t speak\b",
    r"\bone[- ]sided weakness\b|\bweakness on one side\b|\bnumb(ness)? on one side\b",
    r"\bseizure\b",
    r"\bworst headache\b",
    r"\buncontrolled bleeding\b",
]

BANNED_PHRASES = [
    "don't worry",
    "do not worry",
    "hypertension",
    "myocardial",
    "ischemia",
    "dyspnea",
]


@dataclass
class Intake:
    chief_complaint: str
    timeline: str
    severity: str
    key_details: str
    worry: str
    meds_allergies: str


def looks_like_emergency(text):
    t = text.lower()
    for pat in EMERGENCY_TRIGGERS:
        if re.search(pat, t):
            return True
    return False


def enforce_language_rules(text):
    issues = []
    lower = text.lower()

    for banned in BANNED_PHRASES:
        if banned in lower:
            issues.append(f'Contains banned phrase or jargon: "{banned}"')

    if "How does this sound to you?" not in text:
        issues.append('Missing required ending: "How does this sound to you?"')

    if DISCLAIMER not in text:
        issues.append(f'Missing disclaimer: "{DISCLAIMER}"')

    if "Here's what I recommend" in text:
        if REMOTE_LIMIT not in text:
            issues.append(f'Missing escalation safety line: "{REMOTE_LIMIT}"')

    return (len(issues) == 0, issues)


def mild_plan(intake, followup_days=3):
    response_lines = []

    response_lines.append("I understand. Let's work through this together.")

    if intake.worry.strip():
        response_lines.append(
            f"It’s completely understandable that you’re concerned about {intake.worry.strip()}."
        )

    response_lines.append(f"{DISCLAIMER}.")
    response_lines.append(
        "Based on what you’ve told me, this sounds like a mild issue that can often improve with a few simple steps."
    )

    response_lines.append("1) Drink water regularly today and aim for steady meals.")
    response_lines.append("2) Get extra rest tonight and keep caffeine earlier in the day if you use it.")
    response_lines.append("3) Try a short, gentle walk or light stretching if you feel up to it.")

    response_lines.append(
        f"If this isn't improving in {followup_days} days, please contact a primary care clinic or urgent care."
    )
    response_lines.append("How does this sound to you?")

    return "\n".join(response_lines)


def emergency_plan(intake):
    response_lines = []

    response_lines.append("I understand. Let's work through this together.")

    if "pain" in intake.chief_complaint.lower():
        response_lines.append("That sounds really uncomfortable")

    if intake.worry.strip():
        response_lines.append(
            f"It’s completely understandable that you’re concerned about {intake.worry.strip()}."
        )

    response_lines.append(
        "Based on what you've told me, your symptoms could be serious and need urgent in-person care."
    )
    response_lines.append(REMOTE_LIMIT)
    response_lines.append(
        "Here's what I recommend: Call emergency services now. If you can, sit upright, unlock your door, and keep your phone on speaker. If someone is nearby, ask them to stay with you. Do not drive yourself."
    )
    response_lines.append(f"{DISCLAIMER}.")
    response_lines.append("How does this sound to you?")

    return "\n".join(response_lines)


def collect_intake():
    print(f"Hi, I’m here to help. {DISCLAIMER}.")
    chief = input("What brings you in today? ").strip()

    timeline = input(f"{TIMELINE_Q} ").strip()

    severity = input("How bad is it right now on a 0 to 10 scale? ").strip()

    key_details = input(
        "What else is happening with it (for example: where it is, what makes it better or worse, and any other symptoms)? "
    ).strip()

    meds_allergies = input(
        "Any medicines you take regularly, and any allergies? "
    ).strip()

    worry = input(f"{PRIORITY_Q} ").strip()

    return Intake(
        chief_complaint=chief,
        timeline=timeline,
        severity=severity,
        key_details=key_details,
        worry=worry,
        meds_allergies=meds_allergies,
    )


def main():
    intake = collect_intake()

    combined = " ".join(
        [intake.chief_complaint, intake.key_details, intake.timeline]
    )
    is_emergency = looks_like_emergency(combined)

    if is_emergency:
        response = emergency_plan(intake)
    else:
        response = mild_plan(intake, followup_days=3)

    ok, issues = enforce_language_rules(response)

    if not ok:
        print("\n[Internal check] Output violates constraints:")
        for i in issues:
            print(f"- {i}")

        print("\n[Internal check] Refusing to display unsafe/noncompliant output.\n")
        response = emergency_plan(intake)

    print("\n---\n")
    print(response)
    print("\n---\n")


if __name__ == "__main__":
    main()
