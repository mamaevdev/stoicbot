import os
import fitz
import json
from pathlib import Path
from typing import NamedTuple

PARSING_FOLDER = Path("./pdf_parsing/")
RESULT_FILE_PATH = PARSING_FOLDER / "Stoic_log.json"

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
MIN_QUOTE_SOURCE_LENGTH = 5
START_QUOTE_SYMBOL = "\u201c"  # Origin: “
END_QUOTE_SYMBOL = "\u201d"  # Origin: ”
START_SOURCE_SYMBOL = "\u2014"  # Origin: —


class ParsedStoicPageContent(NamedTuple):
    """
    A named tuple to store the parsed content of a page from The Daily Stoic book.
    """

    title: str
    quote: str
    quote_source: str
    explanation: str


class FirstLinesData(NamedTuple):
    """
    A named tuple to store the parsed data of the first lines of a page and the remaining lines.
    """

    explanation_first_letter: str
    date: str
    title: str
    remaining_lines: list


class Parser:
    """
        Parses The Daily Stoic book.

        The book is a PDF file with a specific structure.

    Attributes:
        PARSING_FOLDER (Path): The path to the folder containing the PDF files.
        RESULT_FILE_PATH (Path): The path to the output JSON file.
        FIRST_STOIC_PAGE (int): The page number of the first stoic page in the PDF.
        LAST_STOIC_PAGE (int): The page number of the last stoic page in the PDF.
        SKIP_NON_STOIC_PAGES (list): A list of page numbers to skip that are not stoic pages.
        MIN_QUOTE_SOURCE_LENGTH (int): The minimum length of a quote source.
        START_QUOTE_SYMBOL (str): The symbol indicating the start of a quote.
        END_QUOTE_SYMBOL (str): The symbol indicating the end of a quote.
        START_SOURCE_SYMBOL (str): The symbol indicating the start of a quote source.

    Public methods:
        get_pdf_files_paths(folder=Path(".")): Returns a list of all pdf files in a folder.
        parse_book(pdf_file): Parses The Daily Stoic book and returns a dictionary with the entries.
    """

    def get_pdf_files_paths(self, directory=Path(".")) -> list[Path]:
        """
        Returns a list of all pdf files in a folder.

        Args:
            directory (Path): The path to the directory containing the PDF files. Defaults to the current directory.

        Returns:
            list: A list of PDF file paths.
        """
        return [
            Path(directory / file) for file in os.listdir(directory) if ".pdf" in file
        ]

    def parse_book(self, pdf_file: Path) -> dict[str, dict[ParsedStoicPageContent]]:
        """
        Parses The Daily Stoic book and returns a dictionary of entries with keys "date".
            Each entry is a dictionary with keys "title", "quote", "quote_source", and "explanation".
            Example of the output dictionary entry:
                date: {
                    title,
                    quote,
                    quote_source,
                    explanation
                }

        Args:
            pdf_file (Path): The path to the PDF file.

        Returns:
            dict: A dictionary with the parsed entries. The keys are dates and the values are dictionaries.
        """
        entries = {}

        with fitz.open(pdf_file) as f:
            for page in f:
                if page.number < FIRST_STOIC_PAGE:
                    continue
                if page.number > LAST_STOIC_PAGE:
                    break
                if page.number in SKIP_NON_STOIC_PAGES:
                    continue

                date, parsed_page_content = self._parse_page_text(page.get_text())

                entries[date] = parsed_page_content._asdict()

        return entries

    def _parse_page_text(self, text: str) -> tuple[str, ParsedStoicPageContent]:
        """
        Extracts the date, quote, quote_source and explanation from a page of the Daily Stoic.

        Args:
            text (str): The text content of the page.

        Returns:
            NamedTuple: A NamedTuple 'ParsedPageContent' containing the date (str), title (str), quote (str), quote_source (str), and explanation (str).
        """
        lines = text.replace("\t", " ").splitlines()

        quote_lines = []
        explanation_lines = []
        quote_found = False
        quote_source_found = False

        first_lines_data = self._parse_letter_date_title(lines)

        for index, line in enumerate(first_lines_data.remaining_lines):
            line = line.strip()

            if not quote_found:
                quote_lines.append(line)
                quote_found = self._is_end_of_quote(
                    line, first_lines_data.remaining_lines[index + 1].strip()
                )
                continue

            if not quote_source_found and (
                line[0] == START_SOURCE_SYMBOL
                or line[0:MIN_QUOTE_SOURCE_LENGTH].isupper()
            ):
                quote_source = START_SOURCE_SYMBOL
                # This is required to handle cases where the START_SOURCE_SYMBOL is missing
                quote_source += line[1:] if (line[0] == START_SOURCE_SYMBOL) else line
                quote_source = quote_source.strip()
                quote_source_found = True
                continue

            explanation_lines.append(line)

        quote = self._apply_quotes(" ".join(quote_lines).strip())
        explanation = (
            first_lines_data.explanation_first_letter + " ".join(explanation_lines)
        ).strip()

        return (
            first_lines_data.date,
            ParsedStoicPageContent(
                first_lines_data.title,
                quote,
                quote_source,
                explanation,
            ),
        )

    def _parse_letter_date_title(self, lines) -> FirstLinesData:
        """
        Extracts the first letter of explanation, date, and title from the first lines of the page.

        Args:
            lines (list): The lines of text on the page.

        Returns:
            NamedTuple: A NamedTuple 'FirstLinesData' containing the explanation_first_letter (str), date (str), title (str), and remaining_lines (list of str).
        """
        index = 0
        explanation_first_letter = ""

        # Required to cover cases where the first letter is empty or the first letter is prefixed with quote.
        if len(lines[index]) == 1 or len(lines[index]) == 2:
            explanation_first_letter = lines[index].strip()
            index += 1

        date = lines[index].strip()[:-2]
        index += 1

        # Required to cover cases with invisible linebreaks in titles that splits them into multiple lines.
        title_lines = []
        while lines[index].isupper():
            title_lines.append(lines[index])
            index += 1
        title = "".join(title_lines).strip()

        return FirstLinesData(explanation_first_letter, date, title, lines[index:])

    def _is_end_of_quote(self, line, next_line) -> bool:
        """
        Checks if the current line is the end of quote.

        Args:
            line (str): The current line of text.
            next_line (str): The next line of text.

        Returns:
            bool: True if the current line is the end of quote, False otherwise.
        """
        # This is required to handle cases where the END_QUOTE_SYMBOL is missing
        return (
            line[-1] == END_QUOTE_SYMBOL
            or (
                next_line[0] == START_SOURCE_SYMBOL
                and next_line[1 : MIN_QUOTE_SOURCE_LENGTH + 1].isupper()
            )
            or next_line[0:MIN_QUOTE_SOURCE_LENGTH].isupper()
        )

    def _apply_quotes(self, quote) -> str:
        """
        Adds quotes to the quote text.

        Args:
            quote (str): The quote text.

        Returns:
            str: The quote text surrounded by quotes.
        """
        if quote[0] != START_QUOTE_SYMBOL:
            quote = START_QUOTE_SYMBOL + quote
        if quote[-1] != END_QUOTE_SYMBOL:
            quote = quote + END_QUOTE_SYMBOL
        return quote


if __name__ == "__main__":
    book_parser = Parser()
    book_pdf_files = book_parser.get_pdf_files_paths(PARSING_FOLDER)

    if len(book_pdf_files) and book_pdf_files[0]:
        book_content = book_parser.parse_book(book_pdf_files[0])
        with open(RESULT_FILE_PATH, "w") as output_file:
            json.dump(book_content, output_file, indent=4)
