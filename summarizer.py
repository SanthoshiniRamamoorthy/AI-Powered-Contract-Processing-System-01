# app/services/summarizer.py
from app.services.parser import extract_text_from_file
from app.services.redactor import redact_pii
from app.services.llm_client import analyze_contract_llm
from app.services.risk_calculator import calculate_overall_risk, get_risk_rating
from app.utils.logger import logger
from app.models.schema import ContractAnalysisResponse
from pydantic import ValidationError

def process_contract(file_path: str) -> ContractAnalysisResponse:
    """
    Orchestrates the contract analysis workflow: Parse -> Redact -> LLM -> Validate/Score.
    """
    try:
        logger.info(f"Starting analysis for file: {file_path}")
        
        # 1. Parse Document
        text = extract_text_from_file(file_path)
        logger.info(f"Document parsed. Text length: {len(text)} characters")
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Extracted text is too short or empty. Please check the file content.")
        
        # 2. Redact PII (Ethical/Security Requirement)
        cleaned_text = redact_pii(text)
        logger.info("PII redaction completed")
        
        # 3. LLM Analysis
        logger.info("Starting LLM analysis...")
        llm_output = analyze_contract_llm(cleaned_text)
        logger.info("LLM analysis completed successfully")
        
        # 4. Validate LLM output
        if not llm_output or not isinstance(llm_output, dict):
            raise RuntimeError("LLM analysis failed or returned invalid data.")
        
        # 5. Calculate risk score if missing or invalid
        overall_score = llm_output.get("overall_risk_score")
        if not isinstance(overall_score, int) or not (0 <= overall_score <= 10):
            identified_risks = llm_output.get("identified_risks", [])
            llm_output["overall_risk_score"] = calculate_overall_risk(identified_risks)
            logger.info(f"Calculated risk score: {llm_output['overall_risk_score']}")
        
        # 6. Add risk rating
        llm_output["risk_rating"] = get_risk_rating(llm_output["overall_risk_score"])
        
        # 7. Ensure all required fields have defaults
        defaults = {
            "contract_title": "Untitled Contract",
            "parties_involved": [],
            "effective_date": "Not Specified",
            "termination_date": "Not Specified",
            "governing_law": "Not Specified",
            "payment_terms": "Not Specified",
            "termination_clauses": "Not Specified",
            "confidentiality_clause": "Not Specified",
            "liability_clause": "Not Specified",
            "renewal_terms": "Not Specified",
            "obligations_summary": [],
            "identified_risks": [],
            "summary": "Contract analysis completed."
        }
        
        # Apply defaults for missing fields
        for key, default_value in defaults.items():
            if key not in llm_output or llm_output[key] is None:
                llm_output[key] = default_value
        
        # 8. Pydantic Validation
        try:
            result = ContractAnalysisResponse(**llm_output)
            logger.info("Response validation successful")
            return result
        except ValidationError as e:
            logger.error(f"LLM output validation failed: {e.errors()}")
            logger.error(f"Problematic LLM output: {llm_output}")
            raise RuntimeError(f"LLM output did not match schema. Errors: {e.errors()}")
    
    except Exception as e:
        logger.error(f"Error in process_contract: {str(e)}")
        raise