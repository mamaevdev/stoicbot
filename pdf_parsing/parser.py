import os
import fitz
import json

PARSING_FOLDER = "./pdf_parsing/"
RESULT_FILE_PATH = PARSING_FOLDER + "Stoic_log.json"

# These needs to be set according to a specific copy of The Daily Stoic book.
# Page numbers start from 0, so page number in PDF minus 1
FIRST_STOIC_PAGE = 14
LAST_STOIC_PAGE = 392
SKIP_NON_STOIC_PAGES = [
    45,
    75,
    107,
    138,
    139,
    171,
    202,
    234,
    266,
    267,
    298,
    330,
    361,
]
START_QUOTE_SYMBOL = "\u201c"  # Origin: “
END_QUOTE_SYMBOL = "\u201d"  # Origin: ”
START_SOURCE_SYMBOL = "\u2014"  # Origin: —


# Parses The Daily Stoic book.
# The book is a PDF file with a specific structure.
class Parser:
    # Returns a list of all pdf files in a folder.
    def get_pdfs(self, folder="."):
        return [folder + "/" + file for file in os.listdir(folder) if ".pdf" in file]

    # Parses The Daily Stoic book and returns a dictionary with the entries.
    def parse_book(self, pdf_file):
        entries = {}

        with fitz.open(pdf_file) as f:
            for page in f:
                if page.number < FIRST_STOIC_PAGE:
                    continue
                if page.number > LAST_STOIC_PAGE:
                    break
                if page.number in SKIP_NON_STOIC_PAGES:
                    continue

                date, title, quote, quote_source, explanation = self.__parse_page_text(
                    page.get_text()
                )

                entries[date] = {
                    "title": title,
                    "quote": quote,
                    "quote_source": quote_source,
                    "explanation": explanation,
                }

        return entries

    # Extracts the date, source, quote and explanation from a page of the Daily Stoic
    def __parse_page_text(self, text: str):
        lines = text.replace("\t", " ").split("\n")

        quote_lines = []
        explanation_lines = []
        quote_found = False
        quote_source_found = False

        explanation_first_letter, date, title, next_lines = (
            self.__parse_letter_date_title(lines)
        )

        for index, line in enumerate(next_lines):
            line = line.strip()

            if not quote_found:
                quote_lines.append(line)
                quote_found = self.__is_end_of_quote(
                    line, next_lines[index + 1].strip()
                )
                continue

            if not quote_source_found and (
                line[0] == START_SOURCE_SYMBOL or line[0:5].isupper()
            ):
                quote_source = START_SOURCE_SYMBOL
                # This is required to handle cases where the START_SOURCE_SYMBOL is missing
                quote_source += line[1:] if (line[0] == START_SOURCE_SYMBOL) else line
                quote_source = quote_source.strip()
                quote_source_found = True
                continue

            explanation_lines.append(line)

        date = date[:-2]
        quote = self.__apply_quotes(" ".join(quote_lines).strip())
        explanation = (explanation_first_letter + " ".join(explanation_lines)).strip()

        return date, title, quote, quote_source, explanation

    # Extracts the first letter of explanation, date and title from the first lines of the page
    def __parse_letter_date_title(self, lines):
        index = 0
        explanation_first_letter = ""

        # Required to cover cases where the first letter is empty or the first letter is prefixed with quote.
        if len(lines[index]) == 1 or len(lines[index]) == 2:
            explanation_first_letter = lines[index].strip()
            index += 1

        date = lines[index].strip()
        index += 1

        # Required to cover cases where the title is split into multiple lines.
        title_lines = []
        while lines[index].isupper():
            title_lines.append(lines[index])
            index += 1
        title = "".join(title_lines).strip()

        return explanation_first_letter, date, title, lines[index:]

    # Checks if the current line is the end of quote.
    def __is_end_of_quote(self, line, next_line):
        # This is required to handle cases where the END_QUOTE_SYMBOL is missing
        return (
            line[-1] == END_QUOTE_SYMBOL
            or (next_line[0] == START_SOURCE_SYMBOL and next_line[1:6].isupper())
            or next_line[0:5].isupper()
        )

    # Adds quotes to the quote text.
    def __apply_quotes(self, quote):
        if quote[0] != START_QUOTE_SYMBOL:
            quote = START_QUOTE_SYMBOL + quote
        if quote[-1] != END_QUOTE_SYMBOL:
            quote = quote + END_QUOTE_SYMBOL
        return quote


if __name__ == "__main__":
    book_parser = Parser()
    book_file = book_parser.get_pdfs(PARSING_FOLDER)

    if len(book_file) and book_file[0]:
        data = book_parser.parse_book(book_file[0])
        with open(RESULT_FILE_PATH, "w") as output_file:
            json.dump(data, output_file, indent=4)
