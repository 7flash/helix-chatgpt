# helix-chatgpt

https://github.com/7flash/helix-chatgpt/assets/4569866/59ef07fe-ddab-4a90-b1bc-4169ff54334c

## Overview

This guide provides instructions on how to integrate a CLI-based text transformation and AI completion program with the Warp terminal and Helix editor. The integration facilitates an efficient workflow for generating and processing prompts, leveraging the capabilities of the program within a development environment optimized for productivity.

## Prerequisites

- **Warp Terminal**: A modern terminal application that supports scripting and advanced features.
- **Helix Editor**: A post-modern modal text editor that is efficient and lightweight.
- **Python 3**: The programming language used to write the CLI-based program.
- **Required Python Packages**: Ensure `requests`, `bs4`, and `OpenAI` packages are installed.

## Setup Script

The script automates the process of creating a new prompt file, opening it for editing, running the text transformation and AI completion program, and then opening the output file for review.

### Script Breakdown

1. **Date Variables**:
   - `current_month_day`: Stores the current month and day in `MMMDD` format.
   - `xit`: A unique timestamp in `MMMDD-HHMMSS` format used to name files.

2. **Directories and File Paths**:
   - `pit`: The directory path where prompt files are stored, organized by date.
   - `ipixit`: The input file path for the prompt to be edited.
   - `opixit`: The output file path for the AI-completed text.
   - `zit`: The path to the Python script that performs text transformation and AI completion.

3. **Creating the Directory**: Checks if the directory for the current day's prompts exists; if not, it creates it.

4. **Opening Input File for Editing**: Uses the Helix editor (`hx`) to open the newly created input file for editing.

5. **Running the Program**: After editing, the script runs the Python program, passing the input file path and additional arguments (`--model` and `--temperature`) to it.

6. **Opening the Output File**: Once the program completes, the output file is opened in the Helix editor for review.

### Script

```bash
current_month_day=$(date +%b%d)
xit="$(date +"%b%d-%H%M%S")"

pit="Documents/$current_month_day-prompts"
[ ! -d "$HOME/$pit" ] && mkdir -p "$HOME/$pit"
ipixit="$HOME/$pit/$xit-in.txt"
opixit="$HOME/$pit/$xit-out.txt"

zit="$HOME/Documents/main.py"

hx $ipixit && echo $ipixit && python3 $zit $ipixit --model=gpt-4-0613 --temperature=0.0 && hx $opixit && echo $opixit
```

## Usage

1. **Prepare the Environment**: Ensure the Warp terminal and Helix editor are installed and configured on your system.

2. **Run the Script**: Execute the script from the Warp terminal. This will:
   - Create a new input file for today's date.
   - Open the input file in the Helix editor for you to enter the prompt.
   - Run the text transformation and AI completion program on the prompt.
   - Open the output file in the Helix editor for review.

3. **Edit and Review**: Use the Helix editor to enter your prompt and review the AI-generated completion.

## How It Works

1. **Accepting CLI Arguments**: The program starts by accepting command-line arguments that specify the path to the input file, the AI model name, the temperature setting for AI completion, and whether to write headers in the output.

2. **Reading the Input File**: It reads the content of the specified file, removing any leading or trailing whitespace.

3. **Resolving Links**: The program then processes the content to resolve any links it contains. This involves fetching the content from the linked files or web pages and replacing the links with the fetched content. The program supports both file and HTTP/HTTPS links.

4. **Structuring Messages**: The content is then parsed into a structured format, distinguishing between different roles (e.g., user, assistant, system) based on markers within the text.

5. **Writing the Structured Prompt**: The structured messages are written to a new file, which serves as the input for the AI completion task.

6. **Generating AI Completion**: The program uses the specified AI model to generate a completion for the structured prompt.

7. **Writing the AI Completion**: Finally, the AI-generated completion is written to another file, marking the end of the process.

## Key Functions

### `main(prompt_path, model_name, temperature, write_headers)`

The main function orchestrates the entire process, from reading the input file to writing the AI completion.

### `parse_prompt_into_messages(prompt)`

This function parses the input content into a structured format, identifying different roles based on predefined markers.

### `resolve_links(content, write_headers, is_recursive=False)`

Resolves links within the content, fetching and incorporating linked content. It supports both recursion and the inclusion of headers in the output.

### `fetch_file_content(file_path, selector)`

Fetches content from a file, optionally filtering the content based on a selector that identifies specific sections of the file.

### `fetch_web_content(link)`

Fetches content from a web page specified by a URL.

