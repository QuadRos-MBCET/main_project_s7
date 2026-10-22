from backend.app.db.models import SafetyClassification, ModerationAction, AgeGroup

class PolicyService:
    @staticmethod
    def determine_publication_action(classification: SafetyClassification) -> ModerationAction:
        """
        Determines platform publication action based on content safety classification.
        """
        if classification == SafetyClassification.SAFE_FOR_ALL:
            return ModerationAction.APPROVE
        elif classification in [SafetyClassification.SAFE_14_PLUS, SafetyClassification.AGE_14_PLUS,
                                SafetyClassification.SAFE_18_PLUS, SafetyClassification.AGE_18_PLUS]:
            return ModerationAction.RESTRICT if hasattr(ModerationAction, "RESTRICT") else ModerationAction.AGE_RESTRICT
        elif classification == SafetyClassification.REQUIRES_HUMAN_REVIEW:
            return ModerationAction.HUMAN_REVIEW
        else:  # UNSAFE_FOR_ALL
            return ModerationAction.REJECT

    @staticmethod
    def evaluate_user_access(
        classification: SafetyClassification,
        user_age_group: AgeGroup
    ) -> bool:
        """
        Evaluates whether a specific user is permitted to view an advertisement.
        IMPORTANT POLICY SEPARATION:
        - REQUIRES_HUMAN_REVIEW: NEVER ALLOWED for anyone. Withheld from all feeds.
        - UNSAFE_FOR_ALL: NEVER ALLOWED for anyone (including adults).
        - SAFE_18_PLUS / AGE_18_PLUS: Only allowed if user is AGE_18_PLUS.
        - SAFE_14_PLUS / AGE_14_PLUS: Allowed for AGE_14_TO_17 and AGE_18_PLUS.
        - SAFE_FOR_ALL: Allowed for all users.
        """
        if classification in [SafetyClassification.UNSAFE_FOR_ALL, SafetyClassification.REQUIRES_HUMAN_REVIEW]:
            return False

        if classification in [SafetyClassification.SAFE_18_PLUS, SafetyClassification.AGE_18_PLUS]:
            return user_age_group == AgeGroup.AGE_18_PLUS

        if classification in [SafetyClassification.SAFE_14_PLUS, SafetyClassification.AGE_14_PLUS]:
            return user_age_group in [AgeGroup.AGE_14_TO_17, AgeGroup.AGE_18_PLUS]

        if classification == SafetyClassification.SAFE_FOR_ALL:
            return True

        return False
