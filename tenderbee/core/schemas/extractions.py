"""Document extraction schemas for Udyam, CA Turnover, and NSIC certificates."""
from typing import List, Optional
from pydantic import BaseModel, Field

from tenderbee.core.schemas.enums import EnterpriseType, TurnoverUnit
from tenderbee.core.schemas.evidence import GroundedField


class TurnoverRow(BaseModel):
    """Single Financial Year turnover row in CA certificate."""
    fy_label: str = Field(..., description="Raw label e.g. '2023-24' or 'FY 22-23'")
    fy_end_date: Optional[str] = Field(
        default=None,
        description="Canonical end date in YYYY-MM-DD (e.g. '2024-03-31')"
    )
    amount_raw: str = Field(..., description="Verbatim amount string from certificate e.g. '52.50'")
    amount_inr: Optional[float] = Field(
        default=None,
        description="Deterministic normalized amount in INR, calculated by Python"
    )
    page: int = Field(..., ge=1, description="Page number where this row appears")
    quote: str = Field(..., description="Verbatim line or table row quote")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    grounded: bool = Field(default=True)


class UdyamExtraction(BaseModel):
    """Schema for extracting fields from an Udyam Registration Certificate."""
    udyam_number: GroundedField[str] = Field(
        ...,
        description="Udyam Registration Number e.g. 'UDYAM-MH-01-0012345'"
    )
    enterprise_name: GroundedField[str] = Field(..., description="Legal name of enterprise")
    enterprise_type: GroundedField[EnterpriseType] = Field(
        ...,
        description="MICRO, SMALL, or MEDIUM classification"
    )
    nic_codes: List[GroundedField[str]] = Field(
        default_factory=list,
        description="List of 2, 4, or 5-digit NIC activity codes (e.g. '812', '8121')"
    )
    registration_date: Optional[GroundedField[str]] = Field(default=None)
    state: Optional[GroundedField[str]] = Field(default=None)
    pin_code: Optional[GroundedField[str]] = Field(default=None)


class CATurnoverExtraction(BaseModel):
    """Schema for extracting fields from a Chartered Accountant Turnover Certificate."""
    ca_firm_name: GroundedField[str] = Field(..., description="Name of the CA firm or practicing CA")
    ca_firm_reg_number: Optional[GroundedField[str]] = Field(
        default=None,
        description="CA Firm Registration Number (FRN)"
    )
    ca_membership_number: Optional[GroundedField[str]] = Field(
        default=None,
        description="CA Membership Number (MRN)"
    )
    udin: GroundedField[str] = Field(
        ...,
        description="18-character ICAI Unique Document Identification Number"
    )
    certificate_date: Optional[GroundedField[str]] = Field(default=None)
    unit_statement: GroundedField[TurnoverUnit] = Field(
        ...,
        description="Turnover currency unit explicitly stated e.g. LAKHS, CRORES, RUPEES"
    )
    turnover_rows: List[TurnoverRow] = Field(
        default_factory=list,
        description="Turnover entries by financial year"
    )
    stated_average: Optional[GroundedField[float]] = Field(
        default=None,
        description="Pre-calculated average turnover printed by the CA, if any"
    )


class NSICExtraction(BaseModel):
    """Schema for extracting fields from an NSIC Registration Certificate."""
    nsic_number: GroundedField[str] = Field(..., description="NSIC registration or certificate number")
    enterprise_name: GroundedField[str] = Field(..., description="Enterprise name")
    store_details: List[GroundedField[str]] = Field(
        default_factory=list,
        description="Service or product descriptions listed under NSIC store details"
    )
    valid_from: Optional[GroundedField[str]] = Field(default=None)
    valid_to: Optional[GroundedField[str]] = Field(default=None)
