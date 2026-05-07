#!/bin/bash
# Add new source files to Xcode project

PROJECT_FILE="lara.xcodeproj/project.pbxproj"

echo "Adding new files to Xcode project..."

# Files to add
FILES=(
    "lara/kexploit/pe/csflags_patch.h"
    "lara/kexploit/pe/csflags_patch.m"
    "lara/kexploit/pe/entitlement_inject.h"
    "lara/kexploit/pe/entitlement_inject.m"
    "lara/kexploit/pe/amfi_userclient.h"
    "lara/kexploit/pe/amfi_userclient.m"
)

# Check if files exist in project
for file in "${FILES[@]}"; do
    filename=$(basename "$file")
    if grep -q "$filename" "$PROJECT_FILE"; then
        echo "✓ $filename already in project"
    else
        echo "⚠️ $filename NOT in project - needs manual add"
    fi
done

echo ""
echo "To add files manually:"
echo "1. Open lara.xcodeproj in Xcode"
echo "2. Right-click on kexploit/pe folder"
echo "3. Add Files to 'lara'..."
echo "4. Select: csflags_patch.h/m, entitlement_inject.h/m, amfi_userclient.h/m"
echo "5. Commit and push"
