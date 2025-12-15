#!/usr/bin/env python3
"""
Pre-flight validation script for Loom addon.

Validates the addon structure before loading into Blender.
"""

import os
import sys
import ast
from pathlib import Path
from collections import defaultdict

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print section header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ{RESET} {text}")


class AddonValidator:
    """Validates Loom addon structure."""

    def __init__(self, addon_path):
        self.addon_path = Path(addon_path)
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)

    def validate(self):
        """Run all validations."""
        print_header("LOOM ADDON STRUCTURE VALIDATION")

        self.check_directory_structure()
        self.check_python_syntax()
        self.check_imports()
        self.check_class_definitions()
        self.check_registration()
        self.check_bl_info()
        self.print_summary()

        return len(self.errors) == 0

    def check_directory_structure(self):
        """Validate directory structure."""
        print_header("1. Directory Structure")

        expected_dirs = [
            'helpers',
            'properties',
            'ui',
            'operators',
            'presets',
            'handlers'
        ]

        for dirname in expected_dirs:
            dir_path = self.addon_path / dirname
            if dir_path.exists() and dir_path.is_dir():
                print_success(f"Directory exists: {dirname}/")
                self.stats['directories'] += 1
            else:
                print_error(f"Missing directory: {dirname}/")
                self.errors.append(f"Missing directory: {dirname}")

    def check_python_syntax(self):
        """Check Python syntax for all .py files."""
        print_header("2. Python Syntax Validation")

        py_files = list(self.addon_path.rglob("*.py"))
        print_info(f"Found {len(py_files)} Python files")

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    ast.parse(code)
                print_success(f"Valid syntax: {py_file.relative_to(self.addon_path)}")
                self.stats['valid_files'] += 1
            except SyntaxError as e:
                print_error(f"Syntax error in {py_file.relative_to(self.addon_path)}: {e}")
                self.errors.append(f"Syntax error: {py_file.name}")

    def check_imports(self):
        """Check import statements."""
        print_header("3. Import Structure")

        py_files = list(self.addon_path.rglob("*.py"))
        bpy_imports = 0
        relative_imports = 0

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == 'bpy':
                                bpy_imports += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('.'):
                            relative_imports += 1

            except Exception as e:
                print_warning(f"Could not analyze imports in {py_file.name}: {e}")

        print_success(f"Found {bpy_imports} bpy imports")
        print_success(f"Found {relative_imports} relative imports")
        self.stats['bpy_imports'] = bpy_imports
        self.stats['relative_imports'] = relative_imports

    def check_class_definitions(self):
        """Check for Blender class definitions."""
        print_header("4. Class Definitions")

        py_files = list(self.addon_path.rglob("*.py"))
        class_types = defaultdict(int)

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        name = node.name
                        if name.startswith('LOOM_PG_'):
                            class_types['PropertyGroups'] += 1
                        elif name.startswith('LOOM_UL_'):
                            class_types['UILists'] += 1
                        elif name.startswith('LOOM_OT_'):
                            class_types['Operators'] += 1
                        elif name.startswith('LOOM_MT_'):
                            class_types['Menus'] += 1
                        elif name.startswith('LOOM_PT_'):
                            class_types['Panels'] += 1
                        elif name.startswith('LOOM_AP_'):
                            class_types['AddonPrefs'] += 1

            except Exception as e:
                print_warning(f"Could not analyze classes in {py_file.name}: {e}")

        for class_type, count in sorted(class_types.items()):
            print_success(f"{class_type}: {count} classes")
            self.stats[f'class_{class_type}'] = count

        total_classes = sum(class_types.values())
        self.stats['total_classes'] = total_classes
        print_info(f"Total Blender classes: {total_classes}")

    def check_registration(self):
        """Check registration functions."""
        print_header("5. Registration Functions")

        # Check main __init__.py
        main_init = self.addon_path / '__init__.py'
        if not main_init.exists():
            print_error("Main __init__.py not found")
            self.errors.append("Missing main __init__.py")
            return

        with open(main_init, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        has_register = False
        has_unregister = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'register':
                    has_register = True
                    print_success("Found register() function")
                elif node.name == 'unregister':
                    has_unregister = True
                    print_success("Found unregister() function")

        if not has_register:
            print_error("Missing register() function")
            self.errors.append("Missing register()")
        if not has_unregister:
            print_error("Missing unregister() function")
            self.errors.append("Missing unregister()")

        # Check for module imports
        has_imports = all(mod in content for mod in ['properties', 'ui', 'operators', 'presets', 'handlers'])
        if has_imports:
            print_success("All modules imported")
        else:
            print_warning("Some modules may not be imported")

    def check_bl_info(self):
        """Check bl_info."""
        print_header("6. bl_info Validation")

        bl_info_file = self.addon_path / 'bl_info.py'
        if not bl_info_file.exists():
            print_error("bl_info.py not found")
            self.errors.append("Missing bl_info.py")
            return

        with open(bl_info_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_keys = ['name', 'author', 'version', 'blender', 'location', 'description', 'category']

        for key in required_keys:
            if f'"{key}"' in content or f"'{key}'" in content:
                print_success(f"bl_info has '{key}' key")
            else:
                print_warning(f"bl_info missing '{key}' key")
                self.warnings.append(f"Missing bl_info key: {key}")

        # Check Blender version
        if '(5, 0, 0)' in content:
            print_success("Blender version set to 5.0.0")
        else:
            print_warning("Blender version may not be set correctly")

    def print_summary(self):
        """Print validation summary."""
        print_header("VALIDATION SUMMARY")

        # Statistics
        print(f"{BOLD}Statistics:{RESET}")
        print(f"  Python files: {self.stats['valid_files']}")
        print(f"  Total classes: {self.stats['total_classes']}")
        print(f"  Property Groups: {self.stats.get('class_PropertyGroups', 0)}")
        print(f"  Operators: {self.stats.get('class_Operators', 0)}")
        print(f"  UI Components: {self.stats.get('class_UILists', 0) + self.stats.get('class_Menus', 0) + self.stats.get('class_Panels', 0)}")
        print(f"  bpy imports: {self.stats['bpy_imports']}")
        print(f"  Relative imports: {self.stats['relative_imports']}")

        print()

        # Errors
        if self.errors:
            print(f"{BOLD}{RED}Errors ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"  {RED}✗{RESET} {error}")
        else:
            print(f"{BOLD}{GREEN}No errors found!{RESET}")

        print()

        # Warnings
        if self.warnings:
            print(f"{BOLD}{YELLOW}Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {warning}")
        else:
            print(f"{BOLD}{GREEN}No warnings!{RESET}")

        print()

        # Final result
        if len(self.errors) == 0:
            print(f"{BOLD}{GREEN}{'='*70}{RESET}")
            print(f"{BOLD}{GREEN}✓ VALIDATION PASSED - Ready for Blender testing!{RESET:^70}")
            print(f"{BOLD}{GREEN}{'='*70}{RESET}\n")
        else:
            print(f"{BOLD}{RED}{'='*70}{RESET}")
            print(f"{BOLD}{RED}✗ VALIDATION FAILED - Please fix errors before testing{RESET:^70}")
            print(f"{BOLD}{RED}{'='*70}{RESET}\n")


def main():
    """Main entry point."""
    addon_path = Path(__file__).parent / 'loom'

    if not addon_path.exists():
        print_error(f"Addon directory not found: {addon_path}")
        sys.exit(1)

    validator = AddonValidator(addon_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
