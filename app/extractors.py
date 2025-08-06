import io
from typing import List
from fastapi import UploadFile
from unstructured.partition.auto import partition
from unstructured.documents.elements import Text, Table

async def extract_text_from_files(files: List[UploadFile]) -> List[str]:
    """Extract text and tables from a list of uploaded files using unstructured.io."""
    extracted_content = []
    for file in files:
        try:
            # Read file content into a BytesIO object
            file_content = await file.read()
            file_like_object = io.BytesIO(file_content)

            # Use unstructured.partition.auto to process the file
            # Pass file_filename to help unstructured identify the file type
            elements = partition(file=file_like_object, file_filename=file.filename)

            # Process extracted elements
            for element in elements:
                if isinstance(element, Text):
                    extracted_content.append(element.text)
                elif isinstance(element, Table):
                    # For tables, you might want to extract the text representation
                    # or the HTML representation, depending on your LLM's capability.
                    # Here, we'll use the text representation.
                    extracted_content.append(element.text)

        except Exception as e:
            extracted_content.append(f"Error processing file {file.filename}: {str(e)}")
    return extracted_content


