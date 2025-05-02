#!/usr/bin/env python3
"""
T-34 vs Tiger Mission Builder CLI (Phase 1)

Clone an existing mission folder under $INSTALL/Missions, rename all occurrences
of the old mission name inside specified file types, and prepare for metadata entry.
"""
import os
import shutil
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="T-34 vs Tiger Mission Builder CLI"
    )
    parser.add_argument(
        "-i", "--install",
        required=True,
        help="Root path of your T-34 vs Tiger installation"
    )
    parser.add_argument(
        "-s", "--source",
        required=True,
        help="Relative path under Missions/ of the existing mission folder"
    )
    parser.add_argument(
        "-n", "--new",
        required=True,
        help="New mission folder name (no spaces, e.g., TestingMission)"
    )
    parser.add_argument(
        "-e", "--ext",
        nargs="+",
        default=[".script", ".rsr"],
        help="File extensions to process for renaming (default: .script .rsr)"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt (assume yes)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    install_root = args.install.rstrip("/\\")
    source_rel = args.source.strip("/\\")

    # Build full paths
    source_folder = os.path.join(install_root, "Missions", source_rel)
    if not os.path.isdir(source_folder):
        print(f"Error: Source mission folder not found: {source_folder}")
        exit(1)

    parent_folder = os.path.dirname(source_folder)
    new_folder = os.path.join(parent_folder, args.new)
    if os.path.exists(new_folder):
        print(f"Error: Target folder already exists: {new_folder}")
        exit(1)

    # Clone folder
    print(f"Cloning:\n  {source_folder}\n→ {new_folder}")
    shutil.copytree(source_folder, new_folder)

    old_prefix = os.path.basename(source_folder)
    new_prefix = args.new

    # Confirm
    if not args.yes:
        choice = input(f"Rename inside files: {old_prefix} → {new_prefix}? (y/N): ").lower()
        if choice != 'y':
            print("Aborted by user.")
            exit(0)

    # Rename inside files
    print()
    for root, dirs, files in os.walk(new_folder):
        for fname in files:
            for ext in args.ext:
                if fname.endswith(ext):
                    path = os.path.join(root, fname)
                    with open(path, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                    updated = text.replace(old_prefix, new_prefix)
                    if updated != text:
                        with open(path, 'w', encoding='utf-8', errors='replace') as f:
                            f.write(updated)
                        print(f"Renamed occurrences in {fname}")
                    break

    print("\nPhase 1 complete: folder cloned and scripts renamed.")
    print("Next: run Phase 2 to gather metadata and patch menu files.")


if __name__ == '__main__':
    main()
