# app/routers/contract.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.summarizer import process_contract
from app.models.schema import ContractAnalysisResponse
from app.utils.logger import logger
import os
import tempfile
from pathlib import Path

router = APIRouter()

@router.post("/analyze/", response_model=ContractAnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    contract_type: str = Form(None)
):
    """
    Analyzes an uploaded contract file using the AI pipeline.
    
    Args:
        file: The uploaded contract file (PDF, DOCX, etc.)
        contract_type: Optional contract type for context
    
    Returns:
        ContractAnalysisResponse: Structured analysis of the contract
    """
    file_path = None
    
    try:
        logger.info(f"Received file: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create a temporary file with proper extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            file_path = temp_file.name
            logger.info(f"File saved to temporary location: {file_path}")
        
        # Process and analyze the contract
        result = process_contract(file_path)
        logger.info(f"Analysis completed successfully for: {file.filename}")
        
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except RuntimeError as e:
        logger.error(f"Runtime error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {file_path}: {e}")