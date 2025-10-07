# app/models/schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class PartyInfo(BaseModel):
    """Information about a party in the contract"""
    name: str = Field(description="Name of the party")
    role: str = Field(description="Role or organization type")

class PartyObligation(BaseModel):
    party: str = Field(description="The name of the party involved.")
    obligations: str = Field(description="A short summary of this party's obligations.")

class RiskItem(BaseModel):
    clause: str = Field(description="The specific clause or phrase that constitutes a risk.")
    description: str = Field(description="What the potential risk or issue is.")
    severity: str = Field(description="Risk level: 'low', 'medium', or 'high'.")

class ContractAnalysisResponse(BaseModel):
    contract_title: Optional[str] = Field(None, description="Title or type of contract.")
    parties_involved: Optional[List[PartyInfo]] = Field(default_factory=list, description="List of parties with name and role.")
    effective_date: Optional[str] = Field(None, description="Contract start date.")
    termination_date: Optional[str] = Field(None, description="Contract end/expiry date.")
    governing_law: Optional[str] = Field(None, description="Jurisdiction governing the contract.")
    payment_terms: Optional[str] = Field(None, description="Summary of payment, compensation, or consideration.")
    termination_clauses: Optional[str] = Field(None, description="Conditions for early termination or breach.")
    confidentiality_clause: Optional[str] = Field(None, description="Summary of confidentiality details.")
    liability_clause: Optional[str] = Field(None, description="Key liability or indemnity details.")
    renewal_terms: Optional[str] = Field(None, description="Auto-renewal or extension conditions.")
    obligations_summary: Optional[List[PartyObligation]] = Field(default_factory=list, description="Summary of obligations for each party.")
    identified_risks: Optional[List[RiskItem]] = Field(default_factory=list, description="List of risks flagged by the AI.")
    overall_risk_score: Optional[int] = Field(None, description="Numerical risk score (1-10).")
    risk_rating: Optional[str] = Field(None, description="Risk rating category: LOW, MODERATE, HIGH")
    summary: Optional[str] = Field(None, description="A concise 5-6 sentence summary of the contract.")