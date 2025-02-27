# DirXtract

DirXtract is a simple tool created to quickly export a file tree of a selected directory and the contents of selected files in a structured text format. It’s designed for working with text-based LLMs, making it easy to provide code files and directory structures in a way that’s readable and useful for AI models.

## What It Does

-   Generates a text-based directory tree of your codebase.
-   Lets you select which files and folders to include.
-   Exports file contents along with the structure in a clean format.
-   Has a "Copy to Clipboard" button for quick pasting into AI chats.
-   Customizable setting to exclude specific files, folders or extensions that you never want to see in the file tree (eg. `.DS_Store`).

## Running DirXtract

1.  Install dependencies:

    ```bash
    pip install PyQt5
    ```

2.  Run the program:

    ```bash
    python DirXtract.py
    ```

## How to Use

1.  **Select a Folder** – Pick the directory you want to export.
2.  **Adjust Selections** – Use checkboxes to include/exclude files.
3.  **View File Tree** – See a structured text version of your directory.
4.  **Export with Contents** – Output the file tree along with file contents.
5.  **Copy to Clipboard** – Quickly paste the output where you need it.

## Example Output





```
-----------------------------
└── DirXtract/
    ├── config/
    │   └── global_ignore.json
    ├── Dirxtract.py
    ├── AnotherDIR
    │   └── Dirb.py
    ├── README.md
    └── WOW.md

<DirXtract/config/global_ignore.json>
[
    ".DS_Store",
    ".git",
    "__pycache__",
    "*.tmp",
    "CNAME",
    ".gitignore",
    "test"
]
</DirXtract/config/global_ignore.json>

<DirXtract/Dirxtract.py>
Rest of files...
```

## Why I Built It

I got tired of manually copying and pasting code when asking LLMs for help. This just makes it easier to package up a project, send it to an AI, and get useful responses without missing context.

## License

This code is provided as-is, with no guarantees or restrictions. Use it however you like with no restriction.

## Author

*   **MitchBoss** - [GitHub Profile](https://github.com/MitchBoss)