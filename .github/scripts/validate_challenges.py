#!/usr/bin/env python3
"""
Validates all Challenge.yaml files in the repository.
Ensures they comply with the CTFChallenge CRD schema and security requirements.

Rules enforced:
  - apiVersion must be skyline.local/v1
  - kind must be CTFChallenge
  - metadata.name must be a valid RFC 1123 subdomain
  - metadata.name must match the parent folder name (lowercased)
  - metadata.namespace must be ctfd
  - spec.name, spec.description, spec.category, spec.points, spec.flag are always required
  - spec.flag must be SOPS-encrypted (starts with ENC[)
  - spec.image and spec.port are required ONLY when instance: true
  - spec.image must match ghcr.io/sp00kyskelet0n/skylinectf-challenges/<name>:latest
  - spec.port must be a valid port (1-65535)
  - spec.points must be a positive integer
  - sops section must be present (file must be encrypted)
"""
import os
import sys
import re
import yaml

# RFC 1123 subdomain regex
NAME_REGEX = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')

# Docker image pattern
IMAGE_REGEX = re.compile(r'^ghcr\.io/sp00kyskelet0n/skylinectf-challenges/[a-z0-9][-a-z0-9]*:.+$')




def validate_challenge(file_path):
    """Validate a single Challenge.yaml file. Returns a list of error strings."""
    errors = []

    # --- Parse YAML ---
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors

    if not data or not isinstance(data, dict):
        errors.append("Empty or invalid file")
        return errors

    # --- apiVersion ---
    if data.get('apiVersion') != 'skyline.local/v1':
        errors.append(f"apiVersion: expected 'skyline.local/v1', got '{data.get('apiVersion')}'")

    # --- kind ---
    if data.get('kind') != 'CTFChallenge':
        errors.append(f"kind: expected 'CTFChallenge', got '{data.get('kind')}'")

    # --- metadata ---
    metadata = data.get('metadata')
    if not metadata or not isinstance(metadata, dict):
        errors.append("Missing metadata section")
    else:
        name = metadata.get('name')
        if not name:
            errors.append("Missing metadata.name")
        elif not isinstance(name, str):
            errors.append(f"metadata.name must be a string, got {type(name).__name__}")
        elif not NAME_REGEX.match(name):
            errors.append(
                f"Invalid metadata.name '{name}': must be a lowercase RFC 1123 subdomain "
                f"(lowercase alphanumeric, '-' or '.', start/end with alphanumeric)"
            )

        # Folder name must match metadata.name (lowercased)
        folder_name = os.path.basename(os.path.dirname(file_path))
        if name and isinstance(name, str) and name != folder_name.lower():
            errors.append(
                f"metadata.name '{name}' does not match folder name '{folder_name}' (lowercased: '{folder_name.lower()}')"
            )

        if metadata.get('namespace') != 'ctfd':
            errors.append(f"metadata.namespace: expected 'ctfd', got '{metadata.get('namespace')}'")

    # --- spec ---
    spec = data.get('spec')
    if not spec or not isinstance(spec, dict):
        errors.append("Missing spec section")
    else:
        # Always-required fields
        for field in ['name', 'description', 'category', 'points', 'flag']:
            if field not in spec:
                errors.append(f"Missing required field: spec.{field}")

        # Points validation
        points = spec.get('points')
        if points is not None:
            if not isinstance(points, int) or points <= 0:
                errors.append(f"Invalid spec.points: must be a positive integer, got '{points}'")

        # Flag encryption check
        flag = spec.get('flag')
        if flag is not None:
            if not isinstance(flag, str):
                errors.append(f"spec.flag must be a string, got {type(flag).__name__}")
            elif not flag.startswith('ENC['):
                errors.append("spec.flag must be encrypted with SOPS (must start with 'ENC[...')")

        # Instance vs static challenge logic
        is_instance = spec.get('instance', False)
        has_uploads = spec.get('upload_files', False)


        # image and port are required ONLY for instance challenges
        if is_instance:
            if 'image' not in spec:
                errors.append("Missing spec.image (required when instance: true)")
            else:
                image = spec['image']
                if not isinstance(image, str) or not IMAGE_REGEX.match(image):
                    errors.append(
                        f"Invalid spec.image '{image}': must match "
                        f"'ghcr.io/sp00kyskelet0n/skylinectf-challenges/<name>:<tag>'"
                    )

            if 'port' not in spec:
                errors.append("Missing spec.port (required when instance: true)")
            else:
                port = spec['port']
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append(f"Invalid spec.port: must be 1-65535, got '{port}'")

    # --- SOPS encryption ---
    if 'sops' not in data:
        errors.append("Missing sops section: Challenge.yaml must be encrypted with SOPS")

    return errors


def main():
    has_errors = False
    root_dir = os.getcwd()
    challenge_files = []

    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and scripts
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'scripts']
        if 'Challenge.yaml' in files:
            challenge_files.append(os.path.join(root, 'Challenge.yaml'))

    if not challenge_files:
        print("No Challenge.yaml files found.")
        sys.exit(0)

    print(f"Found {len(challenge_files)} Challenge.yaml file(s).\n")

    for file_path in challenge_files:
        rel_path = os.path.relpath(file_path, root_dir)
        errors = validate_challenge(file_path)

        if errors:
            has_errors = True
            print(f"❌ {rel_path}:")
            for err in errors:
                print(f"   • {err}")
            print()
        else:
            print(f"✅ {rel_path}")

    if has_errors:
        print("\n❌ Validation failed. Fix the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All challenges are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
