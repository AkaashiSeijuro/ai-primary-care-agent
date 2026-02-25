import re
from dataclasses import dataclass
from typing import List, Tuple, Optional

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


def looks_like_emergency(text: str) -> bool:
    t = text.lower()
    return any(re.search(pat, t) for pat in EMERGENCY_TRIGGERS)


def enforce_language_rules(text: str) -> Tuple[bool, List[str]]:
    issues = []
    lower = text.lower()

    for banned in BANNED_PHRASES:
        if banned in lower:
            issues.append(f'Contains banned phrase or jargon: "{banned}"')

    # Recommendations must end with this exact sentence
    if "How does this sound to you?" not in text:
        issues.append('Missing required ending: "How does this sound to you?"')

    # Must include disclaimer in any recommendation or escalation output
    if DISCLAIMER not in text:
        issues.append(f'Missing disclaimer: "{DISCLAIMER}"')

    # If escalation is present, must include remote safety line
    if "Here's what I recommend" in text and looks_like_emergency(text):
        if REMOTE_LIMIT not in text:
            issues.append(f'Missing escalation safety line: "{REMOTE_LIMIT}"')

    return (len(issues) == 0, issues)


def mild_plan(intake: Intake, followup_days: int = 3) -> str:
    # Exactly 3 self-care recs, numbered 1-3, plain language
    # Must include follow-up timeframe and end with "How does this sound to you?"
    # Must not use jargon, must have disclaimer
    response_lines = []

    # Using required acknowledgement form
    response_lines.append("I understand. Let's work through this together.")

    # Validating worry if present in a simple way
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


def emergency_plan(intake: Intake) -> str:
    # Must follow: "Based on what you've told me..." + assessment + "Here's what I recommend..." + action
    # Must include "This is beyond what I can safely assess remotely"
    # Must include disclaimer
    # Must end with "How does this sound to you?"
    response_lines = []

    # Required acknowledgement form
    response_lines.append("I understand. Let's work through this together.")

    # Validating pain if mentioned
    if "pain" in intake.chief_complaint.lower():
        response_lines.append("That sounds really uncomfortable")

    # Validate worry
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


def collect_intake() -> Intake:
    print(f"Hi, I’m here to help. {DISCLAIMER}.")
    chief = input("What brings you in today? ").strip()

    timeline = input(f"{TIMELINE_Q} ").strip()

    severity = input("How bad is it right now on a 0 to 10 scale? ").strip()

    key_details = input("What else is happening with it (for example: where it is, what makes it better or worse, and any other symptoms)? ").strip()

    meds_allergies = input("Any medicines you take regularly, and any allergies? ").strip()

    # Must ask this before recommendations
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

    combined = " ".join([intake.chief_complaint, intake.key_details, intake.timeline])
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
        # Fallback: always escalate if there is any compliance issue
        response = emergency_plan(intake)

    print("\n---\n")
    print(response)
    print("\n---\n")


if __name__ == "__main__":
    main()
