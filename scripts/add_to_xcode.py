#!/usr/bin/env python3
"""
Add source files to Xcode project programmatically
"""

import sys
import uuid
import re

def generate_uuid():
    """Generate 24-character hex UUID for Xcode"""
    return uuid.uuid4().hex[:24].upper()

def add_files_to_project(project_path, files):
    """Add files to Xcode project.pbxproj"""

    with open(project_path, 'r') as f:
        content = f.read()

    # Generate UUIDs for each file
    file_refs = {}
    build_files = {}

    for filepath in files:
        filename = filepath.split('/')[-1]
        file_refs[filepath] = generate_uuid()
        build_files[filepath] = generate_uuid()
        print(f"Generated UUIDs for {filename}")

    # Find PBXBuildFile section
    build_file_section = re.search(r'/\* Begin PBXBuildFile section \*/(.*?)/\* End PBXBuildFile section \*/', content, re.DOTALL)
    if not build_file_section:
        print("ERROR: Could not find PBXBuildFile section")
        return False

    # Find PBXFileReference section
    file_ref_section = re.search(r'/\* Begin PBXFileReference section \*/(.*?)/\* End PBXFileReference section \*/', content, re.DOTALL)
    if not file_ref_section:
        print("ERROR: Could not find PBXFileReference section")
        return False

    # Find PBXSourcesBuildPhase section
    sources_section = re.search(r'/\* Begin PBXSourcesBuildPhase section \*/(.*?)/\* End PBXSourcesBuildPhase section \*/', content, re.DOTALL)
    if not sources_section:
        print("ERROR: Could not find PBXSourcesBuildPhase section")
        return False

    # Add PBXBuildFile entries
    build_file_entries = []
    for filepath, build_uuid in build_files.items():
        filename = filepath.split('/')[-1]
        file_uuid = file_refs[filepath]
        entry = f"\t\t{build_uuid} /* {filename} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_uuid} /* {filename} */; }};\n"
        build_file_entries.append(entry)

    # Add PBXFileReference entries
    file_ref_entries = []
    for filepath, file_uuid in file_refs.items():
        filename = filepath.split('/')[-1]
        filetype = "sourcecode.c.h" if filename.endswith('.h') else "sourcecode.c.objc"
        entry = f"\t\t{file_uuid} /* {filename} */ = {{isa = PBXFileReference; lastKnownFileType = {filetype}; path = {filename}; sourceTree = \"<group>\"; }};\n"
        file_ref_entries.append(entry)

    # Insert entries
    build_file_insert_pos = build_file_section.end() - len('/\* End PBXBuildFile section \*/')
    content = content[:build_file_insert_pos] + ''.join(build_file_entries) + content[build_file_insert_pos:]

    file_ref_insert_pos = file_ref_section.end() - len('/\* End PBXFileReference section \*/')
    content = content[:file_ref_insert_pos] + ''.join(file_ref_entries) + content[file_ref_insert_pos:]

    # Add to sources build phase
    sources_files_match = re.search(r'(files = \()(.*?)(\);)', sources_section.group(1), re.DOTALL)
    if sources_files_match:
        sources_entries = []
        for filepath, build_uuid in build_files.items():
            filename = filepath.split('/')[-1]
            if filename.endswith('.m'):  # Only add .m files to build phase
                entry = f"\t\t\t\t{build_uuid} /* {filename} in Sources */,\n"
                sources_entries.append(entry)

        # Find the position to insert
        sources_insert_pos = sources_files_match.end(2)
        # Adjust position in full content
        full_sources_start = content.find(sources_section.group(1))
        relative_pos = sources_insert_pos - len(sources_section.group(1)[:sources_files_match.start(2)])
        insert_pos = full_sources_start + sources_files_match.start(2) + len(sources_files_match.group(2))

        content = content[:insert_pos] + ''.join(sources_entries) + content[insert_pos:]

    # Write back
    with open(project_path, 'w') as f:
        f.write(content)

    print(f"\n✓ Added {len(files)} files to Xcode project")
    return True

if __name__ == '__main__':
    project_path = 'lara.xcodeproj/project.pbxproj'

    files = [
        'lara/kexploit/pe/csflags_patch.h',
        'lara/kexploit/pe/csflags_patch.m',
        'lara/kexploit/pe/entitlement_inject.h',
        'lara/kexploit/pe/entitlement_inject.m',
        'lara/kexploit/pe/amfi_userclient.h',
        'lara/kexploit/pe/amfi_userclient.m',
    ]

    print("Adding files to Xcode project...")
    print("=" * 50)

    if add_files_to_project(project_path, files):
        print("\n✓ Success! Files added to project.")
        print("\nNext steps:")
        print("1. git add lara.xcodeproj/project.pbxproj")
        print("2. git commit -m 'Add new source files to Xcode project'")
        print("3. git push")
    else:
        print("\n✗ Failed to add files")
        sys.exit(1)
