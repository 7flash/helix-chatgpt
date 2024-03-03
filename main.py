#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse
from openai import OpenAI


# .main
def main(prompt_path, model_name, temperature, write_headers):
    print("hi")

    prompt_path = os.path.expanduser(prompt_path)
    with open(prompt_path, "r") as file:
        prompt = file.read().strip()

    prompt = resolve_links(prompt, write_headers)
    messages = parse_prompt_into_messages(prompt)

    prompt_file_path = os.path.join(
        os.path.dirname(prompt_path),
        os.path.basename(prompt_path).replace("-in.txt", "-prompt.txt"),
    )
    with open(prompt_file_path, "w") as prompt_file:
        for message in messages:
            prompt_file.write(f"{message['role']}:\n{message['content']}\n")
    client = OpenAI()

    completion = client.chat.completions.create(
        model=model_name, messages=messages, temperature=temperature
    )

    answer = completion.choices[0].message.content

    out_file_path = os.path.join(
        os.path.dirname(prompt_path),
        os.path.basename(prompt_path).replace("-in.txt", "-out.txt"),
    )

    with open(out_file_path, "w") as out_file:
        out_file.write(answer)


# .parse_prompt_into_messages
def parse_prompt_into_messages(prompt):
    roles = ["user", "assistant", "system"]
    pattern = r"\|(" + "|".join(roles) + r")\|"

    parts = re.split(pattern, prompt)

    messages = []

    for i in range(1, len(parts), 2):
        role = parts[i]
        content = parts[i + 1].strip()
        if role in roles:
            messages.append({"role": role, "content": content})

    if len(messages) == 0:
        messages.append({"role": "user", "content": prompt})

    return messages


# .resolve_links
def resolve_links(content, write_headers, is_recursive=False):
    linkRegex = r"(file:\/[^\s]+)|(http[s]?:\/\/[^\s]+)"
    print(f"linkRegexp {linkRegex}")
    matches = re.findall(linkRegex, content)

    if not matches:
        return content

    def replace_with_newline(match):
        return f'{match.group(0)}\n"""\n{resolvedContent}\n"""\n'

    for match in matches:
        print(f"match {match[0]}")
        protocol = urlparse(match[0]).scheme
        if protocol == "file":
            path = urlparse(match[0]).path
            print(f"path {path}")
            fileName = path.split("/")[-1]
            print(f"fileName {fileName}")
            selector = None
            if "#" in match[0]:
                _, selector = match[0].split("#")
            print(f"selector {selector} & {path}")
            resolvedContent = fetch_file_content(path, selector)
            resolvedContent = resolvedContent.replace("|user|", "user:")
            resolvedContent = resolvedContent.replace(
                "|assistant|", "assistant:"
            )
            resolvedContent = resolvedContent.replace("|system|", "system:")
            resolvedContent = resolvedContent.replace("\\", "\\\\")
            # if not is_recursive:
            #     resolvedContent = resolve_links(
            #         resolvedContent, write_headers, True
            #     )
            pattern = r"^" + re.escape(match[0]).replace("/", "\/") + r"$"
            print("sub pattern")
            print(pattern)
            if write_headers:
                header = f"{fileName}"
                if selector is not None:
                    header = f"{selector}"
                content = re.sub(
                    pattern,
                    f'{header}\n"""\n{resolvedContent}\n"""',
                    content,
                    flags=re.MULTILINE,
                )
            else:
                content = re.sub(
                    pattern, resolvedContent, content, flags=re.MULTILINE
                )
        elif not is_recursive:
            path = urlparse(match[1]).path
            fileName = path.split("/")[-1]
            print(f"fileName {fileName}")
            resolvedContent = fetch_web_content(match[1])
            resolvedContent = resolvedContent.replace("|user|", "user:")
            resolvedContent = resolvedContent.replace(
                "|assistant|", "assistant:"
            )
            resolvedContent = resolvedContent.replace("|system|", "system:")
            if "#" in match[1]:
                element = match[1].split("#")[-1]
                print(f"element {element}")
                soup = BeautifulSoup(resolvedContent, "html.parser")
                resolvedContent = soup.select(element)[0].get_text()
            if write_headers:
                if selector is not None:
                    content = content.replace(
                        match[1], f'{selector}\n"""\n{resolvedContent}\n"""\n'
                    )
                else:
                    content = content.replace(
                        match[1], f'{fileName}\n"""\n{resolvedContent}\n"""\n'
                    )
            else:
                content = content.replace(match[1], resolvedContent)

    return content


# .fetch_file_content
def fetch_file_content(file_path, selector):
    home_dir = os.path.expanduser("~")
    if not file_path.startswith(home_dir):
        file_path = file_path.lstrip("/")
        file_path = os.path.join(home_dir, file_path)
    print(f"file path {file_path}")
    try:
        with open(file_path, "r") as file:
            content = file.read()
        if selector:
            file_extension = os.path.splitext(file_path)[1]
            if file_extension == ".py":
                comment_symbol = "#"
            else:
                comment_symbol = "//"
            pattern = rf"({re.escape(comment_symbol)}\s?\.{re.escape(selector)}\n)(.*?(?={re.escape(comment_symbol)}\s?\.|Z))"
            print(pattern)
            try:
                matches = re.findall(pattern, content, re.DOTALL)
                segmented_content = matches[0][1]
                return segmented_content.strip()
            except AttributeError:
                print(f"Segment not found for {selector} in {file_path}")
                return ""
        else:
            return content.strip()
    except Exception as e:
        print(f"!!!!!! Failed to fetch file content from {file_path}:", e)
        return ""


# .fetch_web_content
def fetch_web_content(link):
    try:
        response = requests.get(link)
        return response.text
    except Exception as e:
        print(f"!!!! Failed to fetch web content from {link}:", e)
        return ""


# .start
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate response from a prompt file using OpenAI's model and write the response to a new file."
    )
    parser.add_argument(
        "prompt_path",
        type=str,
        help="Path to the file containing the prompt text.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4-0125-preview",
        help="Model name to be used. Default is 'gpt-4-1106-preview'.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature/Creativity. Default is 0.0",
    )
    parser.add_argument(
        "--write-headers",
        action="store_true",
        help="Include file name and link URLs in the resolved content.",
    )

    args = parser.parse_args()

    main(args.prompt_path, args.model, args.temperature, args.write_headers)
