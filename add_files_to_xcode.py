#!/usr/bin/env python3
import re
import uuid

# Генерируем уникальные UUID для новых файлов
def generate_uuid():
    return ''.join(str(uuid.uuid4()).replace('-', '').upper()[:24])

# Файлы для добавления
files_to_add = [
    {
        'path': 'lara/kexploit/pe/amfi.m',
        'type': 'sourcecode.c.objc',
        'name': 'amfi.m'
    },
    {
        'path': 'lara/kexploit/pe/amfi.h',
        'type': 'sourcecode.c.h',
        'name': 'amfi.h'
    },
    {
        'path': 'lara/kexploit/pe/installd_patch.m',
        'type': 'sourcecode.c.objc',
        'name': 'installd_patch.m'
    },
    {
        'path': 'lara/kexploit/pe/installd_patch.h',
        'type': 'sourcecode.c.h',
        'name': 'installd_patch.h'
    },
    {
        'path': 'lara/views/TrollStoreInstallerView.swift',
        'type': 'sourcecode.swift',
        'name': 'TrollStoreInstallerView.swift'
    }
]

# Читаем project.pbxproj
with open('lara.xcodeproj/project.pbxproj', 'r') as f:
    content = f.read()

# Генерируем UUID для каждого файла
file_refs = {}
build_files = {}
for file_info in files_to_add:
    file_refs[file_info['name']] = generate_uuid()
    build_files[file_info['name']] = generate_uuid()

print("Генерируем UUID для файлов...")
for name, uuid_val in file_refs.items():
    print(f"  {name}: {uuid_val}")

# Находим секцию PBXFileReference
file_ref_section = re.search(r'(/\* Begin PBXFileReference section \*/.*?/\* End PBXFileReference section \*/)', content, re.DOTALL)
if not file_ref_section:
    print("❌ Не найдена секция PBXFileReference")
    exit(1)

# Добавляем PBXFileReference для каждого файла
new_file_refs = []
for file_info in files_to_add:
    uuid_val = file_refs[file_info['name']]
    ref = f"\t\t{uuid_val} /* {file_info['path']} */ = {{isa = PBXFileReference; lastKnownFileType = {file_info['type']}; path = {file_info['path']}; sourceTree = \"<group>\"; }};"
    new_file_refs.append(ref)

# Вставляем перед концом секции
insert_pos = file_ref_section.end() - len('/* End PBXFileReference section */')
new_refs_text = '\n'.join(new_file_refs) + '\n\t\t'
content = content[:insert_pos] + new_refs_text + content[insert_pos:]

print("✅ Добавлены PBXFileReference")

# Находим секцию PBXBuildFile
build_file_section = re.search(r'(/\* Begin PBXBuildFile section \*/.*?/\* End PBXBuildFile section \*/)', content, re.DOTALL)
if not build_file_section:
    print("❌ Не найдена секция PBXBuildFile")
    exit(1)

# Добавляем PBXBuildFile только для .m и .swift файлов
new_build_files = []
for file_info in files_to_add:
    if file_info['type'] in ['sourcecode.c.objc', 'sourcecode.swift']:
        build_uuid = build_files[file_info['name']]
        file_uuid = file_refs[file_info['name']]
        build = f"\t\t{build_uuid} /* {file_info['name']} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_uuid} /* {file_info['path']} */; }};"
        new_build_files.append(build)

# Вставляем перед концом секции
insert_pos = build_file_section.end() - len('/* End PBXBuildFile section */')
new_builds_text = '\n'.join(new_build_files) + '\n\t\t'
content = content[:insert_pos] + new_builds_text + content[insert_pos:]

print("✅ Добавлены PBXBuildFile")

# Находим секцию PBXSourcesBuildPhase
sources_section = re.search(r'(/\* Begin PBXSourcesBuildPhase section \*/.*?files = \()(.*?)(\);)', content, re.DOTALL)
if not sources_section:
    print("❌ Не найдена секция PBXSourcesBuildPhase")
    exit(1)

# Добавляем файлы в Sources
new_sources = []
for file_info in files_to_add:
    if file_info['type'] in ['sourcecode.c.objc', 'sourcecode.swift']:
        build_uuid = build_files[file_info['name']]
        source = f"\t\t\t\t{build_uuid} /* {file_info['name']} in Sources */,"
        new_sources.append(source)

# Вставляем в список files
insert_pos = sources_section.end(2)
new_sources_text = '\n' + '\n'.join(new_sources)
content = content[:insert_pos] + new_sources_text + content[insert_pos:]

print("✅ Добавлены в PBXSourcesBuildPhase")

# Сохраняем
with open('lara.xcodeproj/project.pbxproj', 'w') as f:
    f.write(content)

print("\n✅ Файлы успешно добавлены в project.pbxproj!")
print("\nТеперь выполни:")
print("  git add lara.xcodeproj/project.pbxproj")
print("  git commit -m 'Add TrollStore files to Xcode project'")
print("  git push origin main")

