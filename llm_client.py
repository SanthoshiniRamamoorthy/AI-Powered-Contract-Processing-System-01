# app/services/llm_client.py

import json
import subprocess
import requests
from app.config import GROQ_API_KEY, GROQ_MODEL_NAME, USE_OLLAMA_FALLBACK, OLLAMA_MODEL_NAME
from app.utils.logger import logger

CONTRACT_ANALYSIS_PROMPT = """You are an expert Legal Contract AI Assistant.

Your task: Analyze the provided contract text carefully and output a structured JSON object that summarizes all important details clearly and consistently, even if the contract format varies.

Follow this exact output JSON schema:

{
  "contract_title": "<title or type of contract>",
  "parties_involved": [
    {"name": "<Party A>", "role": "<role/organization>"},
    {"name": "<Party B>", "role": "<role/organization>"}
  ],
  "effective_date": "<start or effective date if present>",
  "termination_date": "<expiry/end date if mentioned>",
  "governing_law": "<jurisdiction or law mentioned>",
  "payment_terms": "<summary of payment, compensation, or consideration>",
  "termination_clauses": "<conditions for early termination or breach>",
  "confidentiality_clause": "<summary if applicable>",
  "liability_clause": "<key liability or indemnity details>",
  "renewal_terms": "<auto-renewal or extension conditions>",
  "obligations_summary": [
    {"party": "<Party A>", "obligations": "<short summary>"},
    {"party": "<Party B>", "obligations": "<short summary>"}
  ],
  "identified_risks": [
    {"clause": "<risk clause or issue>", "description": "<what could go wrong>", "severity": "low/medium/high"}
  ],
  "overall_risk_score": <numerical estimate 1-10>,
  "summary": "<concise 5-6 sentence summary of this contract>"
}

Guidelines:
- If any field is missing or not applicable, return null or "Not Specified".
- Extract insights only from the provided text.
- Always respond with ONLY valid JSON - no extra text before or after.
- Ensure all strings are properly escaped and valid JSON format.
- The overall_risk_score must be a number between 1-10.
"""


def groq_api_call(contract_text: str, prompt: str) -> dict:
    """
    Call Groq API with proper error handling.
    
    Args:
        contract_text: The contract text to analyze
        prompt: The system prompt for the LLM
        
    Returns:
        dict: Parsed JSON response from Groq
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Limit contract text to prevent token overflow
        max_chars = 15000
        truncated_text = contract_text[:max_chars]
        if len(contract_text) > max_chars:
            logger.warning(f"Contract text truncated from {len(contract_text)} to {max_chars} characters")
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Analyze this contract:\n\n{truncated_text}"}
        ]
        
        payload = {
            "model": GROQ_MODEL_NAME,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        logger.info(f"Sending request to Groq API with model: {GROQ_MODEL_NAME}")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # Extract content from response
        content = response.json()['choices'][0]['message']['content']
        logger.info("Successfully received response from Groq")
        
        return json.loads(content)
        
    except requests.exceptions.Timeout:
        logger.error("Groq API request timed out")
        raise RuntimeError("Groq API request timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        logger.error(f"Groq API request failed: {e}")
        raise RuntimeError(f"Groq API error: {str(e)}")
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse Groq response: {e}")
        raise RuntimeError("Invalid response format from Groq API")


def ollama_api_call(contract_text: str, prompt: str, model: str = OLLAMA_MODEL_NAME) -> dict:
    """
    Call Ollama locally with robust JSON extraction.
    
    Args:
        contract_text: The contract text to analyze
        prompt: The system prompt for the LLM
        model: The Ollama model name
        
    Returns:
        dict: Parsed JSON response from Ollama
    """
    try:
        # Limit contract text for Ollama (smaller context window)
        max_chars = 10000
        truncated_text = contract_text[:max_chars]
        if len(contract_text) > max_chars:
            logger.warning(f"Contract text truncated from {len(contract_text)} to {max_chars} characters for Ollama")
        
        # Combine prompt with contract text
        full_prompt = f"{prompt}\n\nContract Text:\n{truncated_text}"
        
        logger.info(f"Calling Ollama with model: {model}")
        
        # Use ollama run command
        result = subprocess.run(
            ["ollama", "run", model, full_prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Ollama subprocess failed"
            logger.error(f"Ollama error: {error_msg}")
            raise RuntimeError(f"Ollama error: {error_msg}")
        
        # Extract JSON from output
        output = result.stdout.strip()
        logger.info(f"Ollama output length: {len(output)} characters")
        
        # Find JSON object in the output
        start_idx = output.find('{')
        end_idx = output.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            logger.error(f"No JSON found in Ollama output. First 500 chars: {output[:500]}")
            raise RuntimeError("Ollama did not return valid JSON")
        
        json_str = output[start_idx:end_idx + 1]
        logger.info("Successfully extracted JSON from Ollama response")
        
        return json.loads(json_str)
        
    except subprocess.TimeoutExpired:
        logger.error("Ollama request timed out after 120 seconds")
        raise RuntimeError("Ollama request timed out")
    except FileNotFoundError:
        logger.error("Ollama command not found. Please install Ollama or disable fallback.")
        raise RuntimeError("Ollama not installed")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode Ollama JSON: {e}")
        raise RuntimeError("Ollama response was not valid JSON")


def analyze_contract_llm(contract_text: str) -> dict:
    """
    Main function to analyze contract using LLM with fallback.
    
    Args:
        contract_text: The contract text to analyze
        
    Returns:
        dict: Analysis results as dictionary
    """
    
    # Validate input
    if not contract_text or len(contract_text.strip()) < 50:
        raise ValueError("Contract text is too short or empty")
    
    # Try Groq first
    try:
        logger.info("Attempting Groq API call...")
        response = groq_api_call(contract_text, CONTRACT_ANALYSIS_PROMPT)
        logger.info("Groq API call successful")
        return response
        
    except Exception as groq_error:
        logger.warning(f"Groq failed: {str(groq_error)}")
        
        # Fallback to Ollama if enabled
        if USE_OLLAMA_FALLBACK:
            try:
                logger.info("Falling back to Ollama...")
                response = ollama_api_call(contract_text, CONTRACT_ANALYSIS_PROMPT)
                logger.info("Ollama call successful")
                return response
                
            except Exception as ollama_error:
                logger.error(f"Ollama fallback also failed: {ollama_error}")
                raise RuntimeError(
                    f"Both Groq and Ollama failed. "
                    f"Groq error: {str(groq_error)}. "
                    f"Ollama error: {str(ollama_error)}"
                )
        else:
            # No fallback enabled, re-raise original error
            raise RuntimeError(f"LLM analysis failed: {str(groq_error)}")