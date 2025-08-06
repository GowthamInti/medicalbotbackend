import argparse
from unstructured.partition.auto import partition
from unstructured.documents.elements import Text, Table

def parse_image_and_print(image_path: str):
    """Parses an image using unstructured.io and prints extracted text and tables."""
    try:
        # Use partition to process the image file
        elements = partition(filename=image_path)

        print(f"\n--- Extracted Content from {image_path} ---\n")
        for i, element in enumerate(elements):
            if isinstance(element, Text):
                print(f"[Text Element {i+1}]:\n{element.text}\n")
            elif isinstance(element, Table):
                print(f"[Table Element {i+1}]:\n{element.text}\n") # Or element.metadata.text_as_html
            else:
                print(f"[Other Element {i+1}]: {type(element).__name__}\n")

    except FileNotFoundError:
        print(f"Error: File not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    parse_image_and_print("/usr/src/app/app/app/screeshot.png")