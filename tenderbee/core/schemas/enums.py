"""Core enumeration types for TenderBee."""
from enum import Enum


class VerdictStatus(str, Enum):
    VERIFIED = "VERIFIED"
    VERIFIED_WITH_WARNING = "VERIFIED_WITH_WARNING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"
    WAIVED = "WAIVED"


class ReadinessState(str, Enum):
    BLOCKED = "BLOCKED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    READY = "READY"


class RuleType(str, Enum):
    DOCUMENT_REQUIRED = "document_required"
    FIELD_IN_SET = "field_in_set"
    NUMERIC_THRESHOLD = "numeric_threshold"
    DATE_VALIDITY = "date_validity"
    IDENTIFIER_PRESENT = "identifier_present"
    CROSS_DOCUMENT_MATCH = "cross_document_match"
    EXTERNAL_CHECK = "external_check"


class RuleStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    CONFIRMED = "CONFIRMED"
    FROZEN = "FROZEN"


class DocumentType(str, Enum):
    UDYAM_CERTIFICATE = "udyam_certificate"
    CA_TURNOVER_CERTIFICATE = "ca_turnover_certificate"
    NSIC_REGISTRATION = "nsic_registration"
    TENDER_NOTICE = "tender_notice"
    OTHER = "other"


class EnterpriseType(str, Enum):
    MICRO = "MICRO"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    UNKNOWN = "UNKNOWN"


class TurnoverUnit(str, Enum):
    INR = "INR"
    RUPEES = "RUPEES"
    THOUSANDS = "THOUSANDS"
    LAKHS = "LAKHS"
    CRORES = "CRORES"
    UNKNOWN = "UNKNOWN"


class ReasonCode(str, Enum):
    # Blueprint Reason-Code Catalogue (Sections 11 & 14)
    DOC_MISSING = "DOC_MISSING"
    THRESHOLD_NOT_MET = "THRESHOLD_NOT_MET"
    NIC_NOT_COVERED = "NIC_NOT_COVERED"
    UDIN_MISSING = "UDIN_MISSING"
    DOC_EXPIRED_BEFORE_REF_DATE = "DOC_EXPIRED_BEFORE_REF_DATE"
    INSUFFICIENT_YEARS = "INSUFFICIENT_YEARS"
    UNIT_AMBIGUOUS = "UNIT_AMBIGUOUS"
    OCR_LOW_CONF = "OCR_LOW_CONF"
    QUOTE_NOT_GROUNDED = "QUOTE_NOT_GROUNDED"
    RULE_AMBIGUOUS = "RULE_AMBIGUOUS"
    NAME_MISMATCH = "NAME_MISMATCH"
    EXTERNAL_UNAVAILABLE = "EXTERNAL_UNAVAILABLE"
    STATED_AVG_MISMATCH = "STATED_AVG_MISMATCH"
    CONFIDENCE_MODERATE = "CONFIDENCE_MODERATE"
    STALE_RULE_PACK = "STALE_RULE_PACK"
    CHECK_NOT_RUN = "CHECK_NOT_RUN"
    OK = "OK"
