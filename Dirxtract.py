import sys
import os
import json
import fnmatch
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel, QHBoxLayout,
    QTextEdit, QDialog, QDialogButtonBox, QListWidget, QInputDialog
)
from PyQt5.QtCore import Qt

# Directory to store configuration for global ignore patterns only
CONFIG_DIR = 'config'
GLOBAL_IGNORE_FILE = 'global_ignore.json'

def get_global_ignore_path():
    """Return the full path for the global ignore JSON file."""
    return os.path.join(CONFIG_DIR, GLOBAL_IGNORE_FILE)

class SettingsDialog(QDialog):
    """Dialog for managing global ignore patterns."""
    def __init__(self, global_ignores, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Global Ignore")
        self.setGeometry(200, 200, 400, 300)
        self.global_ignores = global_ignores.copy()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Global Ignore Patterns:"))
        
        # List widget showing current ignore patterns
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.global_ignores)
        layout.addWidget(self.list_widget)
        
        # Buttons to add or remove ignore patterns
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_ignore)
        buttons_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_ignore)
        buttons_layout.addWidget(self.remove_button)
        layout.addLayout(buttons_layout)
        
        # Dialog buttons to save or cancel changes
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(self.dialog_buttons)
        
        self.setLayout(layout)
    
    def add_ignore(self):
        """Prompt user to add a new ignore pattern."""
        text, ok = QInputDialog.getText(self, "Add Ignore Pattern", "Enter file or directory name to ignore:")
        if ok and text.strip():
            self.list_widget.addItem(text.strip())
    
    def remove_ignore(self):
        """Remove selected ignore patterns from the list."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select items to remove.")
            return
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))
    
    def get_updated_ignores(self):
        """Return the updated list of ignore patterns."""
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

class OutputDialog(QDialog):
    """Dialog to display the generated file tree."""
    def __init__(self, output_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generated File Tree")
        self.setGeometry(150, 150, 600, 400)
        self.init_ui(output_text)
    
    def init_ui(self, text):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(text)
        layout.addWidget(self.text_edit)
        
        # Dialog buttons for copy, save, and close actions
        buttons = QDialogButtonBox()
        self.copy_button = buttons.addButton("Copy to Clipboard", QDialogButtonBox.ActionRole)
        self.save_button = buttons.addButton("Save", QDialogButtonBox.ActionRole)
        self.close_button = buttons.addButton("Close", QDialogButtonBox.RejectRole)
        layout.addWidget(buttons)
        
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.save_button.clicked.connect(self.save_file)
        self.close_button.clicked.connect(self.close)
        
        self.setLayout(layout)
    
    def copy_to_clipboard(self):
        """Copy text content to the clipboard."""
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        QMessageBox.information(self, "Copied", "Text copied to clipboard.")
    
    def save_file(self):
        """Save the displayed file tree to a text file."""
        output_path, _ = QFileDialog.getSaveFileName(self, "Save File Tree", "file_tree.txt", "Text Files (*.txt)")
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Success", f"File tree saved to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file tree:\n{e}")

class ExportOutputDialog(QDialog):
    """Dialog to display the exported file tree with file contents."""
    def __init__(self, tree_text, file_contents, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exported File Tree with Contents")
        self.setGeometry(150, 150, 800, 600)
        self.init_ui(tree_text, file_contents)
    
    def init_ui(self, tree_text, file_contents):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Added separator at the start
        self.text_edit.insertPlainText("-----------------------------\n")

        # Insert tree structure text first
        self.text_edit.insertPlainText(tree_text + "\n\n")
        
        # Append file contents with relative path markers
        for rel_path, content in file_contents.items():
            self.text_edit.insertPlainText(f"<{rel_path}>\n{content}\n</{rel_path}>\n\n")

        # Added separator at the end
        self.text_edit.insertPlainText("-----------------------------\n")

        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox()
        self.copy_button = buttons.addButton("Copy to Clipboard", QDialogButtonBox.ActionRole)
        self.save_button = buttons.addButton("Save", QDialogButtonBox.ActionRole)
        self.close_button = buttons.addButton("Close", QDialogButtonBox.RejectRole)
        layout.addWidget(buttons)
        
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.save_button.clicked.connect(self.save_file)
        self.close_button.clicked.connect(self.close)
        
        self.setLayout(layout)
    
    def copy_to_clipboard(self):
        """Copy the exported text to clipboard."""
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        QMessageBox.information(self, "Copied", "Text copied to clipboard.")
    
    def save_file(self):
        """Save the exported file tree and file contents to a text file."""
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Exported File Tree", "exported_file_tree.txt", "Text Files (*.txt)")
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Success", f"Exported file tree saved to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save exported file tree:\n{e}")

class FileTreeApp(QWidget):
    """Main application window to display and export a file structure tree."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirXtract")
        self.setGeometry(100, 100, 900, 600)
        
        # Ensure CONFIG_DIR exists (for global ignore patterns only)
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        self.current_directory = ""
        self.global_ignores = self.load_global_ignores()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Directory selection row: folder selection, manual path, and settings
        dir_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select Folder")
        self.select_btn.clicked.connect(self.open_folder_dialog)
        dir_layout.addWidget(self.select_btn)

        self.dir_text = QLineEdit()
        self.dir_text.setPlaceholderText("Enter directory path here...")
        self.dir_text.returnPressed.connect(self.load_directory_from_text)
        dir_layout.addWidget(self.dir_text)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        dir_layout.addWidget(self.settings_btn)
        layout.addLayout(dir_layout)

        # Tree widget to show the file structure
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Select", "Name"])
        self.tree.setColumnWidth(1, 700)
        self.tree.itemExpanded.connect(self.on_item_expanded)
        layout.addWidget(self.tree)

        # Action buttons: view tree, reset, export
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("View File Tree")
        self.save_btn.clicked.connect(self.save_file_tree)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_tree)
        buttons_layout.addWidget(self.reset_btn)
        
        self.export_btn = QPushButton("Export File Contents to Text")
        self.export_btn.clicked.connect(self.export_file_contents)
        buttons_layout.addWidget(self.export_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_global_ignores(self):
        """Load global ignore patterns from JSON file or use default values."""
        ignore_path = get_global_ignore_path()
        if os.path.exists(ignore_path):
            try:
                with open(ignore_path, 'r', encoding='utf-8') as f:
                    ignores = json.load(f)
                return ignores if isinstance(ignores, list) else []
            except Exception:
                return []
        else:
            default_ignores = ['.DS_Store', '.git', '__pycache__', '*.tmp']
            self.save_global_ignores(default_ignores)
            return default_ignores

    def save_global_ignores(self, ignores):
        """Save global ignore patterns to JSON file."""
        ignore_path = get_global_ignore_path()
        try:
            with open(ignore_path, 'w', encoding='utf-8') as f:
                json.dump(ignores, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save global ignores:\n{e}")

    def open_settings_dialog(self):
        """Open the settings dialog to update global ignore patterns."""
        dialog = SettingsDialog(self.global_ignores, self)
        if dialog.exec_() == QDialog.Accepted:
            self.global_ignores = dialog.get_updated_ignores()
            self.save_global_ignores(self.global_ignores)
            if self.current_directory:
                self.load_directory(self.current_directory)
            QMessageBox.information(self, "Settings Saved", "Global ignore patterns have been updated.")

    def open_folder_dialog(self):
        """Open a folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            self.dir_text.setText(folder)
            self.load_directory(folder)

    def load_directory_from_text(self):
        """Load a directory from the manually entered path."""
        path = self.dir_text.text()
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            QMessageBox.warning(self, "Invalid Directory", "The directory path entered is invalid.")

    def load_directory(self, path):
        """Build the file tree from the selected directory.
        
        All items are initially checked. The tree is built on the fly without
        persisting any selection state to disk.
        """
        self.tree.blockSignals(True)
        self.tree.clear()
        self.current_directory = path
        
        # Determine a display name for the root node
        root_name = os.path.basename(path) if os.path.basename(path) else path
        root_item = QTreeWidgetItem(self.tree, ["", root_name])
        root_item.setData(0, Qt.UserRole, path)
        root_item.setFlags(root_item.flags() | Qt.ItemIsUserCheckable)
        root_item.setCheckState(0, Qt.Checked)
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        
        # Add immediate children for lazy loading
        self.add_children(root_item, path)
        self.tree.expandItem(root_item)
        self.tree.blockSignals(False)
        self.tree.itemChanged.connect(self.handle_item_changed)

    def is_ignored(self, name):
        """Check if a file/directory name matches any global ignore pattern."""
        return any(fnmatch.fnmatch(name, pattern) for pattern in self.global_ignores)

    def add_children(self, parent_item, parent_path):
        """Add child items (files and directories) to a given tree item."""
        try:
            for item_name in sorted(os.listdir(parent_path), key=lambda s: s.lower()):
                if self.is_ignored(item_name):
                    continue
                item_path = os.path.join(parent_path, item_name)
                child_item = QTreeWidgetItem(parent_item, ["", item_name])
                child_item.setData(0, Qt.UserRole, item_path)
                child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                child_item.setCheckState(0, Qt.Checked)
                if os.path.isdir(item_path):
                    child_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                    # Add a dummy child for lazy expansion
                    child_item.addChild(QTreeWidgetItem(child_item, ["", "Loading..."]))
        except PermissionError:
            pass  # Skip directories without permission
        except Exception as e:
            print(f"Error accessing {parent_path}: {e}")

    def on_item_expanded(self, item):
        """When an item is expanded, remove dummy child and load its real children."""
        if item.childCount() == 1 and item.child(0).text(1) == "Loading...":
            item.removeChild(item.child(0))
            self.add_children(item, item.data(0, Qt.UserRole))

    def handle_item_changed(self, item, column):
        """Propagate checkbox state changes to all descendant items."""
        if column == 0:
            self.tree.blockSignals(True)
            self.propagate_check_state(item, item.checkState(0))
            self.tree.blockSignals(False)

    def propagate_check_state(self, item, state):
        """Recursively set the check state for all children of an item."""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self.propagate_check_state(child, state)

    def collect_deselected(self, item):
        """
        Recursively collect the names of unchecked items.
        Returns a dictionary mapping parent directory paths to a list of deselected names.
        """
        deselected = {}
        path = item.data(0, Qt.UserRole)
        if not path or not isinstance(path, str):
            return deselected
        parent_path = os.path.dirname(path)
        if item.checkState(0) == Qt.Unchecked:
            deselected.setdefault(parent_path, []).append(os.path.basename(path))
        for i in range(item.childCount()):
            child = item.child(i)
            for k, v in self.collect_deselected(child).items():
                deselected.setdefault(k, []).extend(v)
        return deselected

    def traverse_and_format(self, path, prefix, is_last, lines, deselected):
        """
        Recursively traverse the filesystem to build a formatted tree structure.
        Excludes files/folders matching global ignore patterns and unchecked items.
        """
        name = os.path.basename(path) + "/" if os.path.isdir(path) else os.path.basename(path)
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")
        new_prefix = prefix + ("    " if is_last else "│   ")
        if os.path.isdir(path):
            try:
                items = sorted(os.listdir(path), key=lambda s: s.lower())
            except PermissionError:
                return
            # Filter items based on ignore patterns and current deselections
            items = [item for item in items if not self.is_ignored(item)]
            if path in deselected:
                items = [item for item in items if item not in deselected[path]]
            for i, item in enumerate(items):
                self.traverse_and_format(os.path.join(path, item), new_prefix, i == len(items) - 1, lines, deselected)

    def traverse_for_export(self, path, prefix="", is_last=True, relative_path="", deselected=None):
        """
        Recursively traverse to generate tree structure and collect file paths (for export).
        Returns a tuple of (formatted lines, dict mapping relative paths to full file paths).
        """
        if deselected is None:
            deselected = {}
        lines = []
        display_name = os.path.basename(path) + "/" if os.path.isdir(path) else os.path.basename(path)
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_name}")
        files_dict = {}
        if not os.path.isdir(path):
            files_dict[relative_path.replace(os.sep, "/")] = path
            return lines, files_dict

        new_prefix = prefix + ("    " if is_last else "│   ")
        try:
            items = sorted(os.listdir(path), key=lambda s: s.lower())
        except PermissionError:
            return lines, files_dict
        items = [item for item in items if not self.is_ignored(item)]
        if path in deselected:
            items = [item for item in items if item not in deselected[path]]
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            child_is_last = (i == len(items) - 1)
            new_rel = os.path.join(relative_path, item) if relative_path else item
            child_lines, child_files = self.traverse_for_export(item_path, new_prefix, child_is_last, new_rel, deselected)
            lines.extend(child_lines)
            files_dict.update(child_files)
        return lines, files_dict

    def save_file_tree(self):
        """Generate and display the file tree based on current selections."""
        if not self.current_directory or not os.path.isdir(self.current_directory):
            QMessageBox.warning(self, "Invalid Directory", "Please select a valid directory first.")
            return

        deselected = self.collect_deselected(self.tree.topLevelItem(0))
        lines = []
        self.traverse_and_format(self.current_directory, prefix="", is_last=True, lines=lines, deselected=deselected)
        if not lines:
            QMessageBox.information(self, "No Selection", "No files or directories selected.")
            return
        dialog = OutputDialog("\n".join(lines), self)
        dialog.exec_()

    def reset_tree(self):
        """Reload the current directory to reset any temporary selection changes."""
        if not self.current_directory:
            QMessageBox.warning(self, "No Directory", "Please select a directory first.")
            return
        self.load_directory(self.current_directory)
        QMessageBox.information(self, "Reset", "The tree has been reset.")

    def export_file_contents(self):
        """Export the file tree along with contents of selected files."""
        if not self.current_directory or not os.path.isdir(self.current_directory):
            QMessageBox.warning(self, "Invalid Directory", "Please select a valid directory first.")
            return

        deselected = self.collect_deselected(self.tree.topLevelItem(0))
        lines, files_dict = self.traverse_for_export(
            self.current_directory, prefix="", is_last=True,
            relative_path=os.path.basename(self.current_directory), deselected=deselected
        )
        if not lines:
            QMessageBox.information(self, "No Selection", "No files or directories selected.")
            return

        # Read file contents for each selected file
        file_contents = {}
        for rel_path, full_path in files_dict.items():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(full_path, 'r', encoding='latin1') as f:
                        content = f.read()
                except Exception as e:
                    content = f"Could not read file: {e}"
            except Exception as e:
                content = f"Could not read file: {e}"
            file_contents[rel_path] = content

        dialog = ExportOutputDialog("\n".join(lines), file_contents, self)
        dialog.exec_()

def main():
    """Entry point of the application."""
    app = QApplication(sys.argv)
    window = FileTreeApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
