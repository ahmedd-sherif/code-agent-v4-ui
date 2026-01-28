from xhtml2pdf import pisa
import os

source_html = "definition/Project_Definition.html"
output_filename = "definition/Project_Definition_v6.pdf"

# Utility function to convert HTML to PDF
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    with open(output_filename, "w+b") as result_file:
        # read source html
        with open(source_html, "r", encoding="utf-8") as f:
            source_content = f.read()

        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(
                source_content,                # the HTML to convert
                dest=result_file)           # file handle to recieve result

    # return True on success and False on errors
    return pisa_status.err

# Main execution
if __name__ == "__main__":
    if not os.path.exists(source_html):
        print(f"Error: Source file {source_html} not found.")
    else:
        print(f"Converting {source_html} to {output_filename}...")
        error = convert_html_to_pdf(source_html, output_filename)
        if error:
            print(f"Failed to generate PDF. Error code: {error}")
        else:
            print(f"Successfully created PDF at: {os.path.abspath(output_filename)}")
